import logging
from pathlib import Path
import glob
from pubmedllm.rag_system import PubmedLLM

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger().setLevel(logging.INFO)  # Set root logger level

def main():
    setup_logging()
    
    # Initialize PubmedLLM system
    pubmed_llm = PubmedLLM()
    
    # Example: Download and index papers about autoimmune diseases
    query = "((autoimmune diseases) AND inflammation) AND therapy"
    try:
        num_papers = pubmed_llm.download_and_index_papers(query, max_results=1000)
        print(f"Successfully downloaded and indexed {num_papers} papers")
        
        # Example queries
        queries = [
            "What is the impact of microbiota on immune system modulation?",
            "How do biologics target specific pathways in psoriasis treatment?",
            "What are the latest findings on CAR-T cell therapy for cancer?",
        ]
        
        # Run queries and display results
        for query in queries:
            result = pubmed_llm.query(query)
            print(f"\nQuery: {result['query']}")
            print(f"Answer: {result['result']}")
            print(f"Number of source documents: {len(result['source_documents'])}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
