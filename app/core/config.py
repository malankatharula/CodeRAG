from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_MODEL: str = "llama3.2:3b"
    EMBED_MODEL: str = "nomic-embed-text"
    CHROMA_PATH: str = "./chroma_db"
    GROQ_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
