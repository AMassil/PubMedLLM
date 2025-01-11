# pubmedllm/config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Database configuration
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "postgres")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "pubmedllm")
    
    # AWS configuration
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    # Vector store configuration
    COLLECTION_NAME = "pubmed_papers"
    MAX_DOCS_RETURNED = 50
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 0
    NCBI_API_KEY = os.getenv("NCBI_API_KEY")
    NCBI_EMAIL = os.getenv("NCBI_EMAIL", "your@email.com")
    DEFAULT_MAX_PAPERS = 1000