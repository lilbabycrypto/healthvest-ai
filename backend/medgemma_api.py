"""
MedGemma API Client - Uses Hugging Face Inference API
Simpler setup, no local GPU required
"""

import os
import json
import base64
import httpx
from pathlib import Path
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Load prompts
PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(name: str) -> str:
    """Load a prompt template from file."""
    with open(PROMPTS_DIR / f"{name}.txt", "r") as f:
        return f.read()


class MedGemmaAPIClient:
    """
    Client for MedGemma using Hugging Face Inference API.
    Requires HF_TOKEN environment variable.
    """

    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        if not self.hf_token:
            raise ValueError("HF_TOKEN environment variable not set. Get yours at https://huggingface.co/settings/tokens")

        # MedGemma model endpoint
        self.model_id = "google/medgemma-1.5-4b-it"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"

        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    async def extract_lab_values(self, image: Image.Image) -> list[dict]:
        """
        Extract lab values from a lab report image using API.

        Args:
            image: PIL Image of the lab report

        Returns:
            List of extracted lab values
        """
        extraction_prompt = load_prompt("extract")

        # Convert image to base64
        image_b64 = self._image_to_base64(image)

        payload = {
            "inputs": {
                "image": image_b64,
                "text": extraction_prompt
            },
            "parameters": {
                "max_new_tokens": 2048,
                "do_sample": False
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")

            result = response.json()

        # Parse JSON from response
        response_text = result.get("generated_text", "")

        try:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        return []

    async def explain_lab_value(self, test_name: str, value: float, unit: str,
                                 reference_range: str, status: str) -> str:
        """Generate plain English explanation for a lab value."""

        explanation_prompt = load_prompt("explain").format(
            test_name=test_name,
            value=value,
            unit=unit,
            reference_range=reference_range,
            status=status
        )

        payload = {
            "inputs": explanation_prompt,
            "parameters": {
                "max_new_tokens": 256,
                "do_sample": True,
                "temperature": 0.7
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")

            result = response.json()

        return result.get("generated_text", "").replace(explanation_prompt, "").strip()


# Alternative: Use Google AI Studio (Gemini) as fallback
class GeminiClient:
    """
    Fallback client using Google Gemini API.
    MedGemma is based on Gemma, so Gemini can handle similar tasks.
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    async def extract_lab_values(self, image: Image.Image) -> list[dict]:
        """Extract lab values using Gemini."""

        extraction_prompt = load_prompt("extract")
        image_b64 = self._image_to_base64(image)

        payload = {
            "contents": [{
                "parts": [
                    {"text": extraction_prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_b64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "maxOutputTokens": 2048,
                "temperature": 0
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")

            result = response.json()

        # Extract text from response
        response_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        try:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        return []


def get_client():
    """Get the best available client."""
    # Try MedGemma first
    if os.getenv("HF_TOKEN"):
        try:
            return MedGemmaAPIClient()
        except Exception:
            pass

    # Fallback to Gemini
    if os.getenv("GOOGLE_API_KEY"):
        return GeminiClient()

    raise ValueError("No API keys found. Set HF_TOKEN or GOOGLE_API_KEY")


if __name__ == "__main__":
    print("API Client ready. Set HF_TOKEN or GOOGLE_API_KEY environment variable.")
