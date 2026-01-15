#!/usr/bin/env python3
"""
Quick test of MedGemma API with a sample lab report.
"""

import os
import sys
import json
import base64
import httpx
from pathlib import Path
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("Error: HF_TOKEN not found in .env")
    sys.exit(1)

# Try to convert PDF to image
def pdf_to_image(pdf_path: str) -> Image.Image:
    """Convert first page of PDF to image."""
    from pdf2image import convert_from_path
    images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
    return images[0]

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def test_medgemma_api(image: Image.Image):
    """Test MedGemma extraction via HF Inference API."""

    print("\nTesting MedGemma API...")

    # Resize if needed
    max_size = 1024
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    print(f"Image size: {image.size}")

    # Convert to base64
    image_b64 = image_to_base64(image)

    prompt = """Extract all lab test values from this medical report image.

For each test found, return a JSON object with:
- test_name: Name of the test
- value: The numeric value
- unit: Unit of measurement
- reference_range: Normal range shown
- status: "normal", "high", or "low"

Return ONLY a JSON array, no other text."""

    # Call HF Inference API (new router endpoint)
    api_url = "https://router.huggingface.co/hf-inference/models/google/medgemma-4b-it"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    # Format for vision model
    payload = {
        "inputs": f"<image>{image_b64}</image>\n{prompt}",
        "parameters": {
            "max_new_tokens": 1024,
            "return_full_text": False
        }
    }

    print("Calling MedGemma API (may take 30-60 seconds)...")

    with httpx.Client(timeout=120.0) as client:
        response = client.post(api_url, headers=headers, json=payload)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\nResponse:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")

            # Check if model is loading
            if "loading" in response.text.lower():
                print("\nModel is loading. Wait 1-2 minutes and try again.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default test file
        test_file = "/Users/laptopfirst/Downloads/41010638-Feb-2024.pdf"
    else:
        test_file = sys.argv[1]

    if not Path(test_file).exists():
        print(f"File not found: {test_file}")
        sys.exit(1)

    print(f"Testing with: {test_file}")

    # Load image
    if test_file.lower().endswith('.pdf'):
        print("Converting PDF to image...")
        image = pdf_to_image(test_file)
    else:
        image = Image.open(test_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')

    # Save preview
    preview_path = "/Users/laptopfirst/healthvest-ai/test_preview.png"
    image.save(preview_path)
    print(f"Preview saved to: {preview_path}")

    # Test API
    test_medgemma_api(image)
