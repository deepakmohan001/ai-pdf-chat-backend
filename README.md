# DocuMind AI – Backend

An AI-powered PDF Chat Application that allows users to upload PDF documents, extract their content, and ask questions about the documents using Retrieval-Augmented Generation (RAG).

The backend is built with FastAPI and integrates MongoDB, Sentence Transformers, and Ollama to process documents and generate context-based answers.

## Technologies Used


### Backend
- Python
- FastAPI
- PyMongo
- MongoDB Atlas
- Uvicorn

### AI and Machine Learning
- Sentence Transformers
- Embeddings
- Retrieval-Augmented Generation (RAG)
- Ollama
- Llama 3.2 1B

### PDF Processing
- PyPDF
- Text extraction
- Text chunking

## Features

- Upload PDF documents.
- Extract text from PDF files.
- Split extracted text into smaller chunks.
- Generate embeddings using Sentence Transformers.
- Retrieve relevant document content based on user questions.
- Generate answers using Ollama (Llama 3.2 1B).
- Store document information and chat history in MongoDB.
- View and delete uploaded documents.
- View and clear chat history.

## Project Structure

```text
ai-pdf-chat-backend/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   └── services/
│       ├── chunking.py
│       ├── embedding.py
│       └── ollama_service.py
│
├── uploads/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Backend Setup

### 1. Clone the Repository

```bash
git clone https://github.com/deepakmohan001/ai-pdf-chat-backend.git
```

### 2. Navigate to the Project Directory

```bash
cd ai-pdf-chat-backend
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```powershell
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure the following variables:

```env
MONGODB_URL=your_mongodb_connection_string
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Replace the MongoDB placeholder with your own MongoDB Atlas connection string.

Never commit your actual `.env` file or database credentials to GitHub.

### 6. Install and Run Ollama

Install Ollama from:

https://ollama.com/

Download the required model:

```bash
ollama pull llama3.2:1b
```

Make sure Ollama is running before using the AI question-answering functionality.

### 7. Run the Backend

```bash
uvicorn main:app --reload
```

The backend will run at:

http://127.0.0.1:8000

## API Documentation

FastAPI automatically generates interactive API documentation.

After starting the backend, visit:

http://127.0.0.1:8000/docs

## Project Repositories

- **Backend:** https://github.com/deepakmohan001/ai-pdf-chat-backend
- **Frontend:** https://github.com/deepakmohan001/ai-pdf-chat-frontend

## Project Status

- Backend development completed.
- PDF upload and text extraction implemented.
- Embedding generation and RAG-based question answering implemented.
- Ollama integration completed.
- Tested locally with PDF documents.

**Deployment:** Not yet deployed. 
