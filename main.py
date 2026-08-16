import os
from fastmcp import FastMCP
import chromadb
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

PERSISTENCE_DIR = "./chroma_db"
COLLECTION_NAME = "mcp_rag_collection"

def init_chromadb():
    client = chromadb.PersistentClient(path=PERSISTENCE_DIR)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)   
    return collection 

def get_chromadb_client():
    return chromadb.PersistentClient(path=PERSISTENCE_DIR)

def main():
    init_chromadb()

if __name__ == "__main__":
    main()
    