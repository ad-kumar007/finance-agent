# agents/retriever_agent.py

import os
import requests
from bs4 import BeautifulSoup

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.document_loaders import TextLoader, CSVLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter


def scrape_webpage(url: str, save_path: str = "data_ingestion/webpage_content.txt") -> str:
    """
    Scrape visible text from a webpage and save it locally.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract visible text
        texts = soup.stripped_strings
        page_text = "\n".join(texts)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(page_text)

        print(f"Webpage scraped and saved to {save_path}")
        return save_path
    except Exception as e:
        print(f"Error scraping webpage: {e}")
        return ""


def load_documents(file_paths: list):
    """
    Load documents (txt, csv, pdf) into LangChain document objects.
    """
    docs = []
    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".txt":
            loader = TextLoader(path)
        elif ext == ".csv":
            loader = CSVLoader(path)
        elif ext == ".pdf":
            loader = PyPDFLoader(path)
        else:
            print(f"Unsupported file type {ext}, skipping {path}")
            continue
        docs.extend(loader.load())
    return docs


def build_vector_store(file_paths: list, index_path: str = "faiss_index"):
    """
    Build or load a FAISS vector store from documents.
    """
    # Load documents
    documents = load_documents(file_paths)

    # Split documents into chunks for embedding
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(documents)

    # Initialize embedding model
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Build or load FAISS index
    if not os.path.exists(index_path):
        print("Building new FAISS index...")
        vectorstore = FAISS.from_documents(split_docs, embedding_model)
        vectorstore.save_local(index_path)
    else:
        print("Loading existing FAISS index...")
        vectorstore = FAISS.load_local(
            index_path,
            embedding_model,
            allow_dangerous_deserialization=True
        )
    return vectorstore


def retrieve_top_chunks(query: str, vectorstore, k: int = 3):
    """
    Retrieve top-k relevant chunks for a query from the vectorstore.
    """
    results = vectorstore.similarity_search(query, k=k)
    return [r.page_content for r in results]


if __name__ == "__main__":
    # Example usage

    # Step 1: Scrape a webpage (optional)
    scraped_file = scrape_webpage("https://www.sec.gov/Archives/edgar/data/0000320193/000032019323000010/aapl-20230930.htm")

    # Step 2: List your data files for ingestion (add scraped file if exists)
    files = [
        "data_ingestion/sample_earnings.txt",
        "data_ingestion/sample_data.csv",
        "data_ingestion/sample_report.pdf",
    ]
    if scraped_file:
        files.append(scraped_file)

    # Step 3: Build or load vectorstore
    vs = build_vector_store(files)

    # Step 4: Test retrieval
    query = "Did TSMC beat earnings expectations?"
    top_chunks = retrieve_top_chunks(query, vs)
    print("\nTop Relevant Chunks:\n", top_chunks)
