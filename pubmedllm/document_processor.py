# pubmedllm/document_processor.py
import logging
from pathlib import Path
import xml.etree.ElementTree as ET

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from pubmedllm.config import Config

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def process_file(self, file_path: str) -> list[Document]:
        path = Path(file_path)
        try:
            if path.suffix.lower() == ".pdf":
                documents = self._process_pdf(path)
            elif path.suffix.lower() == ".xml":
                documents = self._process_xml(path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}. Only .pdf and .xml files are supported.")
            return self.text_splitter.split_documents(documents)
        except Exception as e:
            logger.error("Error processing %s: %s", file_path, e)
            return []

    @staticmethod
    def _process_pdf(file_path: Path) -> list[Document]:
        reader = PdfReader(file_path)
        documents = []
        for page_number, page in enumerate(reader.pages, start=1):
            content = page.extract_text() or ""
            if content.strip():
                documents.append(Document(
                    page_content=content,
                    metadata={"source": str(file_path), "page": page_number},
                ))
        return documents

    @staticmethod
    def _process_xml(file_path: Path) -> list[Document]:
        root = ET.parse(file_path).getroot()
        article = root.find(".//article") if root.tag != "article" else root
        if article is None:
            raise ValueError("No <article> element found")

        def text(xpath: str) -> str:
            element = article.find(xpath)
            return " ".join("".join(element.itertext()).split()) if element is not None else ""

        title = text(".//article-title")
        abstract = text(".//abstract")
        body = text(".//body")
        content = "\n\n".join(part for part in (title, abstract, body) if part)
        if not content:
            raise ValueError("The article contains no extractable text")

        pmcid = text(".//article-id[@pub-id-type='pmcid']") or text(
            ".//article-id[@pub-id-type='pmc']"
        )
        pmid = text(".//article-id[@pub-id-type='pmid']")
        return [Document(page_content=content, metadata={
            "source": str(file_path),
            "title": title,
            "pmcid": pmcid,
            "pmid": pmid,
        })]