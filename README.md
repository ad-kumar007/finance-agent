# 💼 Multi-Agent Finance Assistant

> A voice-enabled, modular finance assistant that generates daily market briefings using **LLMs**, **RAG**, and **voice pipelines**.

---

## 📌 Use Case

> **"What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?"**

- Fetches real-time company data (Yahoo Finance / EDGAR filings)
- Answers in both **text** and **voice**
- Uses RAG (Retrieval-Augmented Generation) for factual accuracy
- Built with FastAPI + React + LangChain + Whisper + TTS

---

## 🚀 Quick Start

### 1. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables

```bash
# Create .env file with your API key
echo "OPENROUTER_API_KEY=your-key-here" > .env
```

### 3. Start Backend Server

```bash
uvicorn orchestrator.main:app --port 8001 --reload
```

### 4. Start React Frontend (Recommended)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## 🎨 Frontend Options

### React Frontend (Recommended) ✅

Modern React + Vite + TypeScript + Tailwind CSS frontend.

```bash
cd frontend
npm install
npm run dev
```

**Features:**
- Text input for questions
- Voice recording with MediaRecorder API
- Audio file upload (WAV, MP3, M4A)
- Response playback
- Raw JSON toggle
- Loading indicators

### Streamlit Frontend (Deprecated) ⚠️

> **Note:** The Streamlit frontend is deprecated. Please use the React frontend instead.

```bash
streamlit run streamlit_app/app.py
```

---

## 🔧 Architecture

### 🧠 Agent Roles

| Agent       | Role                                                  |
|-------------|-------------------------------------------------------|
| API Agent   | Fetches market data from Yahoo Finance                |
| Analytics   | Technical analysis (RSI, Moving Averages, Beta)       |
| Scraper     | Extracts earnings from filings (EDGAR)                |
| Retriever   | Uses FAISS & SentenceTransformer for RAG              |
| Language    | Uses OpenRouter LLM to synthesize a response          |
| Voice       | Whisper (STT) & TTS for voice interface               |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/ask_llm` | Text question (JSON: `{question}`) |
| POST | `/ask_audio` | Audio question (multipart form) |
| GET | `/audio/{filename}` | Get audio response file |

---

## 📁 Project Structure

```
finance-agent/
├── agents/                    # AI Agents
│   ├── analytics_agent.py     # Technical analysis
│   ├── language_agent.py      # LLM integration
│   ├── retriever_agent.py     # RAG with FAISS
│   └── voice_agent.py         # Voice processing
├── data_ingestion/            # Data sources
│   ├── api_agent.py           # Yahoo Finance API
│   └── scraper_agent.py       # News scraping
├── orchestrator/              # API backend
│   ├── main.py                # FastAPI app
│   ├── voice_agent.py         # Whisper + TTS
│   └── fallback_handler.py    # Error handling
├── frontend/                  # React frontend ✅
│   ├── src/
│   │   ├── api/               # API client
│   │   ├── components/        # React components
│   │   └── pages/             # Page components
│   └── package.json
├── streamlit_app/             # Streamlit frontend (deprecated)
├── tests/                     # Unit tests
└── docs/                      # Documentation
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🐳 Docker

```bash
docker-compose up --build
```

---

## 📝 License

MIT
