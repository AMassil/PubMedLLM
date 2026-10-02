# pubmedllm/rag_system.py
from langchain_aws import BedrockEmbeddings, ChatBedrockConverse
from langchain_postgres import PGVector
from pubmedllm.config import Config
from pubmedllm.database import Database
from pubmedllm.document_processor import DocumentProcessor
from pubmedllm.pubget_handler import PubgetHandler 
import logging
import os
import hashlib

logger = logging.getLogger(__name__)

class PubmedLLM:
    def __init__(self, embeddings=None, llm=None, vectorstore=None):
        self.embeddings = embeddings or BedrockEmbeddings(
            model_id=Config.EMBEDDING_MODEL_ID,
            region_name=Config.AWS_REGION,
        )
        self.llm = llm or ChatBedrockConverse(
            model=Config.CHAT_MODEL_ID,
            region_name=Config.AWS_REGION,
            temperature=0.2,
            max_tokens=2048,
        )

        if vectorstore is not None:
            self.vectorstore = vectorstore
        else:
            Database.ensure_ready()
            self.vectorstore = PGVector(
                embeddings=self.embeddings,
                collection_name=Config.COLLECTION_NAME,
                connection=Database.get_connection_string(),
                use_jsonb=True,
            )
        
        self.document_processor = DocumentProcessor()
        self.pubget_handler = PubgetHandler(
            email=Config.NCBI_EMAIL,
            api_key=Config.NCBI_API_KEY
        )
    
    def download_and_index_papers(self, query: str, max_results: int | None = None):
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
            indexed_chunks = self.index_documents(xml_files)
            if indexed_chunks == 0:
                raise RuntimeError("Articles were downloaded, but no text could be indexed")
            
            return len(xml_files)
            
        except Exception as e:
            logger.error("Error in download_and_index_papers: %s", e)
            raise

    def _get_xml_files(self, data_dir):
        """Retrieve all XML files from the specified directory"""
        xml_files = []
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file == "article.xml":
                    xml_files.append(os.path.join(root, file))
        return xml_files

    def index_documents(self, file_paths) -> int:
        """Index documents into the vector store"""
        indexed = 0
        for file_path in file_paths:
            logger.info("Processing %s", file_path)
            try:
                docs = self.document_processor.process_file(file_path)
                if docs:
                    ids = [
                        hashlib.sha256(
                            f"{file_path}:{chunk_index}:{doc.page_content}".encode("utf-8")
                        ).hexdigest()
                        for chunk_index, doc in enumerate(docs)
                    ]
                    self.vectorstore.add_documents(docs, ids=ids)
                    indexed += len(docs)
            except Exception as e:
                logger.error("Error processing file %s: %s", file_path, e)
        return indexed

    def query(self, query_text):
        """Query the knowledge base"""
        if not query_text:
            raise ValueError("Query text must not be empty")
        
        try:
            docs = self.vectorstore.similarity_search(
                query_text,
                k=Config.MAX_DOCS_RETURNED
            )
            
            if not docs:
                return {"query": query_text, "result": "No relevant document was found.", "source_documents": []}

            context_parts = []
            for number, doc in enumerate(docs, start=1):
                title = doc.metadata.get("title") or doc.metadata.get("source", "Unknown source")
                context_parts.append(f"[Source {number}: {title}]\n{doc.page_content}")
            context = "\n\n".join(context_parts)

            messages = [
                ("system", "You answer only from the supplied biomedical sources. Cite sources as [Source N]. If the evidence is insufficient, say so explicitly."),
                ("human", f"Question: {query_text}\n\nSources:\n{context}"),
            ]
            response = self.llm.invoke(messages)
            text = getattr(response, "text", None)
            if isinstance(text, str) and text:
                result = text
            else:
                content = getattr(response, "content", response)
                result = content if isinstance(content, str) else str(content)
            
            return {
                'query': query_text,
                'result': result,
                'source_documents': docs
            }
        except Exception as e:
            logger.error("Error in query: %s", e)
            raise