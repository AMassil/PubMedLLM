# pubmedllm/document_processor.py
import hashlib
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredXMLLoader
import logging
from pubmedllm.config import Config

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = CharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )

    def process_file(self, file_path):
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

    def _process_pdf(self, file_path):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        return self.text_splitter.split_documents(pages)

    def _process_xml(self, file_path):
        loader = UnstructuredXMLLoader(file_path)
        return loader.load_and_split()