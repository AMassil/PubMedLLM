# pubmedllm/config.py
from dotenv import load_dotenv
import os

load_dotenv()

def env(name: str, default: str = "") -> str:
    """Return a stripped environment value, falling back when it is empty."""
    return os.getenv(name, default).strip() or default

class Config:
    # Database configuration
    DB_USER = env("DB_USER", "postgres")
    DB_PASSWORD = env("DB_PASSWORD", "pubmedllm")
    DB_HOST = env("DB_HOST", "localhost")
    DB_PORT = env("DB_PORT", "5432")
    DB_NAME = env("DB_NAME", "pubmedllm")
    
    # AWS configuration
    AWS_REGION = env("AWS_DEFAULT_REGION", "us-east-1")
    EMBEDDING_MODEL_ID = env(
        "BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0"
    )
    CHAT_MODEL_ID = env("BEDROCK_CHAT_MODEL_ID", "amazon.nova-lite-v1:0")
    
    # Vector store configuration
    COLLECTION_NAME = "pubmed_papers"
    MAX_DOCS_RETURNED = int(env("MAX_DOCS_RETURNED", "8"))
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150
    NCBI_API_KEY = env("NCBI_API_KEY") or None
    NCBI_EMAIL = env("NCBI_EMAIL")
    DEFAULT_MAX_PAPERS = 20