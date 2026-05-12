"""Database configuration and models"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ssc_analyzer.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Association table for question similarities
question_similarity = Table(
    'question_similarity',
    Base.metadata,
    Column('question_id_1', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('question_id_2', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('similarity_score', Float)
)

class Paper(Base):
    """Model for PDF papers"""
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    original_filename = Column(String)
    file_path = Column(String)
    exam_year = Column(String, nullable=True)
    exam_name = Column(String, nullable=True)
    total_pages = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Integer, default=0)  # Boolean as integer
    error_message = Column(Text, nullable=True)

    # Relationships
    questions = relationship("Question", back_populates="paper", cascade="all, delete-orphan")

class Question(Base):
    """Model for extracted questions"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey('papers.id'))
    text = Column(Text, index=True)
    page_number = Column(Integer)
    question_number = Column(Integer, nullable=True)
    topic = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)  # Easy, Medium, Hard
    extracted_at = Column(DateTime, default=datetime.utcnow)
    hash_value = Column(String, unique=True, index=True)  # For duplicate detection

    # Relationships
    paper = relationship("Paper", back_populates="questions")

class Similarity(Base):
    """Model for question similarities"""
    __tablename__ = "similarities"

    id = Column(Integer, primary_key=True, index=True)
    question_id_1 = Column(Integer, ForeignKey('questions.id'))
    question_id_2 = Column(Integer, ForeignKey('questions.id'))
    similarity_score = Column(Float)  # 0-1 range
    similarity_type = Column(String)  # exact, high, medium
    detected_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
