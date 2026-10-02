# PubMedLLM

Python RAG pipeline for downloading **open-access full-text** articles from
PubMed Central (PMC), splitting them, indexing them in PostgreSQL/pgvector, and
querying them with Amazon Bedrock.

## Architecture

1. Biopython searches PMC and downloads the JATS XML for open-access articles.
2. Title, abstract, and body text are extracted and split into chunks.
3. Amazon Titan generates embeddings stored in pgvector.
4. Amazon Nova answers only from retrieved passages and cites `[Source N]`.

PubMed and PMC are not the same: downloads target PMC because PubMed mainly
contains bibliographic records and does not guarantee full text.

## Requirements

- Python 3.10 or newer;
- Docker with Compose for PostgreSQL;
- an AWS account authorized to call Bedrock and the configured models;
- a contact email address for NCBI requests.

## Configuration

Copy `.env.example` to `.env`, then replace at least `NCBI_EMAIL`. For AWS,
prefer a local profile, temporary credentials, or an IAM role instead of storing
long-lived keys in `.env`.

Models can be changed with `BEDROCK_EMBEDDING_MODEL_ID` and
`BEDROCK_CHAT_MODEL_ID`. The default region is `us-east-1`.

> A former plaintext AWS key was removed from the archived project. Revoke it
> in IAM if it is still active.

## Recommended Local Setup

Create the Python environment and install dependencies:

	python3 -m venv .venv
	.venv/bin/python -m pip install -r requirements.txt

Start only the pgvector database:

	docker compose up -d postgres

Download and index up to five PMC articles:

	.venv/bin/python -m pubmedllm.main download-index "rheumatoid arthritis AND T cells" --max-results 5

Then ask a question:

	.venv/bin/python -m pubmedllm.main query "What is the role of T cells?"

You can also index local JATS XML or PDF files:

	.venv/bin/python -m pubmedllm.main index data/xml/article.xml data/pdfs/article.pdf

## Running Entirely in Docker

The `app` profile prevents an application container from starting automatically
and exiting after displaying the help message. Run each command explicitly:

	docker compose --profile app run --rm pubmedllm download-index "cancer immunotherapy" --max-results 5
	docker compose --profile app run --rm pubmedllm query "What results are reported?"

In this mode, provide AWS credentials to Compose through the environment.
`AWS_SESSION_TOKEN` is supported for temporary credentials.

## Tests and Diagnostics

The offline test suite does not call AWS, NCBI, or PostgreSQL:

	.venv/bin/python -m unittest discover -v

Useful commands:

	docker compose ps
	docker compose logs postgres
	.venv/bin/python -m pubmedllm.main --help

Common errors:

- `NCBI_EMAIL must contain...`: set `NCBI_EMAIL` in `.env`;
- Bedrock credential errors: check the AWS profile/role and region;
- unauthorized model: enable model access or change the model identifier;
- PostgreSQL connection refused: check that the `postgres` service is healthy;
- no article found: broaden the query, which only targets the open-access PMC
	corpus.
