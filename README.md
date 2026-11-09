# 🤖 Abir's Autonomous Career Agent (AI Digital Twin)

An enterprise-ready **Local-First Retrieval-Augmented Generation (RAG)** interactive portfolio platform. This project acts as an AI "Digital Twin" capable of answering complex inquiries regarding my engineering background, technical specialities, and project history without data egress or API costs.

---

## 💡 Architectural Architecture Strategy

Rather than leveraging third-party cloud APIs (like OpenAI), this ecosystem runs entirely locally to demonstrate high-level competency in resource-constrained AI engineering.

* **Inference Engine:** `Llama 3.2 (3B)` running locally via `Ollama`. Chosen for its low consumer-hardware footprint balanced with strong context-retention performance.
* **Vector Database:** `ChromaDB` (Persistent Native Storage) handling semantic search indexing.
* **Orchestration Layer:** `LangChain` for strategic document parsing, and dynamic text chunking (`chunk_size=350`, `chunk_overlap=50`) designed to maintain structural programming blocks and technical key phrases.
* **UI Interface:** An interactive reactive `Streamlit` dashboard implementing a secure conversational state loop.

---

## 🛠️ Step-by-Step Local Deployment Installation

### 1. Prerequisites

Ensure you have Python 3.10+ installed and the Ollama server runtime running on your desktop.

### 2. Download and Initialize the Local LLM

Open your terminal/command prompt and spin up the target model:

```bash
ollama pull llama3.2
```

### 3. Setup Project Space

Navigate to the designated project environment:

```bash
cd C:\AKD\workplace\Abir-Personal-Agent
```

### 4. Install Component Stack

```bash
pip install -r requirements.txt
```

### 5. Build Knowledge Base

Populate `career_history.txt` with raw technical experiences, certifications, projects, and structural text summaries.

### 6. Execute Application Launch

```bash
streamlit run app.py
```

---

## 🧠 Governance & Safety Architecture

* **Zero-Hallucination Guardrails:** The core agent is bound to a strict deterministic prompt framework. If a query falls outside the semantic bounds indexed inside ChromaDB, the agent gracefully defaults rather than fabricating career milestones.
* **Privacy By Design:** 100% of data parsing, embedding generation, vector matching, and model generation occur within the local machine perimeter—ideal for enterprise compliance evaluation scenarios.

===> Run looks like
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/ade30c8a-d408-45c3-a11d-77ec001a54f3" />

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/0ee1d45a-07e4-4670-8e7a-935055ebd468" />


