# pubmedllm/pubget_handler.py
import os
import subprocess
import logging
from pathlib import Path
from Bio import Entrez
from typing import List, Optional

logger = logging.getLogger(__name__)

class PubgetHandler:
    def __init__(self, email: str, api_key: Optional[str] = None):
        """
        Initialize PubgetHandler
        
        Args:
            email: Email address for NCBI
            api_key: NCBI API key (optional but recommended)
        """
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
        
    def download_papers(self, query: str, max_results: int = 10) -> str:
        output_dir = Path("data/pubget_data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Run pubget command
            cmd = [
                "pubget", "run",
                "-q", query,
                "-n", str(max_results),
                str(output_dir)
            ]
            
            logger.info(f"Running pubget with query: {query}")
            with open("pubget_log.txt", "w") as log_file:
                result = subprocess.run(cmd, stdout=log_file, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                logger.error(f"Pubget error: {result.stderr}")
                raise Exception(f"Pubget failed with error: {result.stderr}")
                
            logger.info(f"Successfully downloaded papers to {output_dir}")
            return str(output_dir)
            
        except Exception as e:
            logger.error(f"Error downloading papers: {str(e)}")
            raise

    def get_paper_metadata(self, pmid: str) -> dict:
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml")
            record = Entrez.read(handle)
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