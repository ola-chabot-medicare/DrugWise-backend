# DrugWise Implementation Plan

This document tracks both the foundational MVP infrastructure setup from day 1, as well as the advanced Backend integration of RAG and LLM services. 

## Phase 1: Project MVP
*Complete steps to initialize the core scaffolding, directories, and environments.*

| Step | Component | Status | Sub-steps |
| :--- | :--- | :---: | :--- |
| **1** | **Git & GitHub Initialization**<br>`git clone` | ✅ Done | 1. Fork `DrugWise-backend` repository from organization<br>2. Clone repository locally to `/Downloads/backend`<br>3. Set up the [main](file:///Users/nguyenanloc/Downloads/backend/scripts/import_data.py#254-287) branch as the stable working tree<br>4. Create [.gitignore](file:///Users/nguyenanloc/backend/.gitignore) to prevent committing secrets/environments |
| **2** | **Python Environment Setup**<br>`venv` | ✅ Done | 1. Create a virtual environment using `python3 -m venv venv`<br>2. Activate the environment via `source venv/bin/activate`<br>3. Install required libraries (`pip install fastapi uvicorn openai chromadb pydantic python-dotenv`)<br>4. Freeze dependencies into [requirements.txt](file:///Users/nguyenanloc/backend/requirements.txt) |
| **3** | **Project Folder Architecture**<br>*Directories* | ✅ Done | 1. Create `/api` for FastAPI endpoints<br>2. Create `/config` for environment & database configurations<br>3. Create `/models` for Pydantic data validation schemas<br>4. Create `/services` for core LLM and RAG business logic<br>5. Create `/scripts` for standalone data ingestion scripts |
| **4** | **Environment Variables**<br>`.env` | ✅ Done | 1. Create local `.env` file (ignored by Git)<br>2. Securely store `OPENAI_API_KEY`<br>3. Securely store `CHROMA_API_KEY`, `CHROMA_TENANT`, and `CHROMA_DATABASE`<br>4. Build `config/settings.py` to load `.env` variables via Pydantic BaseSettings |
| **5** | **Core API Foundation**<br>`main.py` | ✅ Done | 1. Initialize `app = FastAPI()` instance<br>2. Configure CORS middleware to accept frontend requests (`allow_origins=["*"]`)<br>3. Set up FastAPI lifespan events for database connection health checks<br>4. Build a basic `/health` check endpoint returning 200 OK |
| **6** | **ChromaDB Cloud Setup**<br>`config/chroma.py` | ✅ Done | 1. Log in to Chroma cloud dashboard & create `medicare-chatbot` database<br>2. Initialize `chromadb.HttpClient` with correct headers inside Python<br>3. Create `get_collection()` function to fetch the `medical_collection`<br>4. Implement `test_chroma_connection()` to ping the db on server startup |

---

## Phase 2: Backend
*ChromaDB Cloud + RAG pipeline + LLM generation + FastAPI routes.*

| Step | Component | Status | Sub-steps |
| :--- | :--- | :---: | :--- |
| **1** | **Data Preparation & Ingestion**<br>`scripts/import_data.py` | ✅ Done | 1. Parse FDA `drug-label.json` and `drug-ndc.json`<br>2. Format documents and clean metadata<br>3. Fix missing metadata constraints for NDCs (`label_id`, `effective_time`)<br>4. Connect to ChromaDB Cloud securely<br>5. Upload 30,000 document chunks in batches to prevent timeouts |
| **2** | **LLM Generation Service**<br>`services/llm.py` | ✅ Done | 1. Initialize global OpenAI Client<br>2. Define strict medical `SYSTEM_PROMPT` to prevent hallucinations and enforce FDA data usage<br>3. Program `generate_answer()` using the retrieved context<br>4. Add robust `try/except` for safe OpenAI failure handling<br>5. Fix configuration for reasoning models (removing unsupported parameters) |
| **3** | **RAG Retrieval Engine**<br>`services/rag.py` | ✅ Done | 1. Initialize ChromaDB instance connection<br>2. Build `retrieve_context()` function to search vector embeddings<br>3. Extract and loop through top 5 document matches<br>4. Format unstructured matches into a numbered context list<br>5. Add `try/except` fallback to return empty string on database failure |
| **4** | **FastAPI routes**<br>`api/routes.py` | ✅ Done | 1. Set up `APIRouter()` prefixed with `/api`<br>2. Create `POST /api/chat` endpoint using asynchronous execution<br>3. Wire frontend `ChatRequest` validation to the RAG service<br>4. Pass RAG output and user input into the LLM service<br>5. Wrap output in a clean `StandardResponse` JSON format |
| **5** | **End-to-End Server Testing**<br>`main.py` | ✅ Done | 1. Spin up the backend via `uvicorn main:app --reload`<br>2. Ensure ChromaDB connects properly on server lifespan event<br>3. Navigate to auto-generated OpenAPI Swagger UI at `http://localhost:8000/docs`<br>4. Submit test payload via browser to test RAG + LLM execution<br>5. Verify backend logs and successful 200 OK JSON response |
| **6** | **Git Version Control**<br>*GitHub Workflow* | ✅ Done | 1. Review modified files via `git status`<br>2. Stage backend files via `git add .`<br>3. Create commit message documenting RAG and API implementation<br>4. Push local `feat/llm-service` feature branch to remote GitHub repository<br>5. Open Pull Request on GitHub to merge into `main` |
