"""
rag_chatbot.py

RAG chatbot loader for HerCare Plus.

Flow:

Documents
    |
    v
ingestion_pipeline.py
    |
    v
chroma_db/
    |
    v
rag_chatbot.py
    |
    v
FastAPI chat API
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



# =====================================================
# CONFIG
# =====================================================


os.environ["ANONYMIZED_TELEMETRY"] = "False"

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


COLLECTION_NAME = (
    "womens_health_kb"
)


PERSIST_DIR = (
    "./chroma_db"
)


LLM_MODEL_NAME = (
    "llama-3.3-70b-versatile"
)


TOP_K = 4




# =====================================================
# SYSTEM PROMPT
# =====================================================


SYSTEM_PROMPT = """

You are HerCare Plus, a friendly women's health assistant.

Answer naturally and clearly.

Rules:

- Provide general health information only.
- Do not diagnose diseases.
- Do not confirm medical conditions.
- Do not prescribe medicines.

If symptoms are serious, unusual,
or getting worse, advise consulting
a qualified healthcare professional.


Formatting:

Use bullet points for multiple facts.

Use numbered lists for steps.

Keep answers simple and easy to understand.


If information is unavailable say:

"I don't have enough information about that."


Context:

{context}

"""





# =====================================================
# LOAD GROQ KEY
# =====================================================


def load_api_key():


    load_dotenv()


    api_key = os.getenv(
        "GROQ_API_KEY"
    )


    if not api_key:


        print(
            """
ERROR:
GROQ_API_KEY missing.

Create .env file:

GROQ_API_KEY=your_key_here

"""
        )


        sys.exit(1)



    return api_key







# =====================================================
# BUILD RAG
# =====================================================


def build_rag_chain():


    api_key = load_api_key()



    embeddings = HuggingFaceEmbeddings(

        model_name=
        EMBEDDING_MODEL_NAME

    )




    vectorstore = Chroma(

        collection_name=
        COLLECTION_NAME,

        embedding_function=
        embeddings,

        persist_directory=
        PERSIST_DIR

    )



    print(
        "Chroma documents:",
        vectorstore._collection.count()
    )




    retriever = vectorstore.as_retriever(

        search_kwargs={

            "k":TOP_K

        }

    )





    llm = ChatGroq(

        model=
        LLM_MODEL_NAME,

        api_key=
        api_key,

        temperature=0.2

    )





    prompt = ChatPromptTemplate.from_messages(

        [

            (
                "system",
                SYSTEM_PROMPT
            ),

            (
                "human",
                "{question}"
            )

        ]

    )





    def format_docs(docs):


        return "\n\n".join(

            doc.page_content

            for doc in docs

        )







    rag_chain = (

        {

            "context":
            retriever | format_docs,

            "question":
            RunnablePassthrough()

        }

        |

        prompt

        |

        llm

        |

        StrOutputParser()

    )



    return rag_chain, retriever







# =====================================================
# LOAD ONCE ONLY
# =====================================================


rag_chain, retriever = build_rag_chain()







# =====================================================
# FASTAPI FUNCTION
# =====================================================


def ask_question(question:str):


    if not question.strip():

        return (
            "Please enter a question."
        )



    try:


        answer = rag_chain.invoke(

            question

        )


        return answer



    except Exception as e:


        return (
            f"Error: {str(e)}"
        )







# =====================================================
# OPTIONAL TERMINAL TEST
# =====================================================


def main():


    print(
        "HerCare Plus RAG ready."
    )



    while True:


        question = input(
            "\nYou: "
        )



        if question.lower() in [

            "exit",
            "quit"

        ]:

            break




        answer = ask_question(

            question

        )



        print(

            "\nAssistant:",

            answer

        )







if __name__ == "__main__":


    main()