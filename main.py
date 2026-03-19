""" FastAPI app entry point.
Tests ChromaDB on startup via lifespan,
adds CORS for frontend,
and exposes a /health endpoint.
"""

import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from config.chroma import test_chroma_connection
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once on startup and once on shutdown."""
    logger.info("DrugWise starting up...")
    # Test ChromaDB connection before accepting any requests
    if test_chroma_connection():
        logger.info(" ChromaDB is ready.")
    else:
        logger.warning("ChromaDB connection failed. Check your .env credentials.")
    yield  # App is live and serving requests here
    logger.info(" Shutting down.")


app = FastAPI(
    title="DrugWise - Medical Chatbot API",
    description="RAG-based medical chatbot powered by FDA data, ChromaDB, FastAPI & LangChain.",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow the frontend to call this API during local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Quick endpoint to verify the app and ChromaDB are running."""
    return {
        "status": "ok",
        "chroma_connected": test_chroma_connection(),
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
