"""
API Endpoints - connect FastAPI to RAG & LLM services
Hanlde incoming HTTP requests from frontend and connect them to RAG & LLM services
"""

from fastapi import APIRouter
from models.schemas import ChatRequest, StandardResponse  # noqa: F401
from services.rag import retrieve_context  # noqa: F401
from services.llm import generate_answer  # noqa: F401
from utils.logger import logger  # noqa: F401

# Create a FastAPI router with prefix "/api"
router = APIRouter(prefix="/api")  # All routes here will be prefixed with /api


# The @router.post decorator means this function handles POST requests to /api/chat
# tags = ["Chat"] groups this nicely in Swagger UI
@router.post("/chat", tags = ["Chat"])
async def chat(request: ChatRequest) -> StandardResponse:
    # request: ChatRequest auto ensure incoming JSON match our rules
    # async def allows the endpoint wait for background (like ChromaDB or OpenAI) without freezing the entire FastAPI server.
    logger.info(f"Incoming chat request: {request.message}")   # higher version of print()

    """ Wiring RAG and LLM together with try/except """
    try:
        # Step 1: Retrieve context from ChromaDB
        context = retrieve_context(question = request.message)

        # Step 2: Pass the message + retrieved context to LLM
        answer = generate_answer(
            question = request.message,
            context = context,
            model = request.model
        )
    
        # Step 3: Return a successful JSON response
        return StandardResponse(
            status = "success",
            data = {"answer": answer}
        )

    except Exception as e:
        # Catch any errors and return a friendly error
        logger.error(f"Chat endpoint failed: {e}")
        return StandardResponse(
            status = "error",
            message = str(e)
        )

