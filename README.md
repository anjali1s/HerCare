# Women's Health RAG Chatbot — Full Pipeline

## What was wrong with your original notebook

Your `dat_ing.ipynb` only did steps 1–2 of a RAG pipeline:
- ✅ Load PDFs (PyMuPDFLoader)
- ✅ Chunk them (RecursiveCharacterTextSplitter)
- ❌ No DOCX support at all
- ❌ No embeddings step
- ❌ No vector database
- ❌ No LLM connection anywhere in the file

So if your app is failing with an "API key" error, that's happening in some
other script you have, not this notebook. The most common reasons that
happens with this stack:

1. `.env` file exists but `load_dotenv()` was never called before creating
   the LLM client — the SDK just sees `None` and fails silently or throws
   an auth error.
2. Variable name mismatch — e.g. you set `OPENAI_KEY` in `.env` but the
   library is looking for `OPENAI_API_KEY` (or `GROQ_API_KEY`, `GOOGLE_API_KEY`,
   etc. — every provider uses a different exact name).
3. `.env` is in a different folder than where you're running the script from
   (dotenv only auto-finds it in the current working directory / its parents).
4. Key created in one terminal session, but Jupyter/your script was started
   from a different terminal before the key was exported — restart the
   kernel after adding the key.
5. Using a paid-only model name with a free-tier key.

`rag_chatbot.py` below fails loudly with the exact fix if the key is missing,
instead of silently breaking.

## The new pipeline

```
data/                      <- put your .pdf and .docx source files here
ingestion_pipeline.py      <- loads, chunks, embeds, stores everything
rag_chatbot.py             <- retrieves + asks the LLM + answers you
requirements.txt
.env.example
```

**Stack chosen and why:**
| Piece | Choice | Why |
|---|---|---|
| PDF parsing | `PyMuPDFLoader` | same as your original code, kept it |
| DOCX parsing | `Docx2txtLoader` | simplest reliable Word loader in LangChain |
| Chunking | `RecursiveCharacterTextSplitter` | same as your original code |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local) | **completely free, no API key, no rate limit** — runs on your own CPU |
| Vector DB | `Chroma` | free, local, persists to disk, zero setup |
| LLM | **Groq** (`llama-3.3-70b-versatile`) | free API tier, very fast, good quality for Q&A — good fit for a health chatbot that needs quick, accurate responses |

## Requirements

Python 3.9–3.12 (tested on 3.12). Works on Mac, Linux, and Windows.

## One-command setup

**Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:** double-click `setup.bat` (or run it from a terminal).

This creates a virtual environment, installs everything in `requirements.txt`,
and creates a `.env` file from the template for you.

Then:
1. Open `.env` and paste in a free Groq key from https://console.groq.com/keys
2. Put your PDF/DOCX source files into the `data/` folder.

## Run it

Activate the virtual environment first (the setup script tells you the exact
command for your OS), then:

```bash
# Step 1: build the vector database (run once, or whenever you add new docs)
python ingestion_pipeline.py

# Step 2: chat with your documents
python rag_chatbot.py
```

`ingestion_pipeline.py` defaults to reading from `./data` and writing to
`./chroma_db` — pass `--data_dir` / `--persist_dir` if you want different
locations.

## Manual setup (if you don't want to use the scripts)

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then edit .env with your real key
```

## Notes on safety for a health chatbot

The system prompt in `rag_chatbot.py` is deliberately constrained:
- It only answers from retrieved context, and says so when it doesn't know.
- It never states a diagnosis.
- It nudges the user toward a real clinician for anything symptom/medication/
  lab-result specific.

You should treat this as a starting point, not a finished medical product —
if this is going to real users, get the disclaimers and scope reviewed
properly before launch.

## Extending it

- Add more file types by writing another `load_xxx()` function in
  `ingestion_pipeline.py` following the same pattern as `load_pdf`/`load_docx`.
- To swap the LLM (e.g. to Google Gemini's free tier instead of Groq), you'd
  only need to change the `ChatGroq(...)` block in `rag_chatbot.py` to the
  equivalent `ChatGoogleGenerativeAI(...)` from `langchain-google-genai`.
