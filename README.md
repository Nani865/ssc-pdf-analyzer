# SSC PDF Analyzer 📄🔍

An AI-powered PDF analyzer and question list maker for SSC aspirants. Automatically extracts questions from previous year question papers, identifies repeated questions, and generates comprehensive analytics.

## Features ✨

- **PDF Processing**: Handle up to 100 PDF files simultaneously
- **Question Extraction**: Intelligent extraction of questions from PDFs
- **Duplicate Detection**: AI-powered duplicate and similar question identification
- **Analytics**: Find most repeated questions, topic distribution, difficulty levels
- **Export**: Generate reports in JSON, CSV formats
- **REST API**: Complete FastAPI backend with RESTful endpoints
- **Web Dashboard**: React-based frontend for easy interaction

## Tech Stack 🛠️

**Backend:**
- FastAPI (modern Python web framework)
- SQLAlchemy (ORM)
- SQLite (database)
- PyPDF2 & pdfplumber (PDF processing)
- scikit-learn (ML/NLP)
- spaCy (NLP)

**Frontend:**
- React with TypeScript
- Axios (HTTP client)
- Tailwind CSS (styling)

## Project Structure 📁

```
ssc-pdf-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   │   ├── pdf_processor.py
│   │   │   ├── question_extractor.py
│   │   │   └── analytics.py
│   │   └── routes/
│   │       ├── papers.py
│   │       └── questions.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   └── package.json
└── docker-compose.yml
```

## Quick Start 🚀

### Prerequisites
- Python 3.9+
- Node.js 16+
- pip & npm

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

UI will be available at: `http://localhost:3000`

## API Endpoints 📡

### Papers
- `POST /api/papers/upload` - Upload PDF files
- `GET /api/papers` - List all papers
- `GET /api/papers/{paper_id}` - Get paper details
- `DELETE /api/papers/{paper_id}` - Delete paper

### Questions
- `GET /api/questions` - List all extracted questions
- `GET /api/questions/repeated` - Get repeated questions
- `GET /api/questions/by-topic` - Questions grouped by topic
- `GET /api/questions/by-difficulty` - Questions grouped by difficulty

### Analytics
- `GET /api/analytics/summary` - Overall statistics
- `GET /api/analytics/duplicates` - Duplicate analysis
- `GET /api/analytics/export` - Export data (JSON/CSV)

## Usage Examples 📚

### 1. Upload PDFs
```bash
curl -X POST "http://localhost:8000/api/papers/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@paper1.pdf" \
  -F "files=@paper2.pdf"
```

### 2. Get Repeated Questions
```bash
curl "http://localhost:8000/api/questions/repeated"
```

### 3. Export Analytics
```bash
curl "http://localhost:8000/api/analytics/export?format=json" \
  -o analytics.json
```

## Configuration 🔧

Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=sqlite:///./ssc_analyzer.db
API_PORT=8000
API_HOST=0.0.0.0
MAX_PDF_FILES=100
SIMILARITY_THRESHOLD=0.75
```

## Docker Deployment 🐳

```bash
docker-compose up -d
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Database: SQLite (persistent volume)

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

MIT License - feel free to use this project for your needs.

## Support 💬

For issues and questions, please create a GitHub Issue.

---

**Made for SSC aspirants with ❤️**
