import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")  # Updated default
    BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "True").lower() == "true"
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
settings = Settings()