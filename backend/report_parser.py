"""
Report Parser - Handles PDF and image uploads
Converts lab reports to images for MedGemma processing
"""

import io
from pathlib import Path
from PIL import Image
from typing import Union

# Optional: For PDF support
try:
    from pdf2image import convert_from_bytes
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: pdf2image not installed. PDF support disabled.")


def load_report(file_bytes: bytes, filename: str) -> list[Image.Image]:
    """
    Load a lab report from bytes and convert to PIL Images.

    Args:
        file_bytes: Raw file bytes
        filename: Original filename (used to detect format)

    Returns:
        List of PIL Images (one per page for PDFs)
    """
    filename_lower = filename.lower()

    # Handle PDFs
    if filename_lower.endswith('.pdf'):
        if not PDF_SUPPORT:
            raise ValueError("PDF support not available. Please install pdf2image and poppler.")
        images = convert_from_bytes(file_bytes, dpi=200)
        return images

    # Handle images
    if filename_lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
        image = Image.open(io.BytesIO(file_bytes))
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return [image]

    raise ValueError(f"Unsupported file format: {filename}")


def preprocess_image(image: Image.Image, max_size: int = 1568) -> Image.Image:
    """
    Preprocess image for MedGemma.
    MedGemma works best with images up to 1568x1568.

    Args:
        image: PIL Image
        max_size: Maximum dimension

    Returns:
        Preprocessed PIL Image
    """
    # Resize if too large while maintaining aspect ratio
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    return image


def extract_text_regions(image: Image.Image) -> dict:
    """
    Optional: Use OCR to extract text regions for validation.
    Requires pytesseract and tesseract-ocr installed.
    """
    try:
        import pytesseract
        text = pytesseract.image_to_string(image)
        return {"raw_text": text}
    except Exception as e:
        return {"error": str(e)}
