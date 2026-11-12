from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from app.database.connection import documents_collection
import shutil
from pypdf import PdfReader
from bson import ObjectId
from app.services.chunking import split_text_into_chunks
from app.services.embedding import generate_embedding

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
    
    
@router.put("/documents")
def update_document():
    result = documents_collection.update_one(
        {"filename": "python_notes.pdf"},
        {"$set": {"filename": "django_notes.pdf"}}
    )

    return {
        "message": "Document updated successfully",
        "modified_count": result.modified_count
    }
    
@router.delete("/documents")
def delete_document():
    result = documents_collection.delete_one(
        {"filename": "django_notes.pdf"}
    )

    return {
        "message": "Document deleted successfully",
        "deleted_count": result.deleted_count
    }        
    
    
@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = {
        "filename": file.filename,
        "file_path": file_path,
        "file_type": file.content_type
    }

    result = documents_collection.insert_one(document)

    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "document_id": str(result.inserted_id)
    }
    




@router.get("/extract-text/{document_id}")
def extract_pdf_text(document_id: str):

    # Validate MongoDB document ID
    if not ObjectId.is_valid(document_id):
        return {"error": "Invalid document ID"}

    # Find document in MongoDB
    document = documents_collection.find_one(
        {"_id": ObjectId(document_id)}
    )

    if not document:
        return {"error": "Document not found"}

    # Read PDF file
    reader = PdfReader(document["file_path"])

    extracted_text = ""

    # Extract text from all PDF pages
    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text += text + "\n"

    # Split extracted text into chunks
    chunks = split_text_into_chunks(extracted_text)

    # Generate embeddings for each chunk
    chunk_data = []

    for index, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)

        chunk_data.append({
            "chunk_index": index,
            "text": chunk,
            "embedding": embedding
        })

    # Save extracted text, chunks, and embeddings in MongoDB
    documents_collection.update_one(
        {"_id": ObjectId(document_id)},
        {
            "$set": {
                "extracted_text": extracted_text,
                "chunks": chunk_data
            }
        }
    )

    return {
        "message": "PDF text extracted and embeddings generated successfully",
        "total_pages": len(reader.pages),
        "total_chunks": len(chunk_data),
        "extracted_text": extracted_text
    }

