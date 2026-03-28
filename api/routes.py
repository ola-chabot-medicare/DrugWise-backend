"""API router for chatbot endpoints."""

from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, StandardResponse
from utils.logger import logger

router = APIRouter(prefix="/api")


@router.post("/chat", response_model=StandardResponse, tags=["Chatbot"])
async def chat_bot(request: ChatRequest) -> StandardResponse:
    """Temporary chat endpoint that echoes the incoming message."""
    try:
        reply_text = f"Received: {request.message}"
        return StandardResponse(status="success", data={"reply": reply_text})
    except Exception as exc:
        logger.error(f"Error in asking chatbot: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
