# embedder.py
import os
import uuid
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_core.documents import Document
from utility.scraper_and_embedder import scrape_wakawell_pages

load_dotenv()

CHROMA_DIR = "chroma_store"

embedding_model = AzureOpenAIEmbeddings(
    azure_deployment="embedding-ada",  
    openai_api_version="2023-05-15"
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False
)

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
        all_chunks.extend(chunks)
    return all_chunks

def embed_and_store_documents(documents):
    """Embed documents and store in Chroma DB"""
    if not documents:
        print("❌ No documents to embed.")
        return

    print(f"📚 Total chunks to embed: {len(documents)}")

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )
    vector_store.persist()
    print(f"✅ Embeddings saved to: {CHROMA_DIR}")

    metadata_log = [
        {
            "id": doc.metadata["id"],
            "url": doc.metadata.get("source_url"),
            "title": doc.metadata.get("title"),
            "content_snippet": doc.page_content[:150].replace("\n", " ") + "..."
        }
        for doc in documents
    ]

    with open("embedding_metadata.json", "w", encoding="utf-8") as f:
        import json
        json.dump(metadata_log, f, indent=2, ensure_ascii=False)

    print("📝 Saved embedding metadata to embedding_metadata.json")

def generate_embeddings(text: str) -> list:
    """Generate embedding for a single string using AzureOpenAIEmbeddings"""
    return embedding_model.embed_query(text)


if __name__ == "__main__":
    print("🔎 Loading scraped Wakawell content...")
    scraped_pages = scrape_wakawell_pages()

    print("🔄 Chunking and preparing documents...")
    documents = prepare_documents(scraped_pages)

    print("📥 Embedding and storing to Chroma...")
    embed_and_store_documents(documents)
