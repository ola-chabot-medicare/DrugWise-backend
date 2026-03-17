"""
Stub router with /api prefix. All future chat endpoints will be registered here
"""

from fastapi import APIRouter
from models.schemas import (
    StandardResponse,
    ChatRequest
)
from utils.logger import logger
router = APIRouter(prefix="/api")  # All routes here will be prefixed with /api

# API endpoints will be added here in the next steps

@router.post("/chat", response_model=StandardResponse , tags=["Chatbot"])
async def chat_bot(request: ChatRequest):
    try:
        
    except Exception as e:
        logger.error(f"Error in asking chatbot: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )