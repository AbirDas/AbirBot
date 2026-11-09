import streamlit as st
import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
import ollama

# Configure Streamlit page layout
st.set_page_config(page_title="Abir's AI Digital Twin", page_icon="🤖", layout="centered")

# Define data paths
DATA_PATH = "career_history.txt"

# 1. Initialize ChromaDB (Persistent local storage)
@st.cache_resource
def get_vector_db():
    # Uses a local directory inside your project folder to persist the database
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="abir_career_twin")
    return collection

collection = get_vector_db()

# 2. Index / Update Knowledge Base
def initialize_knowledge_base():
    if not os.path.exists(DATA_PATH):
        st.error(f"Please create the '{DATA_PATH}' file with your career details first!")
        return False
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Chunk text to preserve semantic context within Llama 3.2's window
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=50)
    chunks = text_splitter.split_text(text)
    
    # Clear existing vectors to prevent duplicates on rerun
    existing_ids = collection.get()['ids']
    if existing_ids:
        collection.delete(ids=existing_ids)
        
    # Inject chunks into ChromaDB
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"chunk_{i}"]
        )
    return True

# Simple UI Button to initialize/refresh data
if st.sidebar.button("🔄 Sync/Refresh Career Data"):
    if initialize_knowledge_base():
        st.sidebar.success("Knowledge base successfully synced!")

# 3. Streamlit Frontend UI Layout
st.title("🤖 Abir's AI Digital Twin")
st.subheader("Chat with an AI agent grounded in Abir's career, skills, and projects.")
st.write("This interface queries a local **Llama 3.2 (3B)** model via **Ollama**, using **ChromaDB** for Retrieval-Augmented Generation (RAG) to ensure zero hallucinations.")

# Initialize chat session history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am Abir's AI Twin. Ask me anything about his technical stack, past experiences, or engineering projects!"}]

# Display chat logs
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User prompt interface
if user_query := st.chat_input("Ask about Abir (e.g., 'What is his experience with Agentic AI?')"):
    # Append user question to UI
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)
        
    # Generate RAG response
    with st.chat_message("assistant"):
        with st.spinner("Retrieving facts and thinking..."):
            try:
                # Semantic search query to ChromaDB
                search_results = collection.query(query_texts=[user_query], n_results=3)
                context = " ".join(search_results['documents'][0]) if search_results['documents'] else ""
                
                # Strict instruction framing to prevent LLM hallucinations
                system_prompt = (
                    "You are the professional AI Digital Twin of Abir. Your task is to accurately answer questions "
                    "about his career, expertise, tech stack, and background based ONLY on the validated context block below.\n"
                    "Rules:\n"
                    "1. Keep answers concise, factual, and written in a highly professional tone.\n"
                    "2. If the answer is not present in the context, say exactly: 'Abir hasn't updated my matrix with those specific details yet, but you can connect with him directly to discuss this!' Do not make things up.\n\n"
                    f"Validated Context:\n{context}"
                )
                
                # Inference via local Ollama
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
