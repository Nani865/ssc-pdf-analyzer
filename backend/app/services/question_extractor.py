"""Question Extraction and Analysis Service"""
import hashlib
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger(__name__)

class QuestionExtractor:
    """Extract, normalize, and deduplicate questions"""
    
    def __init__(self, similarity_threshold: float = 0.75):
        self.similarity_threshold = similarity_threshold
        self.logger = logger
    
    def normalize_question(self, text: str) -> str:
        """
        Normalize question text for comparison.
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove punctuation variations
        text = text.replace('  ', ' ').lower()
        return text.strip()
    
    def get_question_hash(self, text: str) -> str:
        """
        Generate hash for question for exact duplicate detection.
        """
        normalized = self.normalize_question(text)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def find_similar_questions(self, questions: List[str]) -> List[Tuple[int, int, float]]:
        """
        Find similar questions using TF-IDF and cosine similarity.
        Returns: [(q1_index, q2_index, similarity_score), ...]
        """
        if len(questions) < 2:
            return []
        
        try:
            # Vectorize questions
            vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
            tfidf_matrix = vectorizer.fit_transform(questions)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Extract pairs above threshold
            similar_pairs = []
            for i in range(len(questions)):
                for j in range(i + 1, len(questions)):
                    score = similarity_matrix[i][j]
                    if score >= self.similarity_threshold:
                        similar_pairs.append((i, j, float(score)))
            
            self.logger.info(f"Found {len(similar_pairs)} similar question pairs")
            return similar_pairs
        
        except Exception as e:
            self.logger.error(f"Error finding similar questions: {str(e)}")
            return []
    
    def classify_similarity(self, score: float) -> str:
        """
        Classify similarity score into categories.
        """
        if score >= 0.95:
            return "exact"
        elif score >= 0.85:
            return "high"
        elif score >= 0.75:
            return "medium"
        else:
            return "low"
    
    def group_similar_questions(self, questions: List[Dict]) -> List[List[Dict]]:
        """
        Group similar questions together.
        """
        question_texts = [q["text"] for q in questions]
        groups = []
        processed = set()
        
        similar_pairs = self.find_similar_questions(question_texts)
        
        for i, question in enumerate(questions):
            if i in processed:
                continue
            
            group = [question]
            processed.add(i)
            
            # Find all similar questions
            for q1_idx, q2_idx, score in similar_pairs:
                if q1_idx == i and q2_idx not in processed:
                    group.append(questions[q2_idx])
                    processed.add(q2_idx)
                elif q2_idx == i and q1_idx not in processed:
                    group.append(questions[q1_idx])
                    processed.add(q1_idx)
            
            groups.append(group)
        
        return groups
    
    def extract_topics(self, questions: List[str]) -> Dict[str, List[int]]:
        """
        Basic topic extraction from questions.
        """
        topics = {}
        
        # Topic keywords mapping
        topic_keywords = {
            "Government": ["government", "administration", "ministry", "department"],
            "Constitution": ["constitution", "article", "amendment", "right"],
            "History": ["history", "historical", "era", "period", "reign"],
            "Geography": ["geography", "geographic", "location", "country", "city"],
            "Economy": ["economy", "economic", "trade", "commerce", "business"],
            "Science": ["science", "scientific", "physics", "chemistry", "biology"],
            "General Knowledge": ["general", "knowledge", "famous", "notable"]
        }
        
        for idx, question in enumerate(questions):
            question_lower = question.lower()
            found_topic = False
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    if topic not in topics:
                        topics[topic] = []
                    topics[topic].append(idx)
                    found_topic = True
                    break
            
            if not found_topic:
                if "Other" not in topics:
                    topics["Other"] = []
                topics["Other"].append(idx)
        
        return topics
