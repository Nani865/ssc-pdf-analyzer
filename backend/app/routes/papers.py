"""Paper endpoints"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import os
import shutil
from pathlib import Path

from app.database import get_db, Paper
from app.schemas import PaperResponse, PaperDetailResponse, UploadResponse
from app.services.pdf_processor import PDFProcessor

router = APIRouter()

# Create uploads directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_papers(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
) -> UploadResponse:
    """
    Upload multiple PDF files for analysis.
    Maximum 100 files per request.
    """
    max_files = int(os.getenv("MAX_PDF_FILES", 100))
    
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {max_files} files allowed per upload"
        )
    
    uploaded_files = []
    failed_files = []
    
    for file in files:
        try:
            if not file.filename.endswith(".pdf"):
                failed_files.append({"filename": file.filename, "error": "Not a PDF file"})
                continue
            
            # Save file
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create paper record
            paper = Paper(
                filename=file.filename,
                original_filename=file.filename,
                file_path=str(file_path),
                processed=0
            )
            db.add(paper)
            db.commit()
            db.refresh(paper)
            
            uploaded_files.append(file.filename)
            
        except Exception as e:
            failed_files.append({"filename": file.filename, "error": str(e)})
    
    return UploadResponse(
        status="success" if uploaded_files else "failed",
        message=f"Uploaded {len(uploaded_files)} files successfully",
        uploaded_files=uploaded_files,
        failed_files=failed_files if failed_files else None
    )

@router.get("/")
async def list_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[PaperResponse]:
    """
    List all uploaded papers with pagination.
    """
    papers = db.query(Paper).offset(skip).limit(limit).all()
    return papers

@router.get("/count")
async def count_papers(db: Session = Depends(get_db)):
    """
    Get total count of papers.
    """
    count = db.query(func.count(Paper.id)).scalar()
    return {"total_papers": count}

@router.get("/{paper_id}")
async def get_paper(
    paper_id: int,
    db: Session = Depends(get_db)
) -> PaperDetailResponse:
    """
    Get detailed information about a specific paper.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return paper

@router.delete("/{paper_id}")
async def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a paper and its associated data.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Delete file
    if os.path.exists(paper.file_path):
        os.remove(paper.file_path)
    
    # Delete from database
    db.delete(paper)
    db.commit()
    
    return {"message": "Paper deleted successfully"}

@router.post("/{paper_id}/process")
async def process_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """
    Process a paper to extract questions.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    try:
        processor = PDFProcessor()
        questions = processor.extract_questions(paper.file_path)
        paper.processed = 1
        db.commit()
        
        return {
            "status": "success",
            "paper_id": paper_id,
            "questions_extracted": len(questions)
        }
    except Exception as e:
        paper.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
