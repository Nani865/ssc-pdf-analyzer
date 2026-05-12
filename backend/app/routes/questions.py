"""Question endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from collections import Counter

from app.database import get_db, Question, Similarity
from app.schemas import QuestionResponse, AnalyticsQuestion

router = APIRouter()

@router.get("/")
async def list_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> List[QuestionResponse]:
    """
    List all extracted questions with pagination.
    """
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions

@router.get("/count")
async def count_questions(db: Session = Depends(get_db)):
    """
    Get total count of questions.
    """
    total = db.query(func.count(Question.id)).scalar()
    unique = db.query(func.count(func.distinct(Question.hash_value))).scalar()
    
    return {
        "total_questions": total,
        "unique_questions": unique,
        "repeated_questions": total - unique
    }

@router.get("/repeated")
async def get_repeated_questions(
    limit: int = Query(20, ge=1, le=100),
    threshold: float = Query(0.75, ge=0, le=1),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get most repeated questions.
    """
    # Find similarities above threshold
    similarities = db.query(Similarity).filter(
        Similarity.similarity_score >= threshold
    ).order_by(Similarity.similarity_score.desc()).limit(limit).all()
    
    result = []
    for sim in similarities:
        q1 = db.query(Question).filter(Question.id == sim.question_id_1).first()
        q2 = db.query(Question).filter(Question.id == sim.question_id_2).first()
        
        if q1 and q2:
            result.append({
                "question_1": {
                    "id": q1.id,
                    "text": q1.text,
                    "paper_id": q1.paper_id
                },
                "question_2": {
                    "id": q2.id,
                    "text": q2.text,
                    "paper_id": q2.paper_id
                },
                "similarity_score": sim.similarity_score,
                "type": sim.similarity_type
            })
    
    return result

@router.get("/by-topic")
async def get_questions_by_topic(
    db: Session = Depends(get_db)
) -> dict:
    """
    Get questions grouped by topic.
    """
    topics = db.query(Question.topic, func.count(Question.id)).group_by(
        Question.topic
    ).all()
    
    return {
        "topics": [
            {"topic": topic, "count": count}
            for topic, count in topics if topic
        ]
    }

@router.get("/by-difficulty")
async def get_questions_by_difficulty(
    db: Session = Depends(get_db)
) -> dict:
    """
    Get questions grouped by difficulty level.
    """
    difficulties = db.query(
        Question.difficulty,
        func.count(Question.id)
    ).group_by(Question.difficulty).all()
    
    return {
        "difficulties": [
            {"level": level, "count": count}
            for level, count in difficulties if level
        ]
    }

@router.get("/search")
async def search_questions(
    q: str = Query(..., min_length=3),
    db: Session = Depends(get_db)
) -> List[QuestionResponse]:
    """
    Search questions by text.
    """
    results = db.query(Question).filter(
        Question.text.ilike(f"%{q}%")
    ).limit(50).all()
    
    return results
