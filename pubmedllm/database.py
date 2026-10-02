# pubmedllm/database.py
import psycopg
from pubmedllm.config import Config
from urllib.parse import quote

class Database:
    @staticmethod
    def get_connection_string() -> str:
        """Return the SQLAlchemy URL expected by langchain-postgres."""
        user = quote(Config.DB_USER, safe="")
        password = quote(Config.DB_PASSWORD or "", safe="")
        return (
            f"postgresql+psycopg://{user}:{password}@{Config.DB_HOST}:"
            f"{Config.DB_PORT}/{Config.DB_NAME}"
        )

    @staticmethod
    def get_psycopg_connection_string() -> str:
        user = quote(Config.DB_USER, safe="")
        password = quote(Config.DB_PASSWORD or "", safe="")
        return (
            f"postgresql://{user}:{password}@{Config.DB_HOST}:"
            f"{Config.DB_PORT}/{Config.DB_NAME}"
        )
    
    @staticmethod
    def ensure_ready() -> None:
        """Check the database and install pgvector before creating the store."""
        with psycopg.connect(Database.get_psycopg_connection_string()) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")