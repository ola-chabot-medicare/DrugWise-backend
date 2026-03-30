# DrugWise Backend

The powerful Python backend running the intelligence behind the DrugWise medical chatbot. 

It uses a custom **Retrieval-Augmented Generation (RAG)** pipeline to instantly search through FDA drug documents and feed them to an AI model. This ensures the chatbot answers medical questions using real, verified medical data rather than hallucinating from scratch.

## ✨ Features

- 🧠 **RAG Architecture**: Takes user questions, vectorizes them, and searches a database full of FDA drug labels in milliseconds.
- ⚡ **Lightning Fast Caching**: Automatically remembers previous medical questions. If a user asks a duplicate question, the server intercepts it and returns the answer instantly (0.01s) without wasting API budget.
- 📖 **Automatic API Docs**: Built on FastAPI, which automatically generates an interactive Swagger UI dashboard for developers to test endpoints.
- 🛡️ **Budget Protected**: Requires local environment variables so your personal OpenAI API keys are never leaked to the public.

## 🛠 Tech Stack

- **FastAPI** 🚀 (For a blazing fast, asynchronous Python server)
- **ChromaDB** 🗄️ (For storing and searching high-dimensional FDA vector data)
- **OpenAI API** 🤖 (Powered by `gpt-4o-mini` for fast medical reasoning)

## 🚀 How to run locally

If you want to run the backend engine yourself, follow these steps:

1. **Clone the code**:
   ```bash
   git clone https://github.com/ola-chabot-medicare/DrugWise-backend.git
   cd DrugWise-backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup your secret keys**:
   Create a new file called `.env` in the root folder and add your OpenAI key. This prevents your budget from being used by mistake:
   ```env
   OPENAI_API_KEY=sk-your-secret-key
   ```

5. **Start the server**:
   ```bash
   uvicorn main:app --reload
   ```

6. **Test the API**:
   Open your browser to `http://localhost:8000/docs` to see the auto-generated Swagger UI and test the `/api/chat` endpoint directly!
