#!/usr/bin/env python3
"""
Test MedGemma locally using transformers on Mac MPS.
"""

import os
import sys
import json
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

def pdf_to_image(pdf_path: str) -> Image.Image:
    from pdf2image import convert_from_path
    images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
    return images[0]

def test_local_medgemma(image: Image.Image):
    """Test MedGemma locally with transformers."""

    print("\nLoading MedGemma locally...")
    print("This will download ~8GB model on first run.")

    import torch
    from transformers import AutoProcessor, AutoModelForImageTextToText

    # Check device
    if torch.backends.mps.is_available():
        device = "mps"
        dtype = torch.bfloat16
        print("Using Apple Silicon (MPS)")
    elif torch.cuda.is_available():
        device = "cuda"
        dtype = torch.bfloat16
        print("Using CUDA GPU")
    else:
        device = "cpu"
        dtype = torch.float32
        print("Using CPU (will be slow)")

    # MedGemma model
    model_id = "google/medgemma-4b-it"

    print(f"\nLoading processor from {model_id}...")
    processor = AutoProcessor.from_pretrained(
        model_id,
        token=os.getenv("HF_TOKEN"),
        trust_remote_code=True
    )

    print("Loading model (this takes 2-5 minutes first time)...")
    model = AutoModelForImageTextToText.from_pretrained(
        model_id,
        token=os.getenv("HF_TOKEN"),
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True
    )

    print("Model loaded!")

    # Resize image
    max_size = 896
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    print(f"Image size: {image.size}")

    # Prepare prompt
    prompt = """Extract all lab test values from this medical report.
Return a JSON array with: test_name, value, unit, reference_range, status.
Only output JSON."""

    # Process
    print("\nExtracting lab values...")
    inputs = processor(
        images=image,
        text=prompt,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            do_sample=False
        )

    response = processor.decode(outputs[0], skip_special_tokens=True)

    print("\n" + "="*50)
    print("EXTRACTION RESULT:")
    print("="*50)
    print(response)

    # Try to parse JSON
    try:
        start = response.find('[')
        end = response.rfind(']') + 1
        if start != -1 and end > start:
            data = json.loads(response[start:end])
            print(f"\nParsed {len(data)} lab values")
    except:
        pass

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

    test_local_medgemma(image)
