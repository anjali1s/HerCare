from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse

from rag_chatbot import ask_question

import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"


app = FastAPI(
    title="RAG Chatbot API"
)


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return FileResponse("templates/bot.html")


@app.post("/chat")
def chat(data: Question):

    answer = ask_question(data.question)

    return {
        "answer": answer
    }

#uvicorn app:app --reload
 