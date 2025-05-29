from fastapi import FastAPI
from pydantic import BaseModel

from agents.language_agent import answer_question

app = FastAPI()

class Question(BaseModel):
    question: str

@app.post("/ask_llm")
async def ask_llm(data: Question):
    answer = answer_question(data.question)
    return {
        "question": data.question,
        "answer": answer
    }
