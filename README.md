# Simple RAG MCP Server

A lightweight Python project that exposes a retrieval-augmented generation (RAG) workflow through a FastMCP server. It ingests documents from a folder, stores them in a persistent ChromaDB collection, and lets you query the indexed content later via semantic search.

## Overview

This project is built for local document retrieval and experimentation. It is especially useful when you want to:

- ingest PDF or DOCX documents into a searchable vector store
- run a local MCP server for RAG-style document querying
- keep results persistent across runs with ChromaDB
- integrate a document search layer into other AI/MCP workflows

## Features

- Persistent ChromaDB storage in the local `./chroma_db` folder
- Document ingestion from a directory using `LlamaParse`
- Support for `.pdf` and `.docx` file types
- Semantic querying with configurable result count
- Collection-level statistics for monitoring indexed data
- FastMCP HTTP server running on `localhost:8000`

## Project Structure

```text
simple-rag/
├── main.py               # FastMCP server and RAG tool definitions
├── pyproject.toml        # Project dependencies and Python config
├── README.md             # Project documentation
├── papers/               # Source documents for ingestion
├── chroma_db/            # Persistent ChromaDB storage
└── .env                  # Optional environment variables (if used locally)
```

## Tech Stack

- Python 3.13+
- FastMCP
- ChromaDB
- LlamaParse
- LlamaIndex
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

The app uses these defaults:

- `PERSISTENCE_DIR = "./chroma_db"`
- `COLLECTION_NAME = "mcp_rag_collection"`
- `DATA_DIR = "./papers"`

The server runs with:

```python
mcp.run(transport="streamable-http", host="localhost", port=8000)
```

## Running the Server

```bash
uv run main.py
```

This starts the MCP server locally and exposes the tools over HTTP on:

```text
http://localhost:8000
```

## Remote Access with ngrok and Hugging Face

If you want to use the MCP server from a remote chat client such as Hugging Face Chat, expose the local server through a public tunnel first.

### 1) Start the server locally

```bash
uv run main.py
```

### 2) Expose port 8000 with ngrok

In a separate terminal, run:

```bash
ngrok http 8000
```

This creates a public HTTPS URL such as:

```text
https://abcd1234.ngrok-free.app
```

Copy the generated forwarding URL.

### 3) Use the URL in a remote MCP client

Because this project uses FastMCP with `streamable-http`, the remote client typically connects to the MCP endpoint exposed by the tunnel. In practice, you usually use the ngrok HTTPS URL as the remote MCP server address, often with the MCP path required by the client (commonly `/mcp` if the client expects an explicit endpoint).

Example pattern:

```text
https://abcd1234.ngrok-free.app
```

or

```text
https://abcd1234.ngrok-free.app/mcp
```

The exact path depends on the external client implementation, but the core idea is the same: your local `localhost:8000` server is exposed publicly through ngrok, and the remote MCP client points to the tunneled URL instead of the local machine.

### 4) Query it in Hugging Face Chat

Once the remote MCP server is configured in Hugging Face Chat:

1. Add the remote MCP server using the copied ngrok URL.
2. Confirm the server connects successfully.
3. Ask natural-language questions in chat.
4. The model will invoke the MCP tools exposed by this project, such as `ingest_data_directory`, `query_documents`, and `get_db_stats`.

This enables the remote chat app to query your local knowledge base without running the RAG server on the same machine.

> Note: the tunnel is temporary and public, so keep the ngrok URL private if you do not want external access to your local MCP service.

## Available Tools

### ingest_data_directory

Ingests all supported files in a directory into a ChromaDB collection.

Parameters:

- `llama_cloud_api_key`: API key for `LlamaParse`
- `collection_name`: target ChromaDB collection
- `data_dir`: path to the folder containing documents

Example call:

```python
ingest_data_directory(
    llama_cloud_api_key="your_api_key",
    collection_name="research_docs",
    data_dir="./papers"
)
```

### query_documents

Queries a collection for the most relevant documents based on text similarity.

Parameters:

- `query`: search text
- `n_results`: number of results to return (default `2`)
- `collection_name`: collection to search

Example call:

```python
query_documents(
    query="What are the main findings in this paper?",
    n_results=5,
    collection_name="research_docs"
)
```

### get_db_stats

Returns the current number of stored documents in a collection.

## Example Workflow

1. Place your `.pdf` or `.docx` files inside the `papers/` directory.
2. Start the server.
3. Call `ingest_data_directory` with your LlamaCloud API key.
4. Run a query using `query_documents`.
5. Inspect the returned documents and metadata for relevant passages.

## Notes

- ChromaDB is configured to persist data locally, so documents remain available between runs.
- This project currently supports `.pdf` and `.docx` ingestion through `LlamaParse`.
- The code uses the default Chroma embedding behavior unless you modify the implementation.

## License

This project does not currently include a custom license file. If you plan to share or publish it, add a license that matches your intended usage.

## Next Ideas

- add a `.env.example` template
- support more file types
- add automatic embedding model configuration
- improve result formatting and validation
- create a client example for testing the MCP server
