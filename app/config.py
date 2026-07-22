from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    openai_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o"
    officecli_path: str = "bin/officecli.exe"
    output_dir: str = "output"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
