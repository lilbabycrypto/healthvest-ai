"""
MedGemma Client for Lab Report Analysis
Uses MedGemma 1.5 4B from Hugging Face
"""

import os
import json
from pathlib import Path
from PIL import Image
import torch
from transformers import pipeline

# Load prompts
PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(name: str) -> str:
    """Load a prompt template from file."""
    with open(PROMPTS_DIR / f"{name}.txt", "r") as f:
        return f.read()

class MedGemmaClient:
    """Client for interacting with MedGemma model."""

    def __init__(self, model_path: str = None):
        """
        Initialize MedGemma client.

        Args:
            model_path: Local path or Hugging Face model ID for MedGemma
        """
        # Use local model if available, otherwise fall back to HF
        local_model = Path(__file__).parent.parent / "models" / "medgemma-1.5-4b-it"
        if model_path:
            self.model_id = model_path
        elif local_model.exists():
            self.model_id = str(local_model)
            print(f"Using local model: {self.model_id}")
        else:
            self.model_id = "google/medgemma-1.5-4b-it"
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

    def load_model(self):
        """Load model using pipeline."""
        if self.pipe is None:
            print(f"Loading MedGemma model on {self.device}...")

            self.pipe = pipeline(
                "image-text-to-text",
                model=self.model_id,
                device=self.device,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                trust_remote_code=True,
            )

            print("Model loaded successfully!")

    def extract_lab_values(self, image: Image.Image) -> list[dict]:
        """
        Extract lab values from a lab report image.

        Args:
            image: PIL Image of the lab report

        Returns:
            List of extracted lab values with test_name, value, unit, reference_range, status
        """
        self.load_model()

        extraction_prompt = load_prompt("extract")

        # Use pipeline with image and text
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": extraction_prompt}
                ]
            }
        ]

        output = self.pipe(messages, max_new_tokens=2048)
        response = output[0]["generated_text"][-1]["content"]

        # Parse JSON from response
        try:
            # Find JSON array in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        return []

    def explain_lab_value(self, test_name: str, value: float, unit: str,
                          reference_range: str, status: str) -> str:
        """
        Generate a plain English explanation for a lab value.

        Args:
            test_name: Name of the test
            value: Test value
            unit: Unit of measurement
            reference_range: Normal range
            status: normal/high/low

        Returns:
            Plain English explanation
        """
        self.load_model()

        explanation_prompt = load_prompt("explain").format(
            test_name=test_name,
            value=value,
            unit=unit,
            reference_range=reference_range,
            status=status
        )

        # Text-only query
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": explanation_prompt}
                ]
            }
        ]

        output = self.pipe(messages, max_new_tokens=256)
        response = output[0]["generated_text"][-1]["content"]

        return response


# Singleton instance
_client = None

def get_client() -> MedGemmaClient:
    """Get or create MedGemma client singleton."""
    global _client
    if _client is None:
        _client = MedGemmaClient()
    return _client


if __name__ == "__main__":
    # Test the client
    client = get_client()
    print(f"MedGemma client initialized. Device: {client.device}")
