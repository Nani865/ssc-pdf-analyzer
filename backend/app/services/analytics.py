"""Analytics Service"""
from typing import List, Dict
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Generate analytics and insights from question data"""
    
    def __init__(self):
        self.logger = logger
    
    def get_top_repeated_questions(self, similarities: List[Dict], limit: int = 20) -> List[Dict]:
        """
        Get top repeated questions.
        """
        question_counts = Counter()
        
        for sim in similarities:
            question_counts[sim['question_id_1']] += 1
            question_counts[sim['question_id_2']] += 1
        
        top_questions = question_counts.most_common(limit)
        return [
            {"question_id": q_id, "count": count}
            for q_id, count in top_questions
        ]
    
    def get_difficulty_distribution(self, questions: List[Dict]) -> Dict:
        """
        Analyze difficulty distribution.
        """
        difficulty_count = Counter()
        
        for question in questions:
            difficulty = question.get('difficulty', 'Unknown')
            difficulty_count[difficulty] += 1
        
        return dict(difficulty_count)
    
    def get_topic_distribution(self, questions: List[Dict]) -> Dict:
        """
        Analyze topic distribution.
        """
        topic_count = Counter()
        
        for question in questions:
            topic = question.get('topic', 'Unknown')
            topic_count[topic] += 1
        
        return dict(topic_count)
    
    def get_year_wise_distribution(self, papers: List[Dict]) -> Dict:
        """
        Analyze year-wise distribution of papers.
        """
        year_count = Counter()
        
        for paper in papers:
            year = paper.get('exam_year', 'Unknown')
            year_count[year] += 1
        
        return dict(sorted(year_count.items()))
    
    def generate_summary_report(self, papers: List[Dict], questions: List[Dict], similarities: List[Dict]) -> Dict:
        """
        Generate comprehensive summary report.
        """
        total_questions = len(questions)
        unique_hashes = len(set(q.get('hash_value') for q in questions))
        repeated_count = total_questions - unique_hashes
        
        return {
            "summary": {
                "total_papers": len(papers),
                "total_questions": total_questions,
                "unique_questions": unique_hashes,
                "repeated_questions": repeated_count,
                "similarity_pairs": len(similarities),
                "repetition_percentage": round((repeated_count / total_questions * 100), 2) if total_questions > 0 else 0
            },
            "top_repeated": self.get_top_repeated_questions(similarities),
            "difficulty_distribution": self.get_difficulty_distribution(questions),
            "topic_distribution": self.get_topic_distribution(questions),
            "year_wise_distribution": self.get_year_wise_distribution(papers)
        }
