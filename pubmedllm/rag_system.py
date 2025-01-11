# pubmedllm/rag_system.py
import boto3
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.chat_models import BedrockChat
from langchain_community.vectorstores.pgvector import PGVector
from pubmedllm.config import Config
from pubmedllm.database import Database
from pubmedllm.document_processor import DocumentProcessor
from pubmedllm.pubget_handler import PubgetHandler 
import logging
import os
import hashlib

class PubmedLLM:
    def __init__(self):
        self.bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=Config.AWS_REGION
        )
        
        self.embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v2:0",
            client=self.bedrock_client
        )
        
        self.llm = BedrockChat(
            model_id="amazon.titan-text-lite-v1",
            client=self.bedrock_client,
            model_kwargs={
                "temperature": 0.7,
                "max_tokens": 4096,
            }
        )
        
        # Initialize vector store
        try:
            self.vectorstore = PGVector(
                embedding_function=self.embeddings,
                collection_name=Config.COLLECTION_NAME,
                connection_string=Database.get_connection_string(),
                collection_metadata={"description": "PubMed papers collection"}
            )
        except Exception as e:
            logging.error(f"Error initializing vector store: {str(e)}")
            raise
        
        self.document_processor = DocumentProcessor()
        self.pubget_handler = PubgetHandler(
            email=Config.NCBI_EMAIL,
            api_key=Config.NCBI_API_KEY
        )
    
    def download_and_index_papers(self, query: str, max_results: int = None):
        """Download papers from PubMed and index them"""
        if not query:
            raise ValueError("Query must not be empty")
        
        if max_results is None:
            max_results = Config.DEFAULT_MAX_PAPERS
            
        try:
            # Download papers using pubget
            data_dir = self.pubget_handler.download_papers(query, max_results)
            
            # Get all XML files from the pubget data directory
            xml_files = self._get_xml_files(data_dir)
            
            # Index the downloaded papers
            self.index_documents(xml_files)
            
            return len(xml_files)
            
        except Exception as e:
            logging.error(f"Error in download_and_index_papers: {str(e)}")
            raise

    def _get_xml_files(self, data_dir):
        """Retrieve all XML files from the specified directory"""
        xml_files = []
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file == "article.xml":
                    xml_files.append(os.path.join(root, file))
        return xml_files

    def index_documents(self, file_paths):
        """Index documents into the vector store"""
        for file_path in file_paths:
            logging.info(f"Processing {file_path}")
            try:
                docs = self.document_processor.process_file(file_path)
                
                if docs:
                    texts = [doc.page_content for doc in docs]
                    metadatas = [doc.metadata for doc in docs]
                    ids = [hashlib.sha256(text.encode()).hexdigest() for text in texts]
                    
                    self.vectorstore.add_texts(
                        texts=texts,
                        metadatas=metadatas,
                        ids=ids
                    )
            except Exception as e:
                logging.error(f"Error processing file {file_path}: {str(e)}")

    def query(self, query_text):
        """Query the knowledge base"""
        if not query_text:
            raise ValueError("Query text must not be empty")
        
        try:
            docs = self.vectorstore.similarity_search(
                query_text,
                k=Config.MAX_DOCS_RETURNED
            )
            
            context = "\n\n".join(doc.page_content[:1000] for doc in docs)  # Truncate each document to 1000 characters
            
            prompt = f"""Based on the following context from PubMed papers, please answer this query: {query_text}
            
            Context: {context}
            
            Please provide a detailed answer with specific references to the source material when possible.
            
            Answer:"""
            
            response = self.llm.predict(prompt)
            
            return {
                'query': query_text,
                'result': response,
                'source_documents': docs
            }
        except Exception as e:
            logging.error(f"Error in query: {str(e)}")
            raise