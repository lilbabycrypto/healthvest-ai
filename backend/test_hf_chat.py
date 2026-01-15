#!/usr/bin/env python3
"""
Test MedGemma using HF Chat Completions API format.
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

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

def pdf_to_image(pdf_path: str) -> Image.Image:
    from pdf2image import convert_from_path
    images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
    return images[0]

def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def test_with_chat_api(image: Image.Image):
    """Test using HF's OpenAI-compatible chat API."""

    print("\nTesting with HF Chat Completions API...")

    # Resize
    max_size = 800
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    print(f"Image size: {image.size}")
    image_b64 = image_to_base64(image)

    # OpenAI-compatible format
    payload = {
        "model": "google/medgemma-4b-it",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """Extract all lab test values from this medical report.
Return a JSON array with objects containing: test_name, value, unit, reference_range, status (normal/high/low).
Only return the JSON array, no other text."""
                    }
                ]
            }
        ],
        "max_tokens": 1024
    }

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    # Try serverless inference (new router endpoint)
    api_url = "https://router.huggingface.co/hf-inference/v1/chat/completions"

    print("Calling API...")

    with httpx.Client(timeout=120.0) as client:
        response = client.post(api_url, headers=headers, json=payload)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\nSuccess!")
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(content)
        else:
            print(f"Error: {response.text[:500]}")

            # Check model availability
            if "not available" in response.text or "loading" in response.text:
                print("\nModel may not be available on serverless. Trying alternative...")
                return False

    return True

def test_with_replicate():
    """Try Replicate as alternative."""
    print("\n--- Alternative: Replicate ---")
    print("MedGemma is available on Replicate with free credits.")
    print("Get API key at: https://replicate.com/account/api-tokens")

if __name__ == "__main__":
    test_file = sys.argv[1] if len(sys.argv) > 1 else "/Users/laptopfirst/Downloads/41010638-Feb-2024.pdf"

    if not Path(test_file).exists():
        print(f"File not found: {test_file}")
        sys.exit(1)

    print(f"Testing: {test_file}")

    if test_file.lower().endswith('.pdf'):
        image = pdf_to_image(test_file)
    else:
        image = Image.open(test_file).convert('RGB')

    success = test_with_chat_api(image)

    if not success:
        test_with_replicate()
