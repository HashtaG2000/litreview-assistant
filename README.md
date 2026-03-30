# 🗺️ LitMap — AI-Powered Literature Review Assistant

LitMap is a Streamlit web app that helps researchers build **structured, validated literature reviews** using AI. Upload your root paper, validate candidate papers with LLM reasoning, and get a full literature review drafted automatically.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📖 **Research Context Understanding** | After uploading your root paper, LitMap summarises what it understood — key themes, research gap, and acceptance criteria |
| 🔍 **AI Paper Validation** | Each candidate paper is analysed against your research idea using a local embedding search + Groq LLaMA 3.3 70B |
| 💬 **Reasoning & Override** | LitMap explains *why* it accepted or rejected each paper — you have full authority to override the decision |
| ✍️ **Auto Literature Review** | Accepted papers are synthesised into a structured academic literature review |
| ⬇️ **Word Export** | Download the final review as a `.docx` file |
| 🐳 **Docker Support** | Run the whole app in a container with one command |

---

## 🖥️ App Flow

```
1. Welcome      →  Enter research idea + upload root paper
2. Understand   →  LitMap shows what it understood from your idea & paper
3. Validate     →  Upload candidate papers one by one, review AI reasoning, accept/reject
4. Review       →  Full literature review generated and ready to download
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A [Groq API key](https://console.groq.com/) (free tier available)

### 1. Clone the repo

```bash
git clone https://github.com/HashtaG2000/litreview-assistant.git
cd litreview-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🐳 Run with Docker

```bash
docker-compose up --build
```

The app will be available at `http://localhost:8501`

---

## 📁 Project Structure

```
litreview-assistant/
│
├── app.py               # Main Streamlit application (all 4 screens)
├── ingestor.py          # PDF loading, chunking, and ChromaDB storage
├── retriever.py         # Semantic search and LLM relevance checking
├── llm.py               # Groq LLaMA model setup
│
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose config
└── .gitignore
```

---

## 🧠 How It Works

```
Root Paper (PDF)
      │
      ▼
 PyPDFLoader → RecursiveCharacterTextSplitter → HuggingFace Embeddings
      │
      ▼
  ChromaDB (local vector store)
      │
      ▼
Candidate Paper uploaded
      │
      ├── Candidate chunks extracted (first 5 as sample)
      │
      └── Groq LLaMA 3.3 70B
            ├── Verdict: RELEVANT / NOT RELEVANT
            └── Reason: one-sentence explanation
                  │
                  └── User confirms or overrides
                              │
                        If Accepted → chunks stored to ChromaDB
                              │
                        Final Step → similarity search over all accepted chunks
                              │
                        Groq LLaMA generates full literature review
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io/) |
| LLM | [Groq](https://groq.com/) — LLaMA 3.3 70B Versatile |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector Store | [ChromaDB](https://www.trychroma.com/) |
| PDF Parsing | LangChain `PyPDFLoader` |
| Chunking | LangChain `RecursiveCharacterTextSplitter` |
| DOCX Export | `python-docx` |

---

## ⚙️ Configuration

You can adjust these constants in the source files:

| File | Constant | Default | Description |
|---|---|---|---|
| `ingestor.py` | `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `ingestor.py` | `chunk_size` | `500` | Characters per chunk |
| `ingestor.py` | `chunk_overlap` | `50` | Overlap between chunks |
| `llm.py` | `model` | `llama-3.3-70b-versatile` | Groq model |
| `llm.py` | `temperature` | `0.3` | LLM temperature |

---

## 📝 Notes

- The `chroma_store/` folder is created locally on first run — it persists your embeddings between sessions
- Your `.env` file is never committed to Git (it's in `.gitignore`)
- For best results, write a specific 2–3 sentence research idea on the Welcome screen

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
