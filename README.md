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

                        ┌──────────────────┐

                        │      Client      │

                        └────────┬─────────┘

                                 │

                                 ▼

                        ┌──────────────────┐

                        │     FastAPI      │

                        │       API        │

                        └────────┬─────────┘

                                 │

            ┌────────────────────┼────────────────────┐

            │                    │                    │

            ▼                    ▼                    ▼

         Upload                Ingest               Query

            │                    │                    │

            │                    ▼                    │

            │              Text Extraction           │

            │                    │                    │

            │                    ▼                    │

            │                Chunking                │

            │                    │                    │

            │                    ▼                    │

            │               Embeddings               │

            │                    │                    │

            │                    ▼                    │

            │             PostgreSQL +                │

            │               pgvector                  │

            │                         ▲               │

            │                         │               │

            │                  Vector Search ◄────────┘

            │                         │

            │                         ▼

            │                      Context

            │                         │

            │                         ▼

            │                       Ollama

            │                         │

            │                         ▼

            └────────────────────►  Answer

```



\### RAG Pipeline



A document follows this processing pipeline:



```text

Document

  │

  ▼

Upload

  │

  ▼

Ingest

  │

  ├── Text extraction

  ├── Page processing

  └── Chunk creation

  │

  ▼

Embed

  │

  └── Vector embeddings

  │

  ▼

PostgreSQL + pgvector

  │

  ▼

Semantic Search

  │

  ▼

Relevant Context

  │

  ▼

Ollama / LLM

  │

  ▼

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

 -F "file=@test\_documents\\Document de proiect al unei firme.pdf"

```



Example response:



```json

{

 "id": 8,

 "filename": "Document de proiect al unei firme.pdf",

 "document\_type": "pdf",

 "path": "/app/uploads/Document de proiect al unei firme.pdf"

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

 "document\_id": 8,

 "page\_count": 3,

 "chunk\_count": 3

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

 "document\_id": 8,

 "chunk\_count": 3,

 "embedded": true

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

 "question": "Care este bugetul aprobat pentru proiect?",

 "document\_id": 8,

 "top\_k": 3

}

```



PowerShell example:



```powershell

$body = @{

   question = "Care este bugetul aprobat pentru proiect?"

   document\_id = 8

   top\_k = 3

} | ConvertTo-Json



$response = Invoke-WebRequest `

   -Method POST `

   http://localhost:8000/query `

   -ContentType "application/json; charset=utf-8" `

   -Body (\[System.Text.Encoding]::UTF8.GetBytes($body)) `

   -UseBasicParsing



\[System.Text.Encoding]::UTF8.GetString(

   $response.RawContentStream.ToArray()

)

```



The RAG pipeline performs semantic retrieval against the document embeddings and sends the relevant context to the configured LLM.



\---



\# Complete End-to-End Example



The complete document workflow is:



```text

   Upload

     ↓

   Ingest

     ↓

  Chunking

     ↓

   Embed

     ↓

Vector Storage

     ↓

Semantic Search

     ↓

Context Retrieval

     ↓

    LLM

     ↓

   Answer

```



\### 1. Upload



```bash

curl.exe -X POST "http://localhost:8000/documents/upload" ^

 -F "file=@test\_documents\\Document de proiect al unei firme.pdf"

```



Assume the API returns:



```json

{

 "id": 8

}

```



\### 2. Ingest



```bash

curl.exe -X POST "http://localhost:8000/documents/8/ingest"

```



Expected result:



```json

{

 "document\_id": 8,

 "page\_count": 3,

 "chunk\_count": 3

}

```



\### 3. Generate embeddings



```bash

curl.exe -X POST "http://localhost:8000/documents/8/embed"

```



Expected result:



```json

{

 "document\_id": 8,

 "chunk\_count": 3,

 "embedded": true

}

```



\### 4. Query



```json

{

 "question": "Care este bugetul aprobat pentru proiect?",

 "document\_id": 8,

 "top\_k": 3

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

↓

Upload

↓

Ingest

↓

3 pages

↓

3 chunks

↓

Embed

↓

3 embeddings

↓

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

       ↓

Document Ingestion

       ↓

 Text Extraction

       ↓

    Chunking

       ↓

   Embeddings

       ↓

 Vector Storage

       ↓

Semantic Retrieval

       ↓

Context Generation

       ↓

      LLM

       ↓

 Generated Answer

```



The project is ready for further development toward a production-grade document intelligence platform.



\---



\# License



This project is currently provided for educational and development purposes.



A dedicated open-source license can be added when the project's licensing model is finalized.



