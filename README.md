# DrugWise Backend

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F61?style=for-the-badge&logo=databricks&logoColor=white)

A FastAPI-based backend service for a medical chatbot application. It leverages **ChromaDB Cloud** for Retrieval-Augmented Generation (RAG) using FDA-approved drug data, and uses **OpenAI** (gpt-4o-mini) to generate accurate, heavily-guarded medical responses.

---

## Tech Stack

| Technology | Description |
|------------|-------------|
| **Python** | Core programming language |
| **FastAPI** | Modern, high-performance web framework for the API |
| **ChromaDB Cloud** | Vector database for efficient semantic search of FDA documents |
| **OpenAI API** | Large Language Model used to generate conversational context |
| **Uvicorn** | ASGI server for running the FastAPI application |

---

## Project Structure

```
backend/
├── api/                      # API layer
│   └── routes.py             # Defines the POST /api/chat endpoint
├── config/                   # Configuration
│   ├── settings.py           # Pydantic BaseSettings for .env variables
│   └── chroma.py             # ChromaDB Cloud connection initialization
├── models/                   # Data models
│   └── schemas.py            # Pydantic schemas (ChatRequest, StandardResponse)
├── scripts/                  # Standalone utilities
│   └── import_data.py        # Ingests FDA JSON data into ChromaDB
├── services/                 # Business logic
│   ├── llm.py                # Connects to OpenAI with medical SYSTEM_PROMPT
│   └── rag.py                # Retrieves Top-K documents from ChromaDB
├── utils/                    # Utility functions
│   └── logger.py             # Custom logging
├── .env                      # Environment variables (ignored by git)
├── main.py                   # FastAPI application entry point
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

---

## Installation & Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Mac/Linux
   # venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key

   # ChromaDB Cloud Configuration
   CHROMA_API_KEY=your_chroma_api_key
   CHROMA_TENANT=your_tenant_name
   CHROMA_DATABASE=medicare-chatbot
   ```

5. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

---

## API Documentation

Once the server is running, FastAPI automatically generates interactive documentation:

* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (tests ChromaDB connection) |
| `POST` | `/api/chat` | Main endpoint. Accepts `{ "message": "query" }` and returns the RAG LLM answer |

---

## FDA Data Ingestion

To populate your ChromaDB Cloud with the latest FDA data, place the `drug-label.json` and `drug-ndc.json` files in your directory (or ensure paths match) and run:

```bash
python3 scripts/import_data.py
```
This script automatically batches records, inserts metadata, creates embeddings, and upserts them into vector storage.
