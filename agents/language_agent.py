import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from agents.retriever_agent import build_vector_store, retrieve_top_chunks
from agents.market_data_agent import get_realtime_price, format_price_response, resolve_symbol

# Load environment variables
load_dotenv(".env")

# Get OpenRouter API key from .env
openrouter_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

# Define base URL for OpenRouter
openai_base_url = "https://openrouter.ai/api/v1"

llm = ChatOpenAI(
    temperature=0.2,
    api_key=openrouter_key,
    base_url=openai_base_url,
    model="mistralai/mistral-7b-instruct"
)

# Build or load vectorstore once at startup
vectorstore = build_vector_store([
    "data_ingestion/sample_earnings.txt",
])

# ============ HARDENED SYSTEM PROMPT ============
SYSTEM_PROMPT = """You are a financial assistant.
You MUST NOT answer real-time stock price or market questions unless market agent data is provided in the context.
You are only allowed to summarize or format the provided market data.
Do NOT say you lack internet or real-time access.
Do NOT say "I don't have access to real-time data".
Do NOT speculate or guess prices.
When market data IS provided, use the exact numbers from the data to give accurate, helpful answers."""

# Keywords that indicate a MARKET DATA query (requires tool grounding)
MARKET_DATA_KEYWORDS = [
    'price', 'stock price', 'share price', 'current price', 'trading at',
    'today', 'now', 'current', 'latest', 'live', 'real-time',
    'market cap', 'volume', 'pe ratio', 'eps',
    'nifty', 'sensex', 'dow', 'nasdaq', 's&p',
    'how much is', 'what is the price', 'price of',
    'movement', 'up', 'down', 'gained', 'lost',
]

# Stock name patterns for extraction
STOCK_PATTERNS = [
    # Indian Stocks
    'infosys', 'tcs', 'reliance', 'wipro', 'hcl', 'hdfc', 'icici', 'sbi',
    'airtel', 'bharti', 'kotak', 'axis', 'maruti', 'tata motors', 'tata steel',
    'itc', 'asian paints', 'bajaj', 'sun pharma', 'tech mahindra', 'ntpc', 'ongc',
    # US Stocks
    'apple', 'microsoft', 'google', 'amazon', 'tesla', 'nvidia', 'meta',
    'netflix', 'intel', 'amd', 'tsmc', 'qualcomm', 'adobe', 'salesforce',
    'cisco', 'oracle', 'ibm', 'paypal', 'uber', 'zoom', 'spotify',
    # Indices
    'nifty', 'sensex', 'dow', 'nasdaq', 's&p',
]


def extract_stock_name(question: str) -> str:
    """Extract stock/company name from question."""
    question_lower = question.lower()
    
    # Check for known stock patterns
    for pattern in STOCK_PATTERNS:
        if pattern in question_lower:
            return pattern
    
    # Try to find ticker pattern like $AAPL or AAPL
    ticker_match = re.search(r'\$?([A-Z]{2,6})', question)
    if ticker_match:
        return ticker_match.group(1)
    
    return None


def is_market_data_query(question: str) -> bool:
    """Check if question requires real-time market data."""
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in MARKET_DATA_KEYWORDS)


def answer_question(question: str) -> str:
    """
    Answer a financial question with tool-first execution for market data.
    
    Flow:
    1. Detect if market data is needed
    2. If yes, call market_data_agent FIRST
    3. If market data unavailable, return structured fallback
    4. If market data available, pass to LLM for formatting
    5. For non-market queries, use RAG normally
    """
    import logging
    logger = logging.getLogger("LanguageAgent")
    
    # Detect query type
    requires_market_data = is_market_data_query(question)
    stock_name = extract_stock_name(question)
    
    logger.info(f"Query: {question[:50]}")
    logger.info(f"Requires market data: {requires_market_data}, Stock: {stock_name}")
    
    # ============ TOOL-FIRST EXECUTION FOR MARKET DATA ============
    market_context = None
    market_data_fetched = False
    
    if requires_market_data and stock_name:
        logger.info(f"Calling market_data_agent for {stock_name}")
        # Call market data agent FIRST
        price_data = get_realtime_price(stock_name)
        logger.info(f"Market data status: {price_data.get('status')}")
        
        if price_data.get("status") == "success":
            market_context = format_price_response(price_data)
            market_data_fetched = True
            logger.info(f"Market data fetched successfully: {price_data.get('price')}")
        else:
            # Market data unavailable - bypass LLM entirely
            logger.warning("Market data unavailable")
            return "Market data is currently unavailable."
    
    elif requires_market_data and not stock_name:
        # Market query but no stock identified
        logger.warning("Market query but no stock identified")
        return "Please specify which stock or index you'd like information about."
    
    # ============ GET RAG CONTEXT ============
    relevant_chunks = retrieve_top_chunks(question, vectorstore)
    rag_context = "\n".join(relevant_chunks) if relevant_chunks else ""
    
    # ============ BUILD CONTEXT ============
    if market_context:
        full_context = f"""{market_context}

ADDITIONAL CONTEXT:
{rag_context if rag_context else 'No additional data available.'}"""
    else:
        full_context = rag_context if rag_context else "No specific data available."
    
    # ============ LLM INVOCATION ============
    user_prompt = f"""Based ONLY on the following context, answer the user's question.

Context:
{full_context}

Question: {question}

Instructions:
- Use the EXACT numbers from the market data if provided.
- Be specific and accurate.
- Do not make up any data.

Answer:"""

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ])
    
    return response.content


# ============ TEST ============
if __name__ == "__main__":
    print("=" * 60)
    print("Test 1: What is the current stock price of Infosys?")
    print("-" * 60)
    print(answer_question("What is the current stock price of Infosys?"))
    
    print("\n" + "=" * 60)
    print("Test 2: What does Infosys do?")
    print("-" * 60)
    print(answer_question("What does Infosys do?"))
    
    print("\n" + "=" * 60)
    print("Test 3: What is the current price of Microsoft?")
    print("-" * 60)
    print(answer_question("What is the current price of Microsoft?"))
