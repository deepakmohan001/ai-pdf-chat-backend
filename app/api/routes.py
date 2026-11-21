from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.database.connection import documents_collection, chat_history_collection
from app.services.chunking import split_text_into_chunks
from app.services.embedding import generate_embedding
from app.services.ollama_service import generate_answer
from sentence_transformers import util
from pypdf import PdfReader
from bson import ObjectId
import shutil
import os
from datetime import datetime, timezone
import uuid


router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    document_id: str



# Home endpoint
@router.get("/")
def home():
    return {
        "message": "Welcome to AI PDF Chat Application"
    }

@router.post("/ask")
def ask_question(data: QuestionRequest):

    # Step 1: Validate document ID
    if not ObjectId.is_valid(data.document_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    # Step 2: Retrieve selected PDF
    document = documents_collection.find_one({
        "_id": ObjectId(data.document_id),
        "chunks": {"$exists": True}
    })

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found or PDF has not been processed"
        )

    chunks = document.get("chunks", [])

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No processed chunks found in this document"
        )

    # Step 3: Generate question embedding
    question_embedding = generate_embedding(data.question)

    # Step 4: Calculate similarity scores
    scored_chunks = []

    for chunk in chunks:

        similarity = util.cos_sim(
            question_embedding,
            chunk["embedding"]
        )

        score = similarity.item()

        scored_chunks.append({
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "score": score
        })

    # Step 5: Sort chunks by similarity
    scored_chunks.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # Step 6: Retrieve top 3 chunks
    TOP_K = 3
    top_chunks = scored_chunks[:TOP_K]

    # Step 7: Check similarity threshold
    SIMILARITY_THRESHOLD = 0.20

    highest_score = top_chunks[0]["score"]

    if highest_score < SIMILARITY_THRESHOLD:
        raise HTTPException(
            status_code=404,
            detail="No relevant information found in the selected document"
        )

    # Step 8: Combine retrieved chunks
    context = "\n\n".join(
        chunk["text"] for chunk in top_chunks
    )

    # Step 9: Generate AI answer
    answer = generate_answer(
        data.question,
        context
    )

    # Step 10: Save chat history
    chat_record = {
        "document_id": data.document_id,
        "filename": document["filename"],
        "question": data.question,
        "answer": answer,
        "similarity_score": highest_score,
        "retrieved_chunks": [
            {
                "chunk_index": chunk["chunk_index"],
                "similarity_score": chunk["score"]
            }
            for chunk in top_chunks
        ],
        "created_at": datetime.now(timezone.utc)
    }

    chat_history_collection.insert_one(chat_record)

    # Step 11: Return response
    return {
        "question": data.question,
        "document_id": data.document_id,
        "filename": document["filename"],
        "retrieved_chunks": [
            chunk["chunk_index"] for chunk in top_chunks
        ],
        "similarity_score": highest_score,
        "answer": answer
    }


# Get all documents

@router.get("/documents")
def get_documents():

    # Retrieve documents from MongoDB
    documents = list(
        documents_collection.find(
            {},
            {
                "filename": 1,
                "file_type": 1,
                "file_path": 1,
                "created_at": 1,
                "chunks": 1
            }
        )
    )

    # Prepare response
    result = []

    for document in documents:

        result.append({
            "document_id": str(document["_id"]),
            "filename": document["filename"],
            "file_type": document.get("file_type"),
            "file_path": document.get("file_path"),
            "total_chunks": len(document.get("chunks", [])),
            "created_at": document.get("created_at")
        })

    return {
        "total_documents": len(result),
        "documents": result
    }


# Delete selected PDF
@router.delete("/documents/{document_id}")
def delete_document(document_id: str):

    # 1. Validate document ID
    if not ObjectId.is_valid(document_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    # 2. Find document
    document = documents_collection.find_one({
        "_id": ObjectId(document_id)
    })

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # 3. Delete PDF file
    file_path = document.get("file_path")

    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    # 4. Delete related chat history
    chat_history_collection.delete_many({
        "document_id": document_id
    })

    # 5. Delete MongoDB document
    documents_collection.delete_one({
        "_id": ObjectId(document_id)
    })

    return {
        "message": "Document deleted successfully"
    }


# Upload PDF

@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    # Check PDF file extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
        
        
    # Validate actual PDF file signature
    file_signature = file.file.read(5)

    if file_signature != b"%PDF-":
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    # Reset file pointer
    file.file.seek(0)    

    # Check PDF file size (maximum 50 MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024

    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF file size must not exceed 50 MB"
        )

    # Create uploads folder if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Generate a unique filename
    unique_filename = f"{uuid.uuid4()}.pdf"

    # Create file path using unique filename
    file_path = os.path.join("uploads", unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document = {
            "filename": file.filename,
            "stored_filename": unique_filename,
            "file_path": file_path,
            "file_type": file.content_type,
            "created_at": datetime.now(timezone.utc)
        }

        result = documents_collection.insert_one(document)

        return {
            "message": "PDF uploaded successfully",
            "filename": file.filename,
            "document_id": str(result.inserted_id)
        }

    except Exception as error:
        # Remove partially saved file if upload fails
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"PDF upload failed: {str(error)}"
        )

    finally:
        file.file.close()



# Extract PDF text and generate embeddings
@router.get("/extract-text/{document_id}")
def extract_pdf_text(document_id: str):

    # Step 1: Validate document ID
    if not ObjectId.is_valid(document_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    # Step 2: Find document
    document = documents_collection.find_one(
        {"_id": ObjectId(document_id)}
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Step 3: Check PDF file
    file_path = document.get("file_path")

    if not file_path or not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail="PDF file not found on server"
        )

    try:
        # Step 4: Read PDF
        reader = PdfReader(file_path)

        extracted_text = ""

        for page in reader.pages:
            text = page.extract_text()

            if text:
                extracted_text += text + "\n"

        # Step 5: Check extracted text
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in this PDF"
            )

        # Step 6: Split text into chunks
        chunks = split_text_into_chunks(extracted_text)

        # Step 7: Generate embeddings
        chunk_data = []

        for index, chunk in enumerate(chunks):

            embedding = generate_embedding(chunk)

            chunk_data.append({
                "chunk_index": index,
                "text": chunk,
                "embedding": embedding
            })

        # Step 8: Save in MongoDB
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
            "total_chunks": len(chunk_data)
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(error)}"
        )




@router.get("/chat-history/{document_id}")
def get_chat_history(document_id: str):

    # Validate document ID
    if not ObjectId.is_valid(document_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    # Retrieve chat history for the selected PDF
    history = list(
        chat_history_collection.find(
            {"document_id": document_id}
        ).sort("created_at", 1)
    )

    # Convert MongoDB ObjectId to string
    for chat in history:
        chat["_id"] = str(chat["_id"])

    return {
        "document_id": document_id,
        "total_chats": len(history),
        "chat_history": history
    }



@router.delete("/chat-history/{document_id}")
def delete_chat_history(document_id: str):

    # Validate document ID
    if not ObjectId.is_valid(document_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    # Delete all chat history for the selected PDF
    result = chat_history_collection.delete_many(
        {"document_id": document_id}
    )

    return {
        "message": "Chat history deleted successfully",
        "deleted_count": result.deleted_count
    }
