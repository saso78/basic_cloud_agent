# rag_pdf_loader.py
import os
import pdfplumber
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
CHROMA_DB_PATH = "rag_db"
COLLECTION_NAME = "pdf_knowledge"
CHUNK_SIZE = 300  # Smaller chunks for better retrieval
CHUNK_OVERLAP = 50  # Overlap between chunks to preserve context

# Load embedding model (downloads on first run, ~90MB)
print("🔄 Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, lightweight
print("✅ Embedding model loaded!\n")


def get_embedding(text):
    """Generate embedding using local model."""
    try:
        embedding = embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    except Exception as e:
        print(f"❌ Embedding error: {e}")
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
    """Split text into chunks by paragraphs."""
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
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"📄 Loading PDF: {file_path}")
    text = extract_text_from_pdf(file_path)
    
    if not text.strip():
        print("❌ No text extracted from PDF!")
        return
    
    chunks = split_into_chunks(text)
    print(f"✂️ Split into {len(chunks)} chunks")

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    successful = 0
    for i, chunk in enumerate(chunks):
        print(f"🔢 Embedding chunk {i+1}/{len(chunks)}...", end=' ')
        embedding = get_embedding(chunk)
        if embedding is None:
            print("⚠️ Skipped")
            continue
        
        collection.add(
            ids=[f"{os.path.basename(file_path)}_{i}"],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[{"source": file_path, "chunk_index": i}]
        )
        successful += 1
        print("✅")

    print(f"\n✅ PDF indexed successfully! ({successful}/{len(chunks)} chunks)")


def query_knowledge(query_text, n_results=3):
    """Query the knowledge base."""
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except:
        return "📭 No knowledge base found. Index a PDF first!"

    print("🔍 Searching knowledge base...")
    query_embedding = get_embedding(query_text)
    if query_embedding is None:
        return "⚠️ Cannot generate embedding for query."

    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=n_results
    )
    
    docs = results.get("documents")
    if not docs or not docs[0]:
        return "📭 No relevant info found in knowledge base."
    
    # Format results nicely
    context = ""
    for i, doc in enumerate(docs[0], 1):
        context += f"\n📄 Result {i}:\n{doc}\n"
        context += "-" * 80 + "\n"
    
    return context


def list_indexed_documents():
    """List all documents in the knowledge base."""
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        items = collection.get()
        
        if not items or not items['ids']:
            print("📭 No documents indexed yet.")
            return
        
        # Extract unique sources
        sources = set()
        for metadata in items.get('metadatas', []):
            if metadata and 'source' in metadata:
                sources.add(metadata['source'])
        
        print(f"\n📚 Knowledge Base Stats:")
        print(f"   Total chunks: {len(items['ids'])}")
        print(f"   Documents: {len(sources)}")
        print(f"\n📄 Indexed documents:")
        for source in sorted(sources):
            print(f"   • {source}")
    except:
        print("📭 No knowledge base found.")


if __name__ == "__main__":
    print("🤖 RAG Loader / PDF Indexer")
    print("============================")
    print("1️⃣ Index a PDF file")
    print("2️⃣ Query the stored knowledge")
    print("3️⃣ List indexed documents")
    print("4️⃣ Clear knowledge base")
    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        path = input("Enter PDF path: ").strip()
        # Remove quotes if user copied path with quotes
        path = path.strip('"').strip("'")
        index_pdf(path)
    
    elif choice == "2":
        query = input("Enter your question: ").strip()
        context = query_knowledge(query)
        print("\n📚 Context found:\n")
        print(context)
    
    elif choice == "3":
        list_indexed_documents()
    
    elif choice == "4":
        confirm = input("⚠️ Clear entire knowledge base? (yes/no): ").strip().lower()
        if confirm == "yes":
            import shutil
            if os.path.exists(CHROMA_DB_PATH):
                shutil.rmtree(CHROMA_DB_PATH)
                print("✅ Knowledge base cleared!")
            else:
                print("📭 No knowledge base to clear.")
        else:
            print("❌ Cancelled.")
    
    else:
        print("❌ Invalid choice.")