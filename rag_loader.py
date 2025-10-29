import os
import time
import pdfplumber
import chromadb
from chromadb.config import Settings
import requests
import textwrap
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# --- CONFIG ---
CHROMA_DB_PATH = "rag_db"
COLLECTION_NAME = "pdf_knowledge"
EMBED_MODEL = "text-embedding-3-small"  # can switch later
CHUNK_SIZE = 1000  # chars per text chunk


def get_embedding(text, retries=3):
    for attempt in range(retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": EMBED_MODEL, "input": text},
                timeout=30,
            )
            
            if not response.ok:
                print(f"❌ Embedding failed ({attempt+1}/{retries}): {response.status_code} - {response.text[:200]}")
                continue
            
            try:
                data = response.json()
                return data["data"][0]["embedding"]
            except Exception as e:
                print(f"❌ JSON decode error ({attempt+1}/{retries}): {e}")
                continue

        except Exception as e:
            print(f"❌ Embedding request error ({attempt+1}/{retries}): {e}")
    
    return None



def extract_text_from_pdf(file_path):
    """Extract text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def split_into_chunks(text, size=CHUNK_SIZE):
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) <= size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def index_pdf(file_path):
    """Process PDF, embed chunks, and store in Chroma DB."""
    if not api_key:
        print("❌ Missing OPENROUTER_API_KEY in .env")
        return

    print(f"📄 Loading PDF: {file_path}")
    text = extract_text_from_pdf(file_path)
    chunks = split_into_chunks(text)
    print(f"✂️ Split into {len(chunks)} chunks")

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    for i, chunk in enumerate(chunks):
        print(f"🔢 Embedding chunk {i+1}/{len(chunks)}...")
        embedding = get_embedding(chunk)
        if embedding is None:
         print("⚠️ Skipping chunk due to embedding error.")
         continue
        collection.add(
            ids=[f"{os.path.basename(file_path)}_{i}"],
            documents=[chunk],
            embeddings=[embedding], 
        )

    print("✅ PDF indexed successfully!")


def query_knowledge(query_text):
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    print("🔍 Searching knowledge base...")
    query_embedding = get_embedding(query_text)
    if query_embedding is None:
        return "⚠️ Cannot generate embedding for query."

    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    docs = results.get("documents")
    if not docs or not docs[0]:
        return "📭 No relevant info found in knowledge base."
    return "\n\n".join(docs[0])



if __name__ == "__main__":
    print("🤖 RAG Loader / PDF Indexer")
    print("============================")
    print("1️⃣ Index a PDF file")
    print("2️⃣ Query the stored knowledge")
    choice = input("Select option (1/2): ").strip()

    if choice == "1":
        path = input("Enter PDF path: ").strip()
        index_pdf(path)
    elif choice == "2":
        query = input("Enter your question: ").strip()
        context = query_knowledge(query)
        print("\n📚 Context found:\n")
        print(context[:2000])
    else:
        print("❌ Invalid choice.")
