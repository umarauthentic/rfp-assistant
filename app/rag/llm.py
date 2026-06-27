import requests

from app.config import get_settings


class ChatCompletionsClient:
    def __init__(self, api_key: str | None, url: str, model: str, api_key_name: str):
        self.api_key = api_key

        if not self.api_key:
            raise Exception(f"{api_key_name} not set")

        self.url = url
        self.model = model

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
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


class OpenAIClient(ChatCompletionsClient):
    def __init__(self):
        settings = get_settings()
        super().__init__(
            api_key=settings.openai_api_key,
            url="https://api.openai.com/v1/chat/completions",
            model=settings.openai_model,
            api_key_name="OPENAI_API_KEY",
        )


class OllamaClient:
    def __init__(self):
        settings = get_settings()
        self.url = settings.ollama_base_url.rstrip("/") + "/api/chat"
        self.model = settings.ollama_model

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": 0.2,
                },
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]


def get_llm_client():
    settings = get_settings()
    provider = settings.llm_provider.lower().strip()

    if provider == "ollama":
        return OllamaClient()
    if provider == "openai":
        return OpenAIClient()

    raise Exception(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
