import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreService

router = APIRouter()
processor = DocumentProcessor()
vector_store = VectorStoreService()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_file_task(file_path: str, filename: str):
    try:
        metadata = {"source": filename, "type": "pdf"}
        chunks = await processor.process_file(file_path, metadata)
        
        vector_store.add_documents(chunks)
        print(f"Successfully processed {filename}: {len(chunks)} chunks added.")
        
    except Exception as e:
        print(f"Error background processing {filename}: {e}")
    finally:
        pass

@router.post("/")
async def ingest_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    saved_files = []
    
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
            
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            saved_files.append(file.filename)
            # Add background task
            background_tasks.add_task(process_file_task, file_path, file.filename)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}: {str(e)}")

    if not saved_files:
        raise HTTPException(status_code=400, detail="No valid PDF files found.")

    return {
        "message": f"Received {len(saved_files)} files. Processing started in background.",
        "files": saved_files
    }
