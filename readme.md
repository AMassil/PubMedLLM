# PubmedLLM

PubmedLLM is a powerful tool that combines PubMed paper retrieval with Large Language Models (LLMs) to enable intelligent querying of scientific literature. It uses AWS Bedrock for LLM capabilities and PostgreSQL for vector storage.

## Features

- Automated paper downloading from PubMed using Pubget
- PDF and XML document processing
- Vector embedding storage in PostgreSQL
- Intelligent querying using AWS Bedrock
- Docker-based deployment for easy setup

## Prerequisites

- Docker and Docker Compose
- AWS Account with Bedrock access
- NCBI API key for PubMed access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PubmedLLM.git
cd PubmedLLM
```

2. Create a `.env` file with your credentials:
```env
DB_USER=postgres
DB_PASSWORD=your_password_
DB_HOST=pubmedllm_db
DB_PORT=5432 
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-east-1
NCBI_API_KEY=your_ncbi_api_key
NCBI_EMAIL=your@email.com
```

3. Build and start the services:
```bash
docker-compose up --build
```

## Project Structure

```
PubmedLLM/
├── docker-compose.yml        # Docker compose configuration
├── Dockerfile               # Docker build instructions
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables
├── pubmedllm/              # Main package directory
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database operations
│   ├── document_processor.py # Document processing logic
│   ├── pubget_handler.py   # PubMed paper retrieval
│   ├── rag_system.py       # Main RAG implementation
│   └── main.py            # Entry point
└── data/                   # Data directory
    ├── pdfs/              # PDF papers
    ├── xml/               # XML papers
    └── pubget_data/       # Downloaded PubMed papers
```

## Usage

### Basic Usage

1. Start the system:
```bash
docker-compose up -d
```

2. Download and process papers:
```python
from pubmedllm.rag_system import PubmedLLM

# Initialize the system
pubmed_llm = PubmedLLM()

# Download papers about rheumatoid arthritis
query = "((rheumatoid arthritis) AND gene) AND cell"
pubmed_llm.download_and_index_papers(query, max_results=1000)
```

3. Query the papers:
```python
# Ask a question about the papers
result = pubmed_llm.query("Tell me about T cell–derived cytokines in rheumatoid arthritis")
print(result['result'])
```

### Example Queries

```python
queries = [
    "Tell me about T cell–derived cytokines in relation to rheumatoid arthritis",
    "Tell me about single-cell research in rheumatoid arthritis",
    "Tell me about protein-protein associations in rheumatoid arthritis",
]

for query in queries:
    result = pubmed_llm.query(query)
    print(f"\nQuery: {result['query']}")
    print(f"Answer: {result['result']}")
```

## Configuration

You can configure the system by modifying the following files:

- `.env`: Environment variables and API keys
- `pubmedllm/config.py`: System configuration settings
- `docker-compose.yml`: Docker service configuration

### Important Configuration Options

```python
# In config.py
class Config:
    # Vector store configuration
    COLLECTION_NAME = "pubmed_papers"
    MAX_DOCS_RETURNED = 50
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 0
    
    # Pubget configuration
    DEFAULT_MAX_PAPERS = 1000
```

## Database Management

The system uses PostgreSQL with pgvector for storing document embeddings. The database is automatically initialized when you start the Docker containers.

To access the database directly:
```bash
docker-compose exec postgres psql -U postgres -d pubmedllm
```

## Troubleshooting

### Common Issues

1. AWS Bedrock Access
```
Error: AccessDeniedException
Solution: Ensure your AWS credentials have the necessary permissions for Bedrock.
```

2. Database Connection
```
Error: Could not connect to PostgreSQL
Solution: Check if the postgres container is running and the credentials are correct.
```

3. Pubget Download Issues
```
Error: Failed to download papers
Solution: Verify your NCBI API key and internet connection.
```

## Development

To contribute to PubmedLLM:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Running Tests

```bash
# Inside the container
python -m pytest tests/
```


