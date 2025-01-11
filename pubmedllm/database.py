# pubmedllm/database.py
import psycopg
from langchain_community.vectorstores.pgvector import PGVector
from pubmedllm.config import Config
from sqlalchemy import create_engine

class Database:
    @staticmethod
    def get_connection_string():
        return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    
    @staticmethod
    def create_connection():
        with psycopg.connect(Database.get_connection_string()) as conn:
            # Create pgvector extension if it doesn't exist
            with conn.cursor() as cur:
                cur.execute('CREATE EXTENSION IF NOT EXISTS vector;')
                conn.commit()
            return conn