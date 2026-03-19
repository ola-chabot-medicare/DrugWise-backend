# DrugWise — Implementation Plan

## Project Overview
An AI-powered medical chatbot that answers drug-related questions using FDA-approved data,
built with a Retrieval-Augmented Generation (RAG) architecture.

```
User question → FastAPI → RAG (ChromaDB search) → LLM (OpenAI GPT) → Answer
```

---

## Progress Tracker

| Step | File | Status |
|------|------|--------|
| 1 | Get FDA data ([drug-label.json](file:///Users/nguyenanloc/backend/data/drug-label.json), [drug-ndc.json](file:///Users/nguyenanloc/backend/data/drug-ndc.json)) | ✅ Done |
| 2 | Build ingestion script ([scripts/import_data.py](file:///Users/nguyenanloc/backend/scripts/import_data.py)) | ✅ Done |
| 3 | Fix JSON corruption in [drug-ndc.json](file:///Users/nguyenanloc/backend/data/drug-ndc.json) | ✅ Done |
| 4 | Run ingestion — 30,000 docs in ChromaDB Cloud | ✅ Done |
| 5 | Fix NDC metadata (`label_id`, `effective_time`) | ✅ Done |
| 6 | Git commit + push → PR → merge `feat/ingest-fda-data` | ✅ Done |
| 7 | Build LLM service ([services/llm.py](file:///Users/nguyenanloc/backend/services/llm.py)) | 🔄 In progress |
| 8 | Build RAG pipeline ([services/rag.py](file:///Users/nguyenanloc/backend/services/rag.py)) | 🔴 Next |
| 9 | Build chat API ([api/routes.py](file:///Users/nguyenanloc/backend/api/routes.py)) | 🔴 Todo |
| 10 | Test end-to-end | 🔴 Todo |
| 11 | Build frontend UI | 🔴 Todo |

---

## Step 7 — [services/llm.py](file:///Users/nguyenanloc/backend/services/llm.py) (LLM Service)

**Branch:** `feat/llm-service`

### What it does
Takes a user question + FDA context retrieved from ChromaDB → calls OpenAI GPT → returns an answer.

### Structure (4 blocks)

**Block 1 — Imports**
```python
from openai import OpenAI
from config.settings import settings
from utils.logger import logger
```

**Block 2 — Client + System Prompt**
```python
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a helpful medical information assistant.
IMPORTANT GUIDELINES:
- Provide accurate information based on the FDA drug data provided in the context
- Always include appropriate medical disclaimers
- If information is not in the provided context, supplement with your general medical
  knowledge but clearly indicate it is not from FDA data
- Never provide medical advice or diagnose conditions
- Reference FDA data sources when possible
- Be clear about drug information, side effects
- If uncertain about any information, recommend professional medical consultation

RESPONSE FORMAT:
- Start with a direct answer to the question
- Provide relevant details from the FDA data
- Include important warnings if applicable"""
```

**Block 3 — Function signature + user prompt**
```python
def generate_answer(question: str, context: str, model: str = "gpt-4o-mini") -> str:
    user_prompt = f"""Based on the following FDA drug information, answer the question.
If the FDA context is insufficient, supplement with your general medical knowledge
and clearly label it as such.

FDA Context:
{context}

Question: {question}

Answer:"""
```

**Block 4 — OpenAI call with try/except**
```python
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        answer = response.choices[0].message.content.strip()
        logger.info(f"LLM response | model={model} | tokens={response.usage.total_tokens}")
        return answer
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return "Sorry, I was unable to generate an answer. Please try again."
```

> [!NOTE]
> `gpt-4o-mini` — cheap (~$0.001/query), fast, accurate enough for FAQ-style medical Q&A.
> `temperature=0.3` — keeps answers factual, reduces hallucination.

---

## Step 8 — [services/rag.py](file:///Users/nguyenanloc/backend/services/rag.py) (RAG Pipeline)

**Branch:** `feat/llm-service` (same branch, same PR)

### What it does
Takes a user question → searches ChromaDB Cloud for top relevant FDA documents → formats them into a context string → returns context to [llm.py](file:///Users/nguyenanloc/backend/services/llm.py).

### Structure (3 blocks)

**Block 1 — Imports**
```python
from config.chroma import get_collection
from utils.logger import logger
```

**Block 2 — Retrieve function**
```python
def retrieve_context(question: str, n_results: int = 5) -> str:
    """Search ChromaDB for the most relevant FDA docs for the given question."""
```

**Block 3 — Query ChromaDB + format context**
```python
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[question],
            n_results=n_results,
            include=["documents", "metadatas"]
        )
        # Format top results into a readable context string
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        context_parts = []
        for i, (doc, meta) in enumerate(zip(docs, metas), start=1):
            brand = meta.get("brand_name", "Unknown")
            generic = meta.get("generic_name", "Unknown")
            context_parts.append(f"[{i}] {brand} ({generic}):\n{doc[:600]}")
        context = "\n\n".join(context_parts)
        logger.info(f"Retrieved {len(docs)} documents for query: {question[:50]}")
        return context
    except Exception as e:
        logger.error(f"ChromaDB query failed: {e}")
        return ""   # Return empty — LLM will fall back to its own knowledge
```

---

## Step 9 — [api/routes.py](file:///Users/nguyenanloc/backend/api/routes.py) (Chat Endpoint)

**Branch:** `feat/llm-service` (same branch, same PR)

### What it does
Exposes `POST /api/chat` that wires rag → llm → returns answer to the frontend.

### Structure
```python
from fastapi import APIRouter
from models.schemas import ChatRequest, StandardResponse
from services.rag import retrieve_context
from services.llm import generate_answer

router = APIRouter(prefix="/api")

@router.post("/chat", tags=["Chat"])
async def chat(request: ChatRequest) -> StandardResponse:
    try:
        context = retrieve_context(request.message)
        answer = generate_answer(
            question=request.message,
            context=context,
            model=request.model,
        )
        return StandardResponse(status="success", data={"answer": answer})
    except Exception as e:
        return StandardResponse(status="error", message=str(e))
```

---

## Step 10 — Test End-to-End

```bash
uvicorn main:app --reload
```

Then test via Swagger UI at `http://localhost:8000/docs`:
```json
POST /api/chat
{
  "model_provider": "openai",
  "message": "What are the side effects of ibuprofen?",
  "model": "gpt-4o-mini"
}
```

Expected response:
```json
{
  "status": "success",
  "data": {
    "answer": "Based on FDA data, ibuprofen may cause..."
  }
}
```

---

## Git Workflow

```
feat/llm-service branch:
  ├── services/llm.py     ← LLM service
  ├── services/rag.py     ← RAG pipeline
  └── api/routes.py       ← Chat endpoint
       ↓
  git push origin feat/llm-service
       ↓
  PR → merge to main
```