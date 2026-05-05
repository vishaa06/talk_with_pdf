# 📚 Talk With PDF: RAG-Based Autonomous Agent

A functional Retrieval-Augmented Generation (RAG) pipeline that allows users to upload PDFs and have grounded conversations with their data.

## 🛠️ Tech Stack
- **LLM Orchestration:** Inngest (Background task management)
- **Vector Database:** Qdrant (Local semantic storage)
- **Frontend:** Streamlit
- **Embeddings:** HuggingFace / OpenAI
- **Language:** Python (Managed with `uv`)

## 🚀 Features
- **Smart Ingestion:** Automatically chunks PDFs with context-preserving overlap.
- **Semantic Search:** Uses vector embeddings to find exact answers, not just keyword matches.
- **Async Processing:** Uses an event-driven architecture to handle heavy PDF processing without freezing the UI.

## 📦 Installation & Setup
1. **Clone the repo:**
   git clone [https://github.com/vishaa06/talk_with_pdf.git]

Install dependencies:
uv sync

Run the App:
streamlit run streamlit_app.py

## 🧠 How it Works
1. **Upload:** User provides a PDF.
2. **Ingest:** The system breaks text into 1000-character chunks with a 200-character overlap to maintain context.
3. **Vectorize:** Chunks are converted into vectors and stored in Qdrant.
4. **Query:** When a question is asked, the system retrieves the top 3 most relevant chunks to generate a response.

## 🔑 Environment Variables
Create a `.env` file in the root directory and add your keys:
OPENAI_API_KEY=your_key_here
QDRANT_URL=http://localhost:6333

Prerequisites
Python 3.12+, uv, and a running instance of Qdrant

