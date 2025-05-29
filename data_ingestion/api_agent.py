# agents/api_agent.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf
import os
import requests

app = FastAPI(title="API Agent - Market Data")

# Load AlphaVantage API key from env
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

class StockRequest(BaseModel):
    symbol: str
    start_date: str = None  # Optional, YYYY-MM-DD
    end_date: str = None    # Optional, YYYY-MM-DD

@app.get("/")
def root():
    return {"message": "API Agent is running"}

@app.post("/yfinance/historical")
def get_historical_data(req: StockRequest):
    try:
        ticker = yf.Ticker(req.symbol)
        hist = ticker.history(start=req.start_date, end=req.end_date)
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data found")
        # Convert to dict for JSON serialization
        return hist.reset_index().to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alphavantage/quote/{symbol}")
def get_realtime_quote(symbol: str):
    if not ALPHAVANTAGE_API_KEY:
        raise HTTPException(status_code=500, detail="AlphaVantage API key not set")
    url = (
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE"
        f"&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="AlphaVantage API error")
    data = response.json()
    if "Global Quote" not in data:
        raise HTTPException(status_code=404, detail="No quote found")
    return data["Global Quote"]
