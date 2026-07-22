"""
venv\Scripts\activate
ingestion_pipeline.py
======================
Data ingestion pipeline for the Women's Health RAG chatbot.

What this does, end to end:
  1. Recursively finds every .pdf and .docx file under a data folder.
  2. Loads and parses each one (PyMuPDFLoader for PDF, Docx2txtLoader for DOCX).
  3. Attaches useful metadata to every page/doc (file name, type, page number).
  4. Splits everything into overlapping chunks sized for retrieval.
  5. Embeds every chunk locally using a free HuggingFace sentence-transformer
     (no API key, no rate limit, no cost).
  6. Persists everything into a local Chroma vector database on disk.

Run it directly:
    python ingestion_pipeline.py --data_dir ./data --persist_dir ./chroma_db

After this finishes, run rag_chatbot.py to actually chat with the data.
"""

import argparse
import hashlib
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # free, local, 384-dim
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
COLLECTION_NAME = "womens_health_kb"


def load_pdf(file_path: Path):
    """Load a single PDF and tag every page with metadata."""
    loader = PyMuPDFLoader(str(file_path))
    documents = loader.load()
    total_pages = len(documents)
    for i, doc in enumerate(documents):
        doc.metadata["file_name"] = file_path.name
        doc.metadata["file_type"] = "pdf"
        doc.metadata["page_number"] = i + 1
        doc.metadata["total_pages"] = total_pages
    return documents


def load_docx(file_path: Path):
    """Load a single Word document (.docx) and tag it with metadata.

    Docx2txtLoader returns the whole document as ONE Document object
    (Word files don't have a native page concept the way PDFs do), so we
    tag it accordingly. Chunking below is what actually breaks it into
    retrievable pieces.
    """
    loader = Docx2txtLoader(str(file_path))
    documents = loader.load()
    for doc in documents:
        doc.metadata["file_name"] = file_path.name
        doc.metadata["file_type"] = "docx"
        doc.metadata["page_number"] = 1
        doc.metadata["total_pages"] = 1
    return documents




def make_chunk_id(chunk):
    key = (
        f"{chunk.metadata.get('file_name')}-"
        f"{chunk.metadata.get('page_number')}-"
        f"{chunk.page_content}"
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def ingestion_pipeline(data: str):
    """
    Load every PDF and DOCX file recursively, add metadata, and split into chunks.
    Returns a flat list of chunked Document objects ready for embedding.
    """
    all_chunks = []
    data_path = Path(data)

    pdf_files = list(data_path.rglob("*.pdf"))
    docx_files = list(data_path.rglob("*.docx"))

    print(f"Found {len(pdf_files)} PDF file(s) and {len(docx_files)} DOCX file(s)\n")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    for pdf_file in pdf_files:
        print(f"Processing PDF: {pdf_file.name}")
        try:
            documents = load_pdf(pdf_file)
            chunks = splitter.split_documents(documents)
            all_chunks.extend(chunks)
            print(f"  -> {len(documents)} pages -> {len(chunks)} chunks\n")
        except Exception as e:
            print(f"  X Error processing {pdf_file.name}: {e}\n")

    for docx_file in docx_files:
        print(f"Processing DOCX: {docx_file.name}")
        try:
            documents = load_docx(docx_file)
            chunks = splitter.split_documents(documents)
            all_chunks.extend(chunks)
            print(f"  -> {len(documents)} doc(s) -> {len(chunks)} chunks\n")
        except Exception as e:
            print(f"  X Error processing {docx_file.name}: {e}\n")

    print(f"Total chunks created: {len(all_chunks)}")
    return all_chunks


def embed_and_store(chunks, persist_dir: str):
    """
    Embed every chunk with a local HuggingFace model and persist into Chroma.
    This is the step your original notebook was missing entirely.
    """
    if not chunks:
        print("No chunks to embed — check your data_dir path.")
        return None

    print(f"\nLoading embedding model: {EMBEDDING_MODEL_NAME} (first run downloads it once)")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    # ids = [make_chunk_id(c) for c in chunks]

    print(f"Embedding {len(chunks)} chunks and writing to Chroma at: {persist_dir}")


    vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    persist_directory=persist_dir,
)
    print("Documents in collection:", vectorstore._collection.count())
    print("Done. Vector store is persisted to disk and ready for querying.")
    return vectorstore


def main():
    parser = argparse.ArgumentParser(description="Ingest PDFs/DOCX into a Chroma vector store.")
    parser.add_argument("--data_dir", type=str, default="./data", help="Folder containing PDFs/DOCX")
    parser.add_argument("--persist_dir", type=str, default="./chroma_db", help="Where to save the vector DB")
    args = parser.parse_args()

    Path(args.data_dir).mkdir(parents=True, exist_ok=True)
    chunks = ingestion_pipeline(args.data_dir)

    if chunks:
        print("\n--- Sample Chunk ---\n")
        print(chunks[0].page_content[:300])
        print("\n--- Metadata ---\n")
        print(chunks[0].metadata)

    embed_and_store(chunks, args.persist_dir)
    
    


if __name__ == "__main__":
    main()
print

