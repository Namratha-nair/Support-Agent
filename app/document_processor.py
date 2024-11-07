
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFDirectoryLoader
from .embeddings import Embeddings
import logging
def process_documents(folder_path: str):
    # Load the document
    loader = PyPDFDirectoryLoader(folder_path)
    docs = loader.load()
    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(docs)
    # Extract text from chunks
    texts = [chunk.page_content for chunk in chunks]
    # Create JLLEmbeddings instance
    embedding_function = Embeddings()
    # Create and return the vector store
    return Chroma.from_texts(texts, embedding_function)
    
def query_document(vector_store, query: str, k: int = 1):
    try:
        results = vector_store.similarity_search(query, k=k)
        return [result.page_content for result in results]
    except Exception as e:
        logging.error(f"Error querying document: {e}")
        return []
