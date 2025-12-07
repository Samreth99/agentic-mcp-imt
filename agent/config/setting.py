from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

class Settings:
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY : str | None = os.getenv("OPENAI_API_KEY")

settings = Settings()

# if __name__ == "__main__":
#     print("GROQ_API_KEY loaded?", settings.GROQ_API_KEY is not None)
