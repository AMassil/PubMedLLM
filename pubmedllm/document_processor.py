import hashlib
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredXMLLoader
import logging
from typing import List
from pydantic import BaseModel
from pubmedllm.config import Config

logger = logging.getLogger(__name__)

class DocumentMetadata(BaseModel):
    """Standardized document metadata model"""
    pmid: str = "unknown"
    source_file: str
    chunk_index: int
    total_chunks: int

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = CharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )

    def process_file(self, file_path: str) -> List[dict]:
        """
        Process a document file (PDF or XML) into chunks with metadata
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of document chunks with metadata
        """
        try:
            if file_path.endswith('.pdf'):
                return self._process_pdf(file_path)
            elif file_path.endswith('.xml'):
                return self._process_xml(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}. Only .pdf and .xml files are supported.")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return []

    def _process_pdf(self, file_path: str) -> List[dict]:
        """Process a PDF document"""
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        chunks = self.text_splitter.split_documents(pages)
        
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            metadata = DocumentMetadata(
                source_file=file_path,
                chunk_index=i,
                total_chunks=len(chunks)
            )
            processed_chunks.append({
                'content': chunk.page_content,
                'metadata': metadata.dict()
            })
            
        return processed_chunks

    def _process_xml(self, file_path: str) -> List[dict]:
        """Process an XML document with PMID extraction"""
        loader = UnstructuredXMLLoader(file_path)
        docs = loader.load()
        
        # Extract PMID from XML
        pmid = self._extract_pmid_from_file(file_path)
        
        chunks = self.text_splitter.split_documents(docs)
        processed_chunks = []
        
        for i, chunk in enumerate(chunks):
            metadata = DocumentMetadata(
                pmid=pmid,
                source_file=file_path,
                chunk_index=i,
                total_chunks=len(chunks)
            )
            processed_chunks.append({
                'content': chunk.page_content,
                'metadata': metadata.dict()
            })
            
        return processed_chunks

    def _extract_pmid_from_file(self, file_path: str) -> str:
        """
        Extract PMID from XML file content
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            Extracted PMID or 'unknown' if not found
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
                return self._extract_pmid_from_xml(xml_content)
        except Exception as e:
            logger.warning(f"Couldn't extract PMID from {file_path}: {str(e)}")
            return "unknown"

    def _extract_pmid_from_xml(self, xml_content: str) -> str:
        """
        Extract PMID from XML content string
        
        Args:
            xml_content: String containing XML content
            
        Returns:
            Extracted PMID or 'unknown' if not found
        """
        try:
            start_tag = '<article-id pub-id-type="pmid">'
            end_tag = '</article-id>'
            start = xml_content.find(start_tag)
            if start == -1:
                return "unknown"
            start += len(start_tag)
            end = xml_content.find(end_tag, start)
            return xml_content[start:end].strip()
        except Exception as e:
            logger.warning(f"PMID extraction failed: {str(e)}")
            return "unknown"
