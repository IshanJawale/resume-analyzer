# Resume Analyzer - Clean Project Structure

## Project Overview
This is a Django-based resume analysis application that uses AI (Groq API) to extract and analyze resume data.

## Project Structure
```
resume_analyzer/
├── .env                    # Environment variables (GROQ_API_KEY)
├── .env.example           # Example environment file
├── db.sqlite3             # SQLite database
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── resume.pdf            # Sample resume for testing
│
├── a_core/               # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py       # Main Django settings
│   ├── urls.py           # URL configuration
│   └── wsgi.py
│
├── a_resume/             # Main application
│   ├── __init__.py
│   ├── admin.py          # Django admin configuration
│   ├── apps.py
│   ├── forms.py          # Django forms
│   ├── models.py         # Database models
│   ├── tests.py
│   ├── urls.py           # App URL patterns
│   ├── views.py          # Views and business logic
│   ├── management/       # Custom management commands
│   └── migrations/       # Database migrations
│
├── Analyze/              # Analysis engine
│   ├── __init__.py
│   └── new_analysis_service.py  # Complete analysis service with text extraction and AI analysis
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── a_resume/
│   ├── includes/
│   └── layouts/
│
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded files
└── venv/                 # Python virtual environment
```

## Key Components

### 1. Analysis Service (Analyze/new_analysis_service.py)
- Complete analysis engine with integrated text extraction
- PDF text extraction using pdfplumber and OCR fallback
- AI-powered data extraction using Groq API
- Calculates scores and generates recommendations
- Fully self-contained with no external dependencies

### 2. Database Models (a_resume/models.py)
- ResumeAnalysis: Stores extracted data and analysis results
- Uses JSON fields for flexible data storage

### 3. Web Interface (templates/a_resume/)
- Upload interface for resumes
- Analysis results display
- Dashboard for viewing history

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Add your GROQ_API_KEY to .env
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start development server:
   ```bash
   python manage.py runserver
   ```

## Features

- ✅ AI-powered resume analysis using Groq API
- ✅ Structured data extraction (name, email, skills, experience, etc.)
- ✅ Scoring system with recommendations
- ✅ Web interface for uploads and results
- ✅ PostgreSQL/SQLite database support
- ✅ User authentication and dashboard
- ✅ Responsive design with Bootstrap

## API Integration

The system uses the Groq API with the `meta-llama/llama-4-scout-17b-16e-instruct` model for:
- Text analysis and information extraction
- Structured data formatting
- Resume content understanding

## Database Schema

The `ResumeAnalysis` model stores:
- Personal information (name, email, phone)
- JSON arrays for skills, experience, projects, education
- Analysis scores and recommendations
- User association and metadata

Project cleaned and ready for production use!
