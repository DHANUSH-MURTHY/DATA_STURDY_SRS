"""
Configuration module — loads environment variables and provides app-wide settings.
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


class Settings:
    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password123")

    # App
    # Force DEMO_MODE off if using Ollama, otherwise default to False
    _demo_default = "false" if LLM_PROVIDER == "ollama" else "true"
    DEMO_MODE: bool = os.getenv("DEMO_MODE", _demo_default).lower() == "true"
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    # Cohort
    DEFAULT_COHORT: list[str] = [
        "Infosys", "TCS", "Wipro", "HCLTech", "Accenture"
    ]


settings = Settings()
