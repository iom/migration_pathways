# embedder.py
import os
import uuid
import json
import hashlib
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
#from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_core.documents import Document

from utility.scraper_and_embedder import scrape_wakawell_pages
from utility.file_loader import load_and_split_file

load_dotenv()

CHROMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_store"))
UPLOADED_METADATA_PATH = os.path.join("config", "uploaded_files.json")

# embedding_model = AzureOpenAIEmbeddings(
#     azure_deployment="embedding-ada",  
#     openai_api_version="2023-05-15"
# )

embedding_model = AzureOpenAIEmbeddings(
    model= os.getenv("AZURE_EMBEDDING_MODEL"),
    azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"),
    api_key= os.getenv("AZURE_OPENAI_API_KEY_EMBED"),
    openai_api_version= os.getenv("AZURE_OPENAI_API_VERSION_EMBED"),
    deployment= os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False
)

# ----- (1) Scraped Documents Embedding -----
def prepare_documents(scraped_data):
    all_chunks = []
    for page in scraped_data:
        text = page.get("text", "")
        url = page.get("url")
        title = page.get("title", "")

        if not text.strip():
            continue

        chunks = text_splitter.create_documents([text])
        for chunk in chunks:
            chunk.metadata["source_url"] = url
            chunk.metadata["title"] = title
            chunk.metadata["id"] = str(uuid.uuid4())
            chunk.metadata["source"] = "scraped"
        all_chunks.extend(chunks)
    return all_chunks

def embed_and_store_documents(documents):
    """Embed documents and overwrite Chroma DB scraped content"""
    if not documents:
        print(" No documents to embed.")
        return

    print(f" Total chunks to embed: {len(documents)}")

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )
    vector_store.persist()
    print(f" Embeddings saved to: {CHROMA_DIR}")

    metadata_log = [
        {
            "id": doc.metadata.get("id", ""),
            "url": doc.metadata.get("source_url"),
            "title": doc.metadata.get("title"),
            "content_snippet": doc.page_content[:150].replace("\n", " ") + "."
        }
        for doc in documents
    ]

    with open("embedding_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_log, f, indent=2, ensure_ascii=False)

    print(" Saved embedding metadata to embedding_metadata.json")

# ----- (2) Uploaded Files Embedding -----
def load_uploaded_metadata():
    if os.path.exists(UPLOADED_METADATA_PATH):
        with open(UPLOADED_METADATA_PATH, "r") as f:
            return json.load(f)
    return []

def save_uploaded_metadata(metadata):
    with open(UPLOADED_METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

def compute_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def embed_uploaded_file(file_path: str, uploaded_by: str) -> dict:
    file_name = os.path.basename(file_path)
    file_hash = compute_file_hash(file_path)

    metadata_list = load_uploaded_metadata()

    if any(entry["file_hash"] == file_hash for entry in metadata_list):
        return {
            "status": "duplicate",
            "message": f"File '{file_name}' already uploaded",
            "filename": file_name
        }

    try:
        chunks = load_and_split_file(file_path)

        for doc in chunks:
            doc.metadata["source"] = "uploaded"
            doc.metadata["filename"] = file_name
            doc.metadata["file_hash"] = file_hash
            doc.metadata["uploaded_by"] = uploaded_by
            doc.metadata["id"] = str(uuid.uuid4())

        vector_store = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embedding_model
        )
        vector_store.add_documents(chunks)
        vector_store.persist()

        metadata_list.append({
            "filename": file_name,
            "file_hash": file_hash,
            "uploaded_by": uploaded_by
        })
        save_uploaded_metadata(metadata_list)

        return {
            "status": "success",
            "file": file_name,
            "chunks_added": len(chunks)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ----- (3) CLI for Testing -----
if __name__ == "__main__":
    print("🔍 Loading scraped Wakawell content...")
    scraped_pages = scrape_wakawell_pages()

    print("📄 Chunking and preparing documents...")
    documents = prepare_documents(scraped_pages)

    print("📦 Embedding and storing to Chroma...")
    embed_and_store_documents(documents)
