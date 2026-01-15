#!/usr/bin/env python3
"""
Quick test script for lab report extraction.
Usage: python test_extraction.py <path_to_lab_report_image>
"""

import asyncio
import sys
import json
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our clients
from medgemma_api import get_client
from report_parser import load_report, preprocess_image


async def test_extraction(file_path: str):
    """Test lab value extraction on a file."""

    print(f"\n{'='*60}")
    print(f"Testing extraction on: {file_path}")
    print('='*60)

    # Load file
    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    filename = Path(file_path).name

    # Convert to images
    print("\nLoading report...")
    images = load_report(file_bytes, filename)
    print(f"Found {len(images)} page(s)")

    # Get client
    print("\nInitializing AI client...")
    client = get_client()
    print(f"Using: {client.__class__.__name__}")

    # Process each page
    all_results = []
    for i, image in enumerate(images):
        print(f"\nProcessing page {i+1}...")

        # Preprocess
        processed = preprocess_image(image)
        print(f"Image size: {processed.size}")

        # Extract
        print("Extracting lab values (this may take 30-60 seconds)...")
        results = await client.extract_lab_values(processed)

        all_results.extend(results)
        print(f"Found {len(results)} lab values on this page")

    # Display results
    print(f"\n{'='*60}")
    print("EXTRACTION RESULTS")
    print('='*60)

    if all_results:
        print(json.dumps(all_results, indent=2))

        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print('='*60)
        print(f"Total tests found: {len(all_results)}")

        normal = sum(1 for r in all_results if r.get('status') == 'normal')
        high = sum(1 for r in all_results if r.get('status') == 'high')
        low = sum(1 for r in all_results if r.get('status') == 'low')

        print(f"  Normal: {normal}")
        print(f"  High: {high}")
        print(f"  Low: {low}")
    else:
        print("No lab values extracted. Check the image quality and format.")

    return all_results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_extraction.py <path_to_lab_report>")
        print("\nSupported formats: PDF, PNG, JPG, JPEG")
        print("\nExample:")
        print("  python test_extraction.py ~/Downloads/my_blood_test.pdf")
        sys.exit(1)

    file_path = sys.argv[1]

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    asyncio.run(test_extraction(file_path))
