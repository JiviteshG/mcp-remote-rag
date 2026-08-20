import os
from fastmcp import FastMCP
import chromadb
# from llama_cloud_services import LlamaParse
from llama_parse import LlamaParse

import warnings
warnings.filterwarnings("ignore")

from llama_index.core import SimpleDirectoryReader
from dotenv import load_dotenv

PERSISTENCE_DIR = "./chroma_db"
COLLECTION_NAME = "mcp_rag_collection"
DATA_DIR = "./papers"

mcp = FastMCP(name = "Remote RAG MCP Server",
              instructions="Welcome to the Remote RAG MCP Server! This server allows you to ingest documents from a specified directory into a ChromaDB collection and query them later. You can use the provided tools to manage your document collection and retrieve relevant information based on your queries.",
              description="This MCP server is designed to facilitate the ingestion and querying of documents using ChromaDB. It provides tools for adding documents to a collection, querying the collection for relevant documents, and retrieving statistics about the collection. The server is built using FastMCP and integrates with LlamaParse for document parsing.",
              version="1.0.0")

def init_chromadb():
    client = chromadb.PersistentClient(path=PERSISTENCE_DIR)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)   
    return collection 

def get_chromadb_client():
    return chromadb.PersistentClient(path=PERSISTENCE_DIR)

@mcp.tool
async def ingest_data_directory(llama_cloud_api_key, collection_name, data_dir):
    """
    Ingests documents from a specified directory into a ChromaDB collection that the user can quert them later.
    Args:
        llama_cloud_api_key (str): The API key for LlamaParse.
        collection_name (str): The name of the ChromaDB collection to store documents.
        data_dir (str): The directory containing documents to ingest.
    Returns:
        list: A list of ingested documents.
    """
    chroma_client = get_chromadb_client()
    chroma_client.delete_collection(name=collection_name)  # Delete the collection if it exists
    collection = chroma_client.get_or_create_collection(name=collection_name)

    parser = LlamaParse(api_key=llama_cloud_api_key, result_type="text")

    # The file extracter accepts pdf and docx files, and uses the LlamaParse parser to extract text from them
    file_extractor = {
        ".pdf": parser,
        ".docx": parser,
        }
    documents = SimpleDirectoryReader(data_dir, file_extractor=file_extractor).load_data()

    # Added documents to chromadb vector database
    # Note: We did not use an embedding model here, chromadb will use the default embedding model to generate embeddings for the documents
    for doc in documents:
        collection.add(
            documents=[doc.text],
            metadatas=[doc.metadata],
            ids=[doc.doc_id]
        )

    final_count = collection.count()
    return f"Final document count in collection '{collection_name}': {final_count}"

@mcp.tool
def query_documents(query: str, n_results: int = 2, collection_name: str = COLLECTION_NAME) -> str:
    """
    Queries the ChromaDB collection for documents relevant to the provided query.
    Args:
        query (str): The query string to search for relevant documents.
        n_results (int): The number of top results to return. Default is 2.
        collection_name (str): The name of the ChromaDB collection to query. Default is COLLECTION_NAME.
    Returns:
        str: A formatted string containing the query results, including document content, metadata, and distances.
    """
    chroma_client = get_chromadb_client()
    collection = chroma_client.get_collection(name=collection_name)

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    if len(results["documents"]) == 0 or not results["documents"][0]:
        return "No documents found."

    # Format the results for better readability
    formatted_results = []
    documents = results["documents"][0]
    metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)
    distances = results["distances"][0] if results["distances"] else [0] * len(documents)

    for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
        result_text = f"-- Result {i + 1} --\n"
        result_text += f"Document content: {doc}\n"
        result_text += f"Metadata: {metadata}\n"
        result_text += f"Distance: {distance}\n"
        formatted_results.append(result_text)

    response = f"FOund {len(formatted_results)} results for query: '{query}'\n\n" + "\n".join(formatted_results) 
    response += "\n".join(formatted_results) 

    return response

@mcp.tool
def get_db_stats(collection_name: str = COLLECTION_NAME) -> str:
    """
    Retrieves statistics about the ChromaDB collection, including the number of documents.
    Args:
        collection_name (str): The name of the ChromaDB collection to retrieve stats from. Default is COLLECTION_NAME.
    Returns:
        str: A formatted string containing the number of documents in the collection.
    """
    chroma_client = get_chromadb_client()
    collection = chroma_client.get_collection(name=collection_name)

    document_count = collection.count()

    return f"Collection '{collection_name}' contains {document_count} documents."

def main():
    init_chromadb()
    load_dotenv()
    mcp.run(transport="streamable-http", host="localhost", port=8000)

if __name__ == "__main__":
    main()
    