# pubmedllm/pubget_handler.py
import hashlib
import logging
from pathlib import Path
from Bio import Entrez
from typing import Any, Optional, cast

logger = logging.getLogger(__name__)

class PubgetHandler:
    def __init__(self, email: str, api_key: Optional[str] = None):
        """
        Initialize PubgetHandler
        
        Args:
            email: Email address for NCBI
            api_key: NCBI API key (optional but recommended)
        """
        self.email = email.strip()
        Entrez.email = self.email
        if api_key:
            Entrez.api_key = api_key
        
    def download_papers(self, query: str, max_results: int = 10) -> str:
        """Download open-access PMC full text without the obsolete pubget CLI."""
        if not query.strip():
            raise ValueError("Query must not be empty")
        if max_results < 1:
            raise ValueError("max_results must be positive")
        if not self.email:
            raise ValueError("NCBI_EMAIL must contain a valid contact email")

        query_id = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
        output_dir = Path("data/pubget_data") / f"query_{query_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            logger.info("Searching PubMed Central: %s", query)
            with Entrez.esearch(db="pmc", term=query, retmax=max_results) as handle:
                search_result = cast(dict[str, Any], Entrez.read(handle))

            ids = search_result.get("IdList", [])
            if not ids:
                raise RuntimeError("No open-access article found in PubMed Central")

            downloaded = 0
            for pmcid in ids:
                article_dir = output_dir / f"pmcid_{pmcid}"
                destination = article_dir / "article.xml"
                if destination.exists() and destination.stat().st_size:
                    downloaded += 1
                    continue
                article_dir.mkdir(parents=True, exist_ok=True)
                try:
                    with Entrez.efetch(db="pmc", id=pmcid, retmode="xml") as handle:
                        payload = handle.read()
                    if isinstance(payload, str):
                        payload = payload.encode("utf-8")
                    destination.write_bytes(payload)
                    downloaded += 1
                except Exception as exc:
                    logger.warning("Could not download PMC%s: %s", pmcid, exc)

            if downloaded == 0:
                raise RuntimeError("PMC returned results, but no full text could be downloaded")
            logger.info("Downloaded %d article(s) to %s", downloaded, output_dir)
            return str(output_dir)
        except Exception as e:
            logger.error("Error downloading papers: %s", e)
            raise

    def get_paper_metadata(self, pmid: str) -> dict:
        try:
            with Entrez.efetch(db="pubmed", id=pmid, rettype="xml") as handle:
                record = cast(dict[str, Any], Entrez.read(handle))
            article = record['PubmedArticle'][0]
            
            metadata = {
                'pmid': pmid,
                'title': article['MedlineCitation']['Article'].get('ArticleTitle', ''),
                'authors': [],
                'journal': '',
                'year': ''
            }
            
            if 'AuthorList' in article['MedlineCitation']['Article']:
                metadata['authors'] = [
                    author.get('LastName', '') + ' ' + author.get('ForeName', '')
                    for author in article['MedlineCitation']['Article']['AuthorList']
                ]
            
            if 'Journal' in article['MedlineCitation']['Article']:
                journal = article['MedlineCitation']['Article']['Journal']
                metadata['journal'] = journal.get('Title', '')
                if 'JournalIssue' in journal and 'PubDate' in journal['JournalIssue']:
                    metadata['year'] = journal['JournalIssue']['PubDate'].get('Year', '')
            
            return metadata
        except Exception as e:
            logger.error(f"Error fetching metadata for PMID {pmid}: {str(e)}")
            return {'pmid': pmid}