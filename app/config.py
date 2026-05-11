from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="RFP RAG Assistant", alias="APP_NAME")
    env: str = Field(default="local", alias="ENV")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="phi3:mini", alias="OLLAMA_MODEL")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")

    top_k_docs: int = Field(default=4, alias="TOP_K_DOCS")
    top_k_qa: int = Field(default=3, alias="TOP_K_QA")
    min_qa_score: float = Field(default=0.55, alias="MIN_QA_SCORE")

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
    settings = Settings()
    settings.documents_dir.mkdir(parents=True, exist_ok=True)
    settings.qa_memory_dir.mkdir(parents=True, exist_ok=True)
    settings.vector_path.mkdir(parents=True, exist_ok=True)
    return settings
