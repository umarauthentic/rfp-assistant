from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    app_name: str = Field(default="RFP RAG Assistant", alias="APP_NAME")
    env: str = Field(default="local", alias="ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8001, alias="APP_PORT")
    app_password: str | None = Field(default=None, alias="APP_PASSWORD")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2", alias="OLLAMA_MODEL")
    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")

    top_k_docs: int = Field(default=8, alias="TOP_K_DOCS")
    top_k_qa: int = Field(default=3, alias="TOP_K_QA")
    min_qa_score: float = Field(default=0.55, alias="MIN_QA_SCORE")
    min_doc_score: float = Field(default=0.15, alias="MIN_DOC_SCORE")

    data_dir: str = Field(default="data", alias="DATA_DIR")
    vector_dir: str = Field(default="vector_store", alias="VECTOR_DIR")

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def documents_dir(self) -> Path:
        return Path(self.data_dir) / "documents"

    @property
    def qa_memory_dir(self) -> Path:
        return Path(self.data_dir) / "qa_memory"

    @property
    def vector_path(self) -> Path:
        return Path(self.vector_dir)


@lru_cache
def get_settings() -> Settings:
    load_dotenv(override=True)
    settings = Settings()
    settings.documents_dir.mkdir(parents=True, exist_ok=True)
    settings.qa_memory_dir.mkdir(parents=True, exist_ok=True)
    settings.vector_path.mkdir(parents=True, exist_ok=True)
    return settings
