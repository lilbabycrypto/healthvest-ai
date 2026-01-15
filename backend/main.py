"""
HealthVest AI - Lab Report Analyzer Backend
FastAPI server for processing lab reports with MedGemma
"""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from report_parser import load_report, preprocess_image
from medgemma_client import get_client

load_dotenv()

app = FastAPI(
    title="HealthVest AI",
    description="AI-powered lab report analyzer using MedGemma",
    version="0.1.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class LabValue(BaseModel):
    test_name: str
    value: float
    unit: str
    reference_range: str
    status: str  # normal, high, low
    explanation: Optional[str] = None


class AnalysisResult(BaseModel):
    filename: str
    analyzed_at: str
    lab_values: list[LabValue]
    page_count: int


class ExplanationRequest(BaseModel):
    test_name: str
    value: float
    unit: str
    reference_range: str
    status: str


# Routes
@app.get("/")
def root():
    return {
        "name": "HealthVest AI",
        "version": "0.1.0",
        "description": "Lab report analyzer powered by MedGemma"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_report(file: UploadFile = File(...)):
    """
    Upload and analyze a lab report.

    Accepts PDF or image files (PNG, JPG, JPEG).
    Returns extracted lab values with status indicators.
    """
    # Validate file type
    allowed_types = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, PNG, JPG"
        )

    try:
        # Read file
        file_bytes = await file.read()

        # Convert to images
        images = load_report(file_bytes, file.filename)

        # Get MedGemma client
        client = get_client()

        # Process each page
        all_lab_values = []
        for image in images:
            # Preprocess
            processed_image = preprocess_image(image)

            # Extract lab values
            extracted = client.extract_lab_values(processed_image)

            for item in extracted:
                lab_value = LabValue(
                    test_name=item.get("test_name", "Unknown"),
                    value=float(item.get("value", 0)),
                    unit=item.get("unit", ""),
                    reference_range=item.get("reference_range", "N/A"),
                    status=item.get("status", "normal")
                )
                all_lab_values.append(lab_value)

        return AnalysisResult(
            filename=file.filename,
            analyzed_at=datetime.utcnow().isoformat(),
            lab_values=all_lab_values,
            page_count=len(images)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain")
async def explain_value(request: ExplanationRequest):
    """
    Get a plain English explanation for a lab value.
    """
    try:
        client = get_client()
        explanation = client.explain_lab_value(
            test_name=request.test_name,
            value=request.value,
            unit=request.unit,
            reference_range=request.reference_range,
            status=request.status
        )

        return {
            "test_name": request.test_name,
            "explanation": explanation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
