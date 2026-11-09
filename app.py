import streamlit as st
import os
import chromadb
import pypdf
import docx2txt

# Define data paths
DATA_DIR = "./career_history"

# Initialize ChromaDB (Persistent local storage)
@st.cache_resource
def get_vector_db():
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="abir_career_twin")
    return collection

collection = get_vector_db()

def extract_text_from_file(file_path):
    """Native file parsing that avoids compiled binary policy blocks"""
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif ext == ".pdf":
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif ext == ".docx":
            text = docx2txt.process(file_path)
    except Exception as e:
        st.sidebar.warning(f"Could not parse {os.path.basename(file_path)}: {e}")
        
    return text

def native_word_splitter(text, chunk_size=500, chunk_overlap=150):
    """Pure-Python word chunker to isolate information slices"""
    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        # Slice words based on dynamic boundaries
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += (chunk_size - chunk_overlap)
        
    return chunks

def initialize_knowledge_base():
    if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
        st.sidebar.error(f"Please ensure the directory '{DATA_DIR}' exists and contains files!")
        return False
    
    all_chunks = []
    
    # Iterate files in the target directory natively
    for file_name in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file_name)
        if os.path.isfile(file_path):
            file_text = extract_text_from_file(file_path)
            if file_text.strip():
                # Process the word split rules manually
                file_chunks = native_word_splitter(file_text, chunk_size=500, chunk_overlap=150)
                all_chunks.extend(file_chunks)

    if not all_chunks:
        st.sidebar.error("No valid text could be processed from documents.")
        return False
        
    # Clear old vectors to avoid data pollution
    existing_ids = collection.get()['ids']
    if existing_ids:
        collection.delete(ids=existing_ids)
        
    # Sync straight into Chroma database
    for i, chunk in enumerate(all_chunks):
        collection.add(
            documents=[chunk],
            ids=[f"chunk_{i}"]
        )
    return True

def run_ui():
    st.set_page_config(page_title="Abir's AI Digital Twin", page_icon="🤖", layout="centered")
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    st.title("🤖 Abir's AI Digital Twin")
    st.subheader("Chat with an AI agent grounded in Abir's career, skills, and projects.")
    st.write("This interface queries a local **Llama 3.2 (3B)** model via **Ollama**, using **ChromaDB** for RAG.")

    if st.sidebar.button("🔄 Sync/Refresh Career Data"):
        with st.sidebar.spinner("Processing directory natively..."):
            if initialize_knowledge_base():
                st.sidebar.success("Knowledge base successfully synced!")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am Abir's AI Twin. Ask me anything about his technical stack, past experiences, or engineering projects!"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if user_query := st.chat_input("Ask about Abir..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Retrieving facts and thinking..."):
                try:
                    import ollama
                    search_results = collection.query(query_texts=[user_query], n_results=3)
                    context = " ".join(search_results['documents'][0]) if search_results['documents'] else ""
                    
                    system_prompt = (
                        "You are the professional AI Digital Twin of Abir. Your task is to accurately answer questions "
                        "about his career, expertise, tech stack, and background based ONLY on the validated context block below.\n"
                        "Rules:\n"
                        "1. Keep answers concise, factual, and written in a highly professional tone.\n"
                        "2. If the answer is not present in the context, say exactly: 'Abir hasn't updated my matrix with those specific details yet, but you can connect with him directly to discuss this!' Do not make things up.\n\n"
                        f"Validated Context:\n{context}"
                    )
                    
                    response = ollama.chat(
                        model='llama3.2',
                        messages=[
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': user_query}
                        ]
                    )
                    
                    answer = response['message']['content']
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"Error communicating with local Ollama service: {e}")

if __name__ == "__main__":
    run_ui()
