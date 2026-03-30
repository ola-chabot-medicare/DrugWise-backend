# DrugWise Backend — Claude Code Guide

## Project Overview
FastAPI RAG-based medical chatbot. Uses ChromaDB Cloud for vector search over FDA drug data
and OpenAI gpt-4o-mini for response generation.

## Tech Stack
- Python 3.10+
- FastAPI + Uvicorn
- ChromaDB Cloud (vector DB)
- OpenAI API (LLM)
- Pydantic for config and schemas

## Project Structure
- api/routes.py        → POST /api/chat endpoint
- config/settings.py   → Pydantic BaseSettings (.env loader)
- config/chroma.py     → ChromaDB connection
- services/llm.py      → OpenAI integration + SYSTEM_PROMPT
- services/rag.py      → Top-K retrieval from ChromaDB
- models/schemas.py    → ChatRequest, StandardResponse schemas
- scripts/import_data.py → FDA data ingestion into ChromaDB
- utils/logger.py      → Custom logging

## Dev Commands
- Run server: uvicorn main:app --reload
- Ingest data: python3 scripts/import_data.py
- Install deps: pip install -r requirements.txt

## Environment Variables (see example.env)
- OPENAI_API_KEY
- CHROMA_API_KEY
- CHROMA_TENANT
- CHROMA_DATABASE=medicare-chatbot

## Important Rules
- Never hardcode API keys
- Medical responses must stay heavily-guarded (see SYSTEM_PROMPT in services/llm.py)
- Always use the StandardResponse schema for API responses
- RAG retrieval happens before every LLM call — don't bypass it
```