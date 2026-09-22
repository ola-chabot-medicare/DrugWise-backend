# DrugWise Backend

The FastAPI service behind [DrugWise](https://github.com/ola-chabot-medicare/DrugWise-frontend),
a medical drug-information chatbot. Runs a Retrieval-Augmented Generation
(RAG) pipeline over real FDA drug label and NDC data so answers are grounded
in that data instead of the model guessing from general training knowledge.

## Why this exists

I built DrugWise to practice a full RAG pipeline end to end: chunking real
FDA data, embedding and querying it from a hosted vector store, and wiring
that retrieval into an LLM call behind a FastAPI service a separate frontend
actually talks to — not a notebook demo.

## Key features

- **RAG pipeline**: FDA drug label and NDC records are chunked, embedded
  (`text-embedding-3-small`), and stored in ChromaDB Cloud. Every question
  triggers a top-K similarity search before the LLM ever sees it
  (`services/rag.py`).
- **Grounded generation**: `gpt-4o-mini` answers using the retrieved FDA
  context plus a system prompt that enforces medical disclaimers and tells
  the model to clearly label anything it's supplementing from general
  knowledge (`services/llm.py`).
- **Duplicate-question caching**: exact repeat questions are served from an
  in-memory cache instead of re-calling OpenAI.
- **Auto-generated API docs**: FastAPI's Swagger UI at `/docs` for testing
  `/api/chat` directly, no separate client needed.
- **Startup health check**: the app pings ChromaDB Cloud on startup and
  exposes `/health` so the frontend can detect an unreachable backend.

## Tech stack

Verified from `requirements.txt`.

- FastAPI + Uvicorn
- ChromaDB Cloud (vector database)
- OpenAI API — `gpt-4o-mini` for generation, `text-embedding-3-small` for
  embeddings
- LangChain / `langchain-openai`
- Pydantic for config and request/response schemas

## Setup

### 1. Clone and install

```bash
git clone https://github.com/ola-chabot-medicare/DrugWise-backend.git
cd DrugWise-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp example.env .env
```

Edit `.env` and fill in:
- `OPENAI_API_KEY` — required
- `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE` — from a
  [ChromaDB Cloud](https://www.trychroma.com/) account (free tier works);
  the client connects to Chroma Cloud only, there's no local/offline mode

### 3. Ingest FDA data (needed for real, grounded answers)

The `data/` directory (openFDA `drug-label.json` and `drug-ndc.json`) isn't
shipped in this repo — download your own extract from
[api.fda.gov](https://open.fda.gov/apis/drug/), drop the two files in
`backend/data/`, then run:

```bash
python3 scripts/import_data.py
```

This embeds and upserts the records into your ChromaDB Cloud collection.
Without this step the chatbot still runs, but `retrieve_context()` has
nothing to retrieve, so every answer falls back to the model's general
knowledge instead of FDA-sourced data.

### 4. Run the server

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI, or POST
directly to `/api/chat`:

```json
{ "message": "What are the side effects of ibuprofen?", "model": "gpt-4o-mini", "model_provider": "openai" }
```
