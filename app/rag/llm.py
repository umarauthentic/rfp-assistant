import os
import requests


class OllamaClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise Exception("GROQ_API_KEY not set")

        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "temperature": 0.2,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]