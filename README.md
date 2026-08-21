# Remote RAG MCP Server

A Python project that exposes a retrieval-augmented generation (RAG) workflow through a FastMCP server with OAuth 2.0 authentication. It ingests documents from a folder, stores them in a persistent ChromaDB collection, and lets you query the indexed content later via semantic search through an authenticated API.

## Overview

This project combines a document retrieval system with enterprise-grade authentication. It is especially useful when you want to:

- ingest PDF or DOCX documents into a searchable vector store
- run an authenticated MCP server for RAG-style document querying
- keep results persistent across runs with ChromaDB
- integrate a document search layer with OAuth 2.0 authorization
- expose RAG capabilities through a secure HTTP API with CORS support

## Features

- **OAuth 2.0 Authentication** via ScaleKit for secure access control
- **Persistent ChromaDB storage** in the local `./chroma_db` folder
- **Document ingestion** from a directory using `LlamaParse`
- **Multi-format support** for `.pdf` and `.docx` file types
- **Semantic querying** with configurable result count
- **FastAPI wrapper** with CORS middleware for cross-origin requests
- **Environment-based configuration** for flexible deployment
- **Protected resource metadata endpoint** for OAuth client discovery
- **MCP server integration** exposing RAG tools through HTTP

## Project Structure

```text
simple-rag/
├── main.py               # FastAPI app with MCP server integration and auth middleware
├── doc_serv.py           # FastMCP server and RAG tool definitions
├── auth.py               # OAuth 2.0 authentication middleware (ScaleKit)
├── config.py             # Configuration management with environment variables
├── pyproject.toml        # Project dependencies and Python config
├── README.md             # Project documentation
├── papers/               # Source documents for ingestion
├── chroma_db/            # Persistent ChromaDB storage
└── .env                  # Environment variables (not committed)
```

## Tech Stack

- Python 3.13+
- FastAPI & Uvicorn
- FastMCP
- ChromaDB
- LlamaParse
- LlamaIndex
- ScaleKit (OAuth 2.0)
- Starlette
- python-dotenv

## Installation

Using `uv`:

```bash
uv sync
```

Or with `pip`:

```bash
pip install -r requirements.txt
```

If you are using this project as a standard Python package, the dependency list is already defined in `pyproject.toml`.

## Configuration

The app uses these defaults and environment variables:

### RAG Configuration
- `PERSISTENCE_DIR = "./chroma_db"`
- `COLLECTION_NAME = "mcp_rag_collection"`
- `DATA_DIR = "./papers"`

### OAuth 2.0 (ScaleKit)
- `SCALEKIT_ENVIRONMENT_URL`: ScaleKit environment URL
- `SCALEKIT_CLIENT_ID`: OAuth client ID
- `SCALEKIT_CLIENT_SECRET`: OAuth client secret
- `SCALEKIT_RESOURCE_METADATA_URL`: Resource metadata endpoint
- `SCALEKIT_AUDIENCE_NAME`: OAuth audience identifier

### Server Configuration
- `PORT`: Server port (default: 10000)
- `DOCUMENTS_API_KEY`: API key for document service

### Running with uvicorn

```python
uvicorn.run(app, host="0.0.0.0", port=settings.PORT, log_level="debug")
```

## Running the Server

### Prerequisites

Set up your environment variables in a `.env` file:

```bash
SCALEKIT_ENVIRONMENT_URL=<your_scalekit_url>
SCALEKIT_CLIENT_ID=<your_client_id>
SCALEKIT_CLIENT_SECRET=<your_client_secret>
SCALEKIT_RESOURCE_METADATA_URL=<your_metadata_url>
SCALEKIT_AUDIENCE_NAME=<your_audience>
METADATA_JSON_RESPONSE='<json_response>'
DOCUMENTS_API_KEY=<your_api_key>
PORT=10000
```

### Start the Server

```bash
uv run main.py
```

This starts the FastAPI server with the MCP server mounted, running on:

```text
http://0.0.0.0:10000
```

### Making Authenticated Requests

All API endpoints (except `.well-known/` paths) require OAuth 2.0 bearer token authentication:

```bash
curl -H "Authorization: Bearer <your_token>" http://localhost:10000/mcp/tools
```



## API Endpoints

### OAuth 2.0 Protected Resource Metadata
- **GET** `/.well-known/oauth-protected-resource/mcp`
  - Returns OAuth metadata required by MCP clients for authorization discovery
  - No authentication required

### MCP Tools (Authenticated)
All MCP tool endpoints require a valid Bearer token in the `Authorization` header:

```
Authorization: Bearer <OAuth_2.0_access_token>
```

**Available Tools:**

- `POST /mcp/tools/ingest_data_directory` - Ingest documents into ChromaDB
- `POST /mcp/tools/query_documents` - Query the document collection

## Available Tools

### ingest_data_directory

Ingests all supported files in a directory into a ChromaDB collection using LlamaParse for text extraction.

**Parameters:**

- `llama_cloud_api_key` (str): API key for LlamaParse
- `collection_name` (str): Target ChromaDB collection name
- `data_dir` (str): Path to the folder containing documents

**Supported formats:** `.pdf`, `.docx`

**Example call:**

```python
ingest_data_directory(
    llama_cloud_api_key="your_api_key",
    collection_name="research_docs",
    data_dir="./papers"
)
```

**Response:**
```
Final document count in collection 'research_docs': 12
```

### query_documents

Queries a collection for the most relevant documents based on semantic similarity.

**Parameters:**

- `query` (str): Search query text
- `n_results` (int): Number of results to return (default: 2)
- `collection_name` (str): Collection to search (default: `mcp_rag_collection`)

**Example call:**

```python
query_documents(
    query="What are the main findings?",
    n_results=5,
    collection_name="research_docs"
)
```

**Response:**
```
-- Result 1 --
Document content: <extracted text>
Metadata: <document metadata>
Distance: <similarity score>

## Example Workflow

1. **Configure Environment**: Set up all required environment variables in `.env` (see Configuration section).
2. **Start Server**: Run `uv run main.py` to start the FastAPI server.
3. **Obtain Token**: Get an OAuth 2.0 access token from your ScaleKit authorization server.
4. **Place Documents**: Add your `.pdf` or `.docx` files to the `papers/` directory.
5. **Ingest Data**: Call `ingest_data_directory` with your LlamaCloud API key and OAuth token.
6. **Query**: Use `query_documents` to search your ingested documents with proper authentication.
7. **Review Results**: Inspect returned documents and metadata for relevant passages.

## Notes

- **Authentication Required**: All endpoints except `.well-known/` paths require OAuth 2.0 bearer token authentication via ScaleKit.
- **Persistent Storage**: ChromaDB persists data locally, so documents remain available between server restarts.
- **Supported Formats**: Currently supports `.pdf` and `.docx` ingestion through LlamaParse.
- **Default Embeddings**: Uses ChromaDB's default embedding model unless modified.
- **CORS Enabled**: Server accepts cross-origin requests from any origin (configurable in production).
- **Scalability**: For production use, ensure proper environment variable management and consider database connection pooling.

## License

This project does not currently include a custom license file. If you plan to share or publish it, add a license that matches your intended usage.

## Next Ideas

- Add a `.env.example` template for easier setup
- Support more file types (`.txt`, `.docx`, `.pptx`, etc.)
- Implement token caching and refresh logic
- Add request/response logging middleware
- Create a Python client library for the API
- Add comprehensive API documentation (OpenAPI/Swagger)
- Implement rate limiting per authenticated user
- Add collection management endpoints (list, delete, update)
- Support custom embedding models configuration
- Add health check endpoint
- Create example integration tests with OAuth mocking
