"""Analytics endpoints"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import json
import csv
from io import StringIO
from pathlib import Path

from app.database import get_db, Question, Paper, Similarity
from app.schemas import AnalyticsSummary

router = APIRouter()

@router.get("/summary")
async def get_analytics_summary(db: Session = Depends(get_db)) -> dict:
    """
    Get comprehensive analytics summary.
    """
    # Count statistics
    total_papers = db.query(func.count(Paper.id)).scalar()
    total_questions = db.query(func.count(Question.id)).scalar()
    unique_questions = db.query(func.count(func.distinct(Question.hash_value))).scalar()
    
    # Top repeated questions
    repeated = db.query(
        Similarity.question_id_1,
        func.count(Similarity.id).label('count')
    ).group_by(Similarity.question_id_1).order_by(
        func.count(Similarity.id).desc()
    ).limit(10).all()
    
    top_repeated = []
    for q_id, count in repeated:
        q = db.query(Question).filter(Question.id == q_id).first()
        if q:
            top_repeated.append({
                "question_id": q.id,
                "text": q.text,
                "occurrences": count
            })
    
    # By topic
    topics = db.query(
        Question.topic,
        func.count(Question.id)
    ).filter(Question.topic.isnot(None)).group_by(Question.topic).all()
    
    by_topic = {topic: count for topic, count in topics}
    
    # By difficulty
    difficulties = db.query(
        Question.difficulty,
        func.count(Question.id)
    ).filter(Question.difficulty.isnot(None)).group_by(Question.difficulty).all()
    
    by_difficulty = {level: count for level, count in difficulties}
    
    return {
        "total_papers": total_papers or 0,
        "total_questions": total_questions or 0,
        "unique_questions": unique_questions or 0,
        "repeated_questions": (total_questions or 0) - (unique_questions or 0),
        "top_repeated_questions": top_repeated,
        "by_topic": by_topic,
        "by_difficulty": by_difficulty
    }

@router.get("/duplicates")
async def get_duplicate_analysis(
    threshold: float = Query(0.75, ge=0, le=1),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get detailed duplicate analysis.
    """
    similarities = db.query(Similarity).filter(
        Similarity.similarity_score >= threshold
    ).all()
    
    exact_duplicates = [s for s in similarities if s.similarity_type == "exact"]
    high_similarity = [s for s in similarities if s.similarity_type == "high"]
    medium_similarity = [s for s in similarities if s.similarity_type == "medium"]
    
    return {
        "threshold": threshold,
        "total_similarities": len(similarities),
        "exact_duplicates": len(exact_duplicates),
        "high_similarity": len(high_similarity),
        "medium_similarity": len(medium_similarity),
        "similarities": [
            {
                "question_1_id": s.question_id_1,
                "question_2_id": s.question_id_2,
                "score": s.similarity_score,
                "type": s.similarity_type
            }
            for s in similarities
        ]
    }

@router.get("/export")
async def export_analytics(
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Export analytics data in JSON or CSV format.
    """
    # Get all data
    questions = db.query(Question).all()
    papers = db.query(Paper).all()
    similarities = db.query(Similarity).all()
    
    if format == "json":
        data = {
            "papers": [
                {
                    "id": p.id,
                    "filename": p.filename,
                    "exam_year": p.exam_year,
                    "total_pages": p.total_pages,
                    "questions_count": len(p.questions)
                }
                for p in papers
            ],
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "paper_id": q.paper_id,
                    "topic": q.topic,
                    "difficulty": q.difficulty,
                    "page_number": q.page_number
                }
                for q in questions
            ],
            "similarities": [
                {
                    "question_id_1": s.question_id_1,
                    "question_id_2": s.question_id_2,
                    "score": s.similarity_score,
                    "type": s.similarity_type
                }
                for s in similarities
            ]
        }
        return {
            "status": "success",
            "format": "json",
            "data": data
        }
    
    elif format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        
        # Write questions
        writer.writerow(["Question ID", "Paper ID", "Text", "Topic", "Difficulty", "Page"])
        for q in questions:
            writer.writerow([q.id, q.paper_id, q.text, q.topic, q.difficulty, q.page_number])
        
        return {
            "status": "success",
            "format": "csv",
            "data": output.getvalue()
        }
