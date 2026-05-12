"""PDF Processing Service"""
import PyPDF2
import pdfplumber
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Extract text and metadata from PDF files"""
    
    def __init__(self):
        self.logger = logger
    
    def extract_text(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract text from PDF pages.
        Returns: {page_number: text}
        """
        pages_text = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages_text[page_num] = text
            
            self.logger.info(f"Extracted text from {len(pages_text)} pages")
            return pages_text
        
        except Exception as e:
            self.logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def extract_metadata(self, pdf_path: str) -> Dict:
        """
        Extract metadata from PDF.
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                metadata = pdf.metadata
                num_pages = len(pdf.pages)
            
            return {
                "title": metadata.get("/Title", "") if metadata else "",
                "author": metadata.get("/Author", "") if metadata else "",
                "pages": num_pages,
                "created": metadata.get("/CreationDate", "") if metadata else ""
            }
        
        except Exception as e:
            self.logger.warning(f"Could not extract metadata: {str(e)}")
            return {"pages": 0}
    
    def extract_questions(self, pdf_path: str) -> List[Dict]:
        """
        Extract questions from PDF using pattern recognition.
        """
        pages_text = self.extract_text(pdf_path)
        questions = []
        
        for page_num, text in pages_text.items():
            # Simple question extraction (can be improved with ML)
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                
                # Pattern matching for questions
                if self._is_question(line):
                    questions.append({
                        "text": line,
                        "page_number": page_num,
                        "question_number": len(questions) + 1
                    })
        
        self.logger.info(f"Extracted {len(questions)} questions from PDF")
        return questions
    
    @staticmethod
    def _is_question(text: str) -> bool:
        """
        Check if text is likely a question.
        """
        if len(text) < 10:
            return False
        
        # Check for question patterns
        patterns = [
            text.endswith('?'),
            text.startswith(('Q.', 'Q:', 'Question')),
            any(char.isdigit() and text[i+1] == '.' for i, char in enumerate(text[:-1])),
        ]
        
        return any(patterns)
