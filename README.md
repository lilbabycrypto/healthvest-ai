# HealthVest AI - Lab Report Analyzer

AI-powered lab report analysis using MedGemma 1.5 for the [MedGemma Impact Challenge](https://www.kaggle.com/competitions/med-gemma-impact-challenge).

## Problem

Indian patients struggle to:
- Understand lab reports (medical jargon, reference ranges)
- Track health trends over time
- Know when values are concerning
- Prepare informed questions for doctors

## Solution

Upload blood test reports (PDF/image) and get:
- **Extracted Values**: All test values parsed automatically
- **Plain English Explanations**: What each value means
- **Status Indicators**: Normal/High/Low flagging
- **Trend Tracking**: Compare with previous reports (coming soon)

## Tech Stack

- **AI Model**: MedGemma 1.5 4B (Google's medical AI)
- **Backend**: Python + FastAPI
- **Frontend**: Next.js (planned)
- **Database**: Supabase

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

API runs at `http://localhost:8000`

### Test with Notebook

```bash
cd notebooks
jupyter notebook medgemma_test.ipynb
```

## API Endpoints

- `POST /analyze` - Upload and analyze a lab report
- `POST /explain` - Get explanation for a specific lab value
- `GET /health` - Health check

## Project Structure

```
healthvest-ai/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── medgemma_client.py   # MedGemma integration
│   ├── report_parser.py     # PDF/image handling
│   └── prompts/             # Prompt templates
├── frontend/                # Next.js app (planned)
├── notebooks/               # Experimentation
└── submission/              # Competition materials
```

## Team

- Himanshu Balara ([@himanshu-balara](https://linkedin.com/in/himanshu-balara))

## License

MIT
