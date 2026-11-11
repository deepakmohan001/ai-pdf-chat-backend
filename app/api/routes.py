from fastapi import APIRouter
from pydantic import BaseModel
from app.database.connection import documents_collection

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str


@router.get("/")
def home():
    return {
        "message": "Welcome to AI PDF Chat Application"
    }
    
    
@router.post("/ask")
def ask_question(data: QuestionRequest):
    return {
        "message": "Your question was received",
        "question": data.question
    }    
    
    
@router.post("/documents")
def create_document():
    document = {
        "filename": "python_notes.pdf",
        "file_type": "application/pdf"
    }

    result = documents_collection.insert_one(document)

    return {
        "message": "Document saved successfully",
        "document_id": str(result.inserted_id)
    }    
    
 
@router.get("/documents")
def get_documents():
    documents = list(documents_collection.find())

    for document in documents:
        document["_id"] = str(document["_id"])

    return documents    
    