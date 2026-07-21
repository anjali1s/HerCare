from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    collection_name="test",
    persist_directory="./test_db",
    embedding_function=embeddings,
)

db.add_texts(["Machine learning is AI."])

print("Success!")