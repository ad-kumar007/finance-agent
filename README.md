# 💼 Multi-Agent Finance Assistant

> A voice-enabled, modular finance assistant that generates daily market briefings using **LLMs**, **RAG**, and **voice pipelines**.

---

## 📌 Use Case

> **“What’s our risk exposure in Asia tech stocks today, and highlight any earnings surprises?”**

- Fetches real-time company data (Yahoo Finance / EDGAR filings)
- Answers in both **text** and **voice**
- Uses RAG (Retrieval-Augmented Generation) for factual accuracy
- Built with FastAPI + Streamlit + LangChain + Whisper + Coqui TTS

---

## 🔧 Architecture

### 🧠 Agent Roles

| Agent       | Role                                                  |
|-------------|-------------------------------------------------------|
| API Agent   | Fetches market data from Yahoo Finance                |
| Scraper     | Extracts earnings from filings (EDGAR)                |
| Retriever   | Uses FAISS & SentenceTransformer for RAG              |
| Language    | Uses OpenRouter LLM to synthesize a response          |
| Voice       | Whisper (STT) & Coqui TTS (TTS) for voice interface   |

---

### 🔄 Orchestration Flow

