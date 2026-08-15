\# Enterprise RAG



A containerized Retrieval-Augmented Generation (RAG) system for uploading, processing, embedding, and querying documents using semantic search and a local Large Language Model.



The project provides a modular foundation for document-based AI applications where users can upload documents and ask natural-language questions about their content.



\---



\## Features



\* Document upload

\* PDF document processing

\* Text extraction and document ingestion

\* Document chunking

\* Vector embeddings

\* Semantic similarity search

\* Retrieval-Augmented Generation (RAG)

\* Local LLM inference with Ollama

\* PostgreSQL database with pgvector

\* REST API built with FastAPI

\* Docker-based development environment

\* Environment-based configuration

\* Health-check endpoints

\* Document-specific querying

\* Retrieval from multiple document chunks

\* Context-aware answer generation



\---



\## Architecture



The application follows a modular RAG architecture:



```text

&#x20;                        ┌──────────────────┐

&#x20;                        │      Client      │

&#x20;                        └────────┬─────────┘

&#x20;                                 │

&#x20;                                 ▼

&#x20;                        ┌──────────────────┐

&#x20;                        │     FastAPI      │

&#x20;                        │       API        │

&#x20;                        └────────┬─────────┘

&#x20;                                 │

&#x20;            ┌────────────────────┼────────────────────┐

&#x20;            │                    │                    │

&#x20;            ▼                    ▼                    ▼

&#x20;         Upload                Ingest               Query

&#x20;            │                    │                    │

&#x20;            │                    ▼                    │

&#x20;            │              Text Extraction           │

&#x20;            │                    │                    │

&#x20;            │                    ▼                    │

&#x20;            │                Chunking                │

&#x20;            │                    │                    │

&#x20;            │                    ▼                    │

&#x20;            │               Embeddings               │

&#x20;            │                    │                    │

&#x20;            │                    ▼                    │

&#x20;            │             PostgreSQL +                │

&#x20;            │               pgvector                  │

&#x20;            │                         ▲               │

&#x20;            │                         │               │

&#x20;            │                  Vector Search ◄────────┘

&#x20;            │                         │

&#x20;            │                         ▼

&#x20;            │                      Context

&#x20;            │                         │

&#x20;            │                         ▼

&#x20;            │                       Ollama

&#x20;            │                         │

&#x20;            │                         ▼

&#x20;            └────────────────────►  Answer

```



\### RAG Pipeline



A document follows this processing pipeline:



```text

Document

&#x20;  │

&#x20;  ▼

Upload

&#x20;  │

&#x20;  ▼

Ingest

&#x20;  │

&#x20;  ├── Text extraction

&#x20;  ├── Page processing

&#x20;  └── Chunk creation

&#x20;  │

&#x20;  ▼

Embed

&#x20;  │

&#x20;  └── Vector embeddings

&#x20;  │

&#x20;  ▼

PostgreSQL + pgvector

&#x20;  │

&#x20;  ▼

Semantic Search

&#x20;  │

&#x20;  ▼

Relevant Context

&#x20;  │

&#x20;  ▼

Ollama / LLM

&#x20;  │

&#x20;  ▼

Generated Answer

```



\---



\## Technology Stack



| Technology        | Purpose                              |

| ----------------- | ------------------------------------ |

| Python            | Application development              |

| FastAPI           | REST API                             |

| PostgreSQL        | Relational database                  |

| pgvector          | Vector storage and similarity search |

| Ollama            | Local LLM inference                  |

| Qwen3 4B Instruct | Default language model               |

| Docker            | Containerization                     |

| Docker Compose    | Local service orchestration          |



\---



\## Project Structure



The project is organized as follows:



```text

enterprise-rag/

│

├── app/

│   ├── api/

│   ├── llm/

│   │   └── ollama.py

│   └── ...

│

├── test\_documents/

│   └── Document de proiect al unei firme.pdf

│

├── uploads/

│

├── .env

├── .env.example

├── .gitignore

├── docker-compose.yml

├── Dockerfile

├── requirements.txt

└── README.md

```



The project structure may evolve as additional functionality is added.



\---



\# Configuration



The application uses environment variables for configuration.



Create a local `.env` file based on `.env.example`.



\### Example configuration



```env

OLLAMA\_URL=http://host.docker.internal:11434

OLLAMA\_MODEL=qwen3:4b-instruct

```



\### Ollama Configuration



`OLLAMA\_URL` specifies the HTTP endpoint used by the API container to communicate with Ollama.



When Ollama is running directly on the host machine and the API is running inside Docker, the following configuration is used:



```env

OLLAMA\_URL=http://host.docker.internal:11434

```



`11434` is the default HTTP port used by Ollama.



`host.docker.internal` allows a Docker container to communicate with the host machine.



`OLLAMA\_MODEL` specifies the language model used by the application:



```env

OLLAMA\_MODEL=qwen3:4b-instruct

```



These values are configuration parameters and do not contain secrets.



\---



\## Environment Variables and Secrets



The real `.env` file should \*\*not\*\* be committed to GitHub.



Sensitive values such as:



\* database passwords

\* API keys

\* access tokens

\* secret keys



should remain in `.env` and be excluded through `.gitignore`.



The `.env.example` file is safe to commit and provides the configuration structure required to run the application.



Before pushing the project to a public repository, make sure that no credentials or other sensitive information are present in tracked files.



\---



\# Running the Project



\## Prerequisites



Make sure the following software is installed:



\* Docker

\* Docker Compose

\* Ollama



The required Ollama model must also be available locally.



For the default configuration:



```bash

ollama pull qwen3:4b-instruct

```



Verify the model:



```bash

ollama list

```



\---



\## Start the Application



From the project root directory:



```bash

docker compose up --build

```



The API will be available at:



```text

http://localhost:8000

```



\---



\## Stop the Application



```bash

docker compose down

```



\---



\## View Logs



```bash

docker compose logs -f

```



\---



\# API



\## Health Check



```http

GET /health

```



Checks whether the API is running.



Example:



```bash

curl.exe http://localhost:8000/health

```



\---



\## Database Health Check



```http

GET /health/db

```



Checks database connectivity.



Example:



```bash

curl.exe http://localhost:8000/health/db

```



\---



\## Upload Document



```http

POST /documents/upload

```



Uploads a document to the application.



Example:



```bash

curl.exe -X POST "http://localhost:8000/documents/upload" ^

&#x20; -F "file=@test\_documents\\Document de proiect al unei firme.pdf"

```



Example response:



```json

{

&#x20; "id": 8,

&#x20; "filename": "Document de proiect al unei firme.pdf",

&#x20; "document\_type": "pdf",

&#x20; "path": "/app/uploads/Document de proiect al unei firme.pdf"

}

```



The returned `id` identifies the uploaded document and is used by subsequent processing endpoints.



\---



\# Document Ingestion



After uploading a document, it must be ingested.



```http

POST /documents/{id}/ingest

```



Example:



```bash

curl.exe -X POST "http://localhost:8000/documents/8/ingest"

```



Example response:



```json

{

&#x20; "document\_id": 8,

&#x20; "page\_count": 3,

&#x20; "chunk\_count": 3

}

```



The ingestion stage extracts text from the document and creates chunks that can subsequently be embedded.



\---



\# Generate Embeddings



After ingestion, embeddings can be generated:



```http

POST /documents/{id}/embed

```



Example:



```bash

curl.exe -X POST "http://localhost:8000/documents/8/embed"

```



Example response:



```json

{

&#x20; "document\_id": 8,

&#x20; "chunk\_count": 3,

&#x20; "embedded": true

}

```



The generated embeddings are stored in PostgreSQL using pgvector and are used for semantic retrieval.



\---



\# Query the RAG System



The main RAG endpoint is:



```http

POST /query

```



Example request:



```json

{

&#x20; "question": "Care este bugetul aprobat pentru proiect?",

&#x20; "document\_id": 8,

&#x20; "top\_k": 3

}

```



PowerShell example:



```powershell

$body = @{

&#x20;   question = "Care este bugetul aprobat pentru proiect?"

&#x20;   document\_id = 8

&#x20;   top\_k = 3

} | ConvertTo-Json



$response = Invoke-WebRequest `

&#x20;   -Method POST `

&#x20;   http://localhost:8000/query `

&#x20;   -ContentType "application/json; charset=utf-8" `

&#x20;   -Body (\[System.Text.Encoding]::UTF8.GetBytes($body)) `

&#x20;   -UseBasicParsing



\[System.Text.Encoding]::UTF8.GetString(

&#x20;   $response.RawContentStream.ToArray()

)

```



The RAG pipeline performs semantic retrieval against the document embeddings and sends the relevant context to the configured LLM.



\---



\# Complete End-to-End Example



The complete document workflow is:



```text

Upload

&#x20;  ↓

Ingest

&#x20;  ↓

Chunking

&#x20;  ↓

Embed

&#x20;  ↓

Vector Storage

&#x20;  ↓

Semantic Search

&#x20;  ↓

Context Retrieval

&#x20;  ↓

LLM

&#x20;  ↓

Answer

```



\### 1. Upload



```bash

curl.exe -X POST "http://localhost:8000/documents/upload" ^

&#x20; -F "file=@test\_documents\\Document de proiect al unei firme.pdf"

```



Assume the API returns:



```json

{

&#x20; "id": 8

}

```



\### 2. Ingest



```bash

curl.exe -X POST "http://localhost:8000/documents/8/ingest"

```



Expected result:



```json

{

&#x20; "document\_id": 8,

&#x20; "page\_count": 3,

&#x20; "chunk\_count": 3

}

```



\### 3. Generate embeddings



```bash

curl.exe -X POST "http://localhost:8000/documents/8/embed"

```



Expected result:



```json

{

&#x20; "document\_id": 8,

&#x20; "chunk\_count": 3,

&#x20; "embedded": true

}

```



\### 4. Query



```json

{

&#x20; "question": "Care este bugetul aprobat pentru proiect?",

&#x20; "document\_id": 8,

&#x20; "top\_k": 3

}

```



The system retrieves the most relevant chunks and uses them as context for the LLM response.



\---



\# Functional Verification



The core application workflow has been verified successfully:



\* `/health`

\* `/health/db`

\* PDF document upload

\* Document ingestion

\* Embedding generation

\* Query with existing information

\* Query requiring information from multiple chunks

\* Query where the requested information does not exist

\* Ollama communication from the API container

\* End-to-end document processing



A final end-to-end test was performed using a document from `test\_documents`:



```text

PDF

&#x20;↓

Upload

&#x20;↓

Ingest

&#x20;↓

3 pages

&#x20;↓

3 chunks

&#x20;↓

Embed

&#x20;↓

3 embeddings

&#x20;↓

Ready for RAG

```



This confirms that the core document-to-RAG pipeline is operational.



\---



\# Why Docker?



Docker provides a reproducible development environment and isolates application services from the host environment.



The current architecture allows:



\* the API to run inside a Docker container

\* PostgreSQL to run as a containerized service

\* Ollama to run locally on the host machine

\* the API container to communicate with Ollama through `host.docker.internal`



This setup keeps the local development environment simple while providing a foundation that can later be adapted for production deployment.



\---



\# Troubleshooting



\## Ollama is not reachable



Make sure Ollama is running:



```bash

ollama list

```



Verify that the configured model is available:



```bash

ollama list

```



Check the application configuration:



```env

OLLAMA\_URL=http://host.docker.internal:11434

OLLAMA\_MODEL=qwen3:4b-instruct

```



\---



\## Docker container cannot connect to Ollama



If Ollama is running directly on the host machine, the container should use:



```text

host.docker.internal

```



instead of:



```text

localhost

```



For example:



```env

OLLAMA\_URL=http://host.docker.internal:11434

```



\---



\## Database connection problems



Check the running services:



```bash

docker compose ps

```



Inspect the application logs:



```bash

docker compose logs

```



For continuous logs:



```bash

docker compose logs -f

```



\---



\# Security Considerations



The current configuration is intended primarily for local development.



Before deploying the application to a production environment, additional security controls should be implemented, including:



\* authentication and authorization

\* API rate limiting

\* strict input validation

\* file type validation

\* file size restrictions

\* secure secret management

\* database access controls

\* HTTPS/TLS

\* logging and monitoring

\* container hardening

\* protection against malicious document uploads

\* appropriate network isolation



Credentials and secrets should never be committed to the repository.



\---



\# Future Improvements



Potential improvements include:



\* support for additional document formats

\* improved chunking strategies

\* metadata filtering

\* multi-document collections

\* authentication and user management

\* streaming LLM responses

\* asynchronous document processing

\* background ingestion and embedding jobs

\* configurable embedding models

\* configurable LLM providers

\* automated unit and integration tests

\* CI/CD pipeline

\* production observability

\* cloud deployment

\* document lifecycle management



\---



\# Project Status



\*\*Status: Functional MVP\*\*



The core RAG pipeline is implemented and verified:



```text

Document Upload

&#x20;      ↓

Document Ingestion

&#x20;      ↓

Text Extraction

&#x20;      ↓

Chunking

&#x20;      ↓

Embeddings

&#x20;      ↓

Vector Storage

&#x20;      ↓

Semantic Retrieval

&#x20;      ↓

Context Generation

&#x20;      ↓

LLM

&#x20;      ↓

Generated Answer

```



The project is ready for further development toward a production-grade document intelligence platform.



\---



\# License



This project is currently provided for educational and development purposes.



A dedicated open-source license can be added when the project's licensing model is finalized.



