from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """Application configuration settings."""

    # LLM Settings
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    llm_provider: str = Field(default="openai", description="LLM provider: 'openai' or 'anthropic'")
    llm_model: str = Field(default="gpt-4", description="Model name to use")
    llm_temperature: float = Field(default=0.0, description="Temperature for LLM")
    llm_timeout: int = Field(default=30, description="Timeout in seconds for LLM calls")

    # Algorithm Settings
    algorithm_order: List[str] = Field(
        default=["length_check", "keyword_check"],
        description="Order of algorithm execution"
    )

    # Criteria Documents Path
    criteria_path: str = Field(default="src/criteria", description="Path to criteria documents")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_judge_reasoning: bool = Field(default=True, description="Log Judge reasoning process")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
