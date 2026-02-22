import os

from google import genai
from google.genai import types

class GeminiModelClient:
    def __init__(self, model_name: str = "gemini-3-flash-preview") -> None:
        self.model_name = model_name
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def generate(self, prompt: str, file_text: str) -> str:
        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=file_text,
            config=types.GenerateContentConfig(
                system_instruction=prompt
            ),
        )
        return resp.text or ""
