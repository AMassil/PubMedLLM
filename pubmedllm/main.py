import argparse
import logging
from pathlib import Path
from pubmedllm.rag_system import PubmedLLM

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger().setLevel(logging.INFO)  # Set root logger level

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Download, index and query open-access PubMed Central papers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    download_parser = subparsers.add_parser("download-index", help="Download PMC papers and index them")
    download_parser.add_argument("query", help="PMC search query")
    download_parser.add_argument("--max-results", type=int, default=None)

    index_parser = subparsers.add_parser("index", help="Index local XML or PDF files")
    index_parser.add_argument("paths", nargs="+", type=Path)

    query_parser = subparsers.add_parser("query", help="Ask a question using indexed papers")
    query_parser.add_argument("question")

    args = parser.parse_args()

    if args.command == "download-index":
        pubmed_llm = PubmedLLM()
        count = pubmed_llm.download_and_index_papers(args.query, args.max_results)
        print(f"Downloaded and indexed {count} article(s).")
    elif args.command == "index":
        invalid = [path for path in args.paths if path.suffix.lower() not in {".xml", ".pdf"}]
        missing = [path for path in args.paths if not path.is_file()]
        if invalid:
            parser.error(f"unsupported file type: {invalid[0]}")
        if missing:
            parser.error(f"file not found: {missing[0]}")
        files = [str(path) for path in args.paths]
        pubmed_llm = PubmedLLM()
        count = pubmed_llm.index_documents(files)
        print(f"Indexed {count} chunk(s) from {len(files)} file(s).")
    else:
        pubmed_llm = PubmedLLM()
        result = pubmed_llm.query(args.question)
        print(result["result"])

if __name__ == "__main__":
    main()