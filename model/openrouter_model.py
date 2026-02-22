import os

from openai import OpenAI


class OpenRouterModelClient:
    def __init__(
        self,
        model_name: str = "stepfun/step-3.5-flash:free",
        base_url: str = "https://openrouter.ai/api/v1",
    ) -> None:
        self.model_name = model_name
        self.client = OpenAI(
            base_url=base_url,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    def generate(self, prompt: str, file_text: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": file_text},
            ],
        )
        return response.choices[0].message.content or ""
