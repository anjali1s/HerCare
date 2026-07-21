"""
rag_chatbot.py
==============
Loads the Chroma vector store built by ingestion_pipeline.py, retrieves the
most relevant chunks for a user question, and sends them + the question to a
free LLM (Groq) to generate a grounded answer.

Setup (one-time):
    1. pip install -r requirements.txt
    2. Get a free key: https://console.groq.com/keys
    3. Copy .env.example to .env and paste your key in as GROQ_API_KEY=...
    4. Run ingestion_pipeline.py first to build ./chroma_db

Run:
    python rag_chatbot.py
"""

import os
import sys
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ---------------------------------------------------------------------------
# Config — keep in sync with ingestion_pipeline.py
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "womens_health_kb"
PERSIST_DIR = "./chroma_db"

# Groq free-tier model. "llama-3.3-70b-versatile" is strong and free;
# swap to "llama-3.1-8b-instant" if you want faster/lighter responses.
LLM_MODEL_NAME = "llama-3.3-70b-versatile"

TOP_K = 4  # how many chunks to retrieve per question


SYSTEM_PROMPT = """
You are a helpful and friendly women's health assistant.

Answer the user's question naturally like a normal conversation.

Use the provided context as your source of information, but never mention:
- documents
- knowledge base
- context
- sources
- retrieved information

Do not say phrases like:
"According to the document"
"Based on the provided information"
"From the knowledge base"

Instead, directly answer the user's question.

If the information is not available in the provided context, say:
"I don't have enough information about that."

Answer style rules:
- Do not mention documents, context, knowledge base, or sources.
- Do not say "According to the document" or similar phrases.
- Keep answers easy to read.
- Use bullet points whenever there are 2 or more related facts.
- Use numbered lists for steps or instructions.
- Use short paragraphs for simple explanations.
- Avoid long paragraphs.

Examples of formatting:
For symptoms, causes, benefits, risks, or facts:

- Point one
- Point two
- Point three

For explanations:
Give a short introduction paragraph, then use bullet points if needed.


Medical safety rules:
- You are not a doctor and must not provide a diagnosis.
- Never predict, confirm, or assume a disease or medical condition.
- Provide general health information only.
- If a question involves serious symptoms, emergency situations, diagnosis, medication decisions, or complex medical concerns, advise the user to consult a qualified healthcare professional.
- Encourage users to seek medical help when symptoms are severe, unusual, worsening, or causing concern.
Keep answers clear, conversational, and easy to understand.

Context:
{context}
"""

def load_api_key() -> str:
    """
    Load GROQ_API_KEY from .env / environment and fail loudly with a clear
    message if it's missing — this is the #1 cause of "API key not working"
    bugs: the .env file exists but was never loaded, or the variable name
    doesn't match what the library expects.
    """
    load_dotenv()  # reads .env in the current working directory
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        print(
            "\nERROR: GROQ_API_KEY not found.\n"
            "Fix steps:\n"
            "  1. Copy .env.example to a file named exactly '.env'\n"
            "  2. Put your real key in it as: GROQ_API_KEY=gsk_xxxxxxxx\n"
            "  3. Make sure .env is in the SAME folder you run this script from\n"
            "  4. Restart your terminal/kernel after creating .env\n"
        )
        sys.exit(1)

    return api_key


def build_rag_chain():
    api_key = load_api_key()

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
    )

    print("Collection count:", vectorstore._collection.count())
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    llm = ChatGroq(
        model=LLM_MODEL_NAME,
        api_key=api_key,
        temperature=0.2,   # lower = more grounded/less creative, good for health info
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    def format_docs(docs):
        return "\n\n".join(
            f"[Source: {d.metadata.get('file_name', 'unknown')} | "
            f"page {d.metadata.get('page_number', '?')}]\n{d.page_content}"
            for d in docs
        )

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever


# Create the RAG chain once when the server starts
rag_chain, retriever = build_rag_chain()


def ask_question(question: str):
    """
    Takes a user question and returns the RAG answer.
    This function will be called by the website.
    """

    if not question.strip():
        return "Please enter a question."

    try:
        answer = rag_chain.invoke(question)
        return answer

    except Exception as e:
        return f"Error: {str(e)}"

def main():
    print("Chatbot ready.\n")
    print("Ready. Type a question (or 'exit' to quit).\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        try:
            answer = rag_chain.invoke(question)
        except Exception as e:
            print(f"\n[Error calling the LLM: {e}]\n")
            continue

        print(f"\nAssistant: {answer}\n")

        # Optional: show which sources were used, for transparency
        sources = retriever.invoke(question)

        
        seen = set()
        source_lines = []
        print("\n===== RETRIEVED TEXT =====")
        for s in sources:
          print("\nFILE:", s.metadata.get("file_name"))
          print("PAGE:", s.metadata.get("page_number"))
          print(s.page_content[:500])
          print("----------------------")
        print()



# Load RAG once when FastAPI starts
rag_chain, retriever = build_rag_chain()


def ask_question(question: str):

    try:
        answer = rag_chain.invoke(question)
        return answer

    except Exception as e:
        return f"Error: {str(e)}"
    

    
if __name__ == "__main__":
    main()


