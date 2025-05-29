import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from agents.retriever_agent import build_vector_store, retrieve_top_chunks

# Load environment variables
load_dotenv(".env")

openrouter_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

# Explicitly pass the API key here
llm = ChatOpenAI(
    temperature=0.2,
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="mistralai/mistral-7b-instruct",
    openai_api_key=openrouter_key
)

# Build or load vectorstore once at startup
vectorstore = build_vector_store([
    "data_ingestion/sample_earnings.txt",
    # add other files or scraped content here
])

def answer_question(question: str) -> str:
    relevant_chunks = retrieve_top_chunks(question, vectorstore)
    context = "\n".join(relevant_chunks)

    prompt = f"""You are a financial analyst. Use the following context to answer the question.

Context:
{context}

Question: {question}
"""

    # Use .invoke() per deprecation warning instead of .call()
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


if __name__ == "__main__":
    test_question = "Did TSMC beat earnings expectations?"
    print("Question:", test_question)
    print("Answer:", answer_question(test_question))
