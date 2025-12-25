# agents/market_data_agent.py
"""
Market Data Agent for the Finance Assistant.
Fetches real-time stock prices using Yahoo Finance with support for 
US stocks, Indian stocks (NSE/BSE), and global indices.
"""

import yfinance as yf
from datetime import datetime
from typing import Dict, Optional
import logging

# Configure logging
logger = logging.getLogger("MarketDataAgent")

# ============ SYMBOL MAPPING ============
# Maps common names and symbols to Yahoo Finance compatible tickers

SYMBOL_MAP = {
    # Indian Stocks (NSE) - Requires .NS suffix
    'infosys': 'INFY.NS',
    'infy': 'INFY.NS',
    'tcs': 'TCS.NS',
    'tata consultancy': 'TCS.NS',
    'tata consultancy services': 'TCS.NS',
    'reliance': 'RELIANCE.NS',
    'reliance industries': 'RELIANCE.NS',
    'wipro': 'WIPRO.NS',
    'hcl': 'HCLTECH.NS',
    'hcl tech': 'HCLTECH.NS',
    'hdfc bank': 'HDFCBANK.NS',
    'hdfc': 'HDFCBANK.NS',
    'icici bank': 'ICICIBANK.NS',
    'icici': 'ICICIBANK.NS',
    'sbi': 'SBIN.NS',
    'state bank': 'SBIN.NS',
    'bharti airtel': 'BHARTIARTL.NS',
    'airtel': 'BHARTIARTL.NS',
    'kotak': 'KOTAKBANK.NS',
    'kotak mahindra': 'KOTAKBANK.NS',
    'axis bank': 'AXISBANK.NS',
    'axis': 'AXISBANK.NS',
    'maruti': 'MARUTI.NS',
    'maruti suzuki': 'MARUTI.NS',
    'tata motors': 'TATAMOTORS.NS',
    'tata steel': 'TATASTEEL.NS',
    'itc': 'ITC.NS',
    'asian paints': 'ASIANPAINT.NS',
    'bajaj finance': 'BAJFINANCE.NS',
    'larsen': 'LT.NS',
    'l&t': 'LT.NS',
    'sun pharma': 'SUNPHARMA.NS',
    'hindalco': 'HINDALCO.NS',
    'tech mahindra': 'TECHM.NS',
    'power grid': 'POWERGRID.NS',
    'ntpc': 'NTPC.NS',
    'ongc': 'ONGC.NS',
    'ultratech': 'ULTRACEMCO.NS',
    
    # Indian Indices
    'nifty': '^NSEI',
    'nifty50': '^NSEI',
    'nifty 50': '^NSEI',
    'sensex': '^BSESN',
    'bse sensex': '^BSESN',
    'bank nifty': '^NSEBANK',
    'nifty bank': '^NSEBANK',
    
    # US Stocks
    'apple': 'AAPL',
    'aapl': 'AAPL',
    'microsoft': 'MSFT',
    'msft': 'MSFT',
    'google': 'GOOGL',
    'alphabet': 'GOOGL',
    'googl': 'GOOGL',
    'amazon': 'AMZN',
    'amzn': 'AMZN',
    'tesla': 'TSLA',
    'tsla': 'TSLA',
    'nvidia': 'NVDA',
    'nvda': 'NVDA',
    'meta': 'META',
    'facebook': 'META',
    'netflix': 'NFLX',
    'nflx': 'NFLX',
    'intel': 'INTC',
    'intc': 'INTC',
    'amd': 'AMD',
    'tsmc': 'TSM',
    'tsm': 'TSM',
    'qualcomm': 'QCOM',
    'qcom': 'QCOM',
    'broadcom': 'AVGO',
    'avgo': 'AVGO',
    'adobe': 'ADBE',
    'salesforce': 'CRM',
    'cisco': 'CSCO',
    'oracle': 'ORCL',
    'ibm': 'IBM',
    'paypal': 'PYPL',
    'uber': 'UBER',
    'zoom': 'ZM',
    'spotify': 'SPOT',
    
    # US Indices
    'dow': '^DJI',
    'dow jones': '^DJI',
    's&p': '^GSPC',
    's&p 500': '^GSPC',
    'sp500': '^GSPC',
    'nasdaq': '^IXIC',
    'nasdaq composite': '^IXIC',
    'russell': '^RUT',
    'russell 2000': '^RUT',
    
    # Other Global
    'samsung': '005930.KS',
}


def resolve_symbol(query: str) -> Optional[str]:
    """
    Resolve a stock name or symbol to Yahoo Finance compatible ticker.
    
    Args:
        query: Stock name or symbol (e.g., 'Infosys', 'INFY', 'AAPL')
    
    Returns:
        Yahoo Finance compatible symbol or None if not found
    """
    query_lower = query.lower().strip()
    
    # Check direct mapping first
    if query_lower in SYMBOL_MAP:
        return SYMBOL_MAP[query_lower]
    
    # Check if it's already a valid symbol (uppercase)
    if query.isupper() and len(query) >= 2:
        # Could be a direct US ticker
        return query
    
    # Try with .NS suffix for potential Indian stocks
    if query.isupper() and len(query) >= 2:
        return f"{query}.NS"
    
    return None


def get_realtime_price(symbol_or_name: str) -> Dict:
    """
    Fetch real-time stock price from Yahoo Finance.
    
    Args:
        symbol_or_name: Stock symbol or common name (e.g., 'Infosys', 'MSFT')
    
    Returns:
        Structured response with price data or error
    """
    try:
        # Resolve the symbol
        resolved_symbol = resolve_symbol(symbol_or_name)
        
        if not resolved_symbol:
            # Try the input directly as a symbol
            resolved_symbol = symbol_or_name.upper()
        
        logger.info(f"Fetching price for: {resolved_symbol}")
        
        # Fetch from Yahoo Finance
        ticker = yf.Ticker(resolved_symbol)
        
        # Get current price info (fast method)
        info = ticker.info
        
        if not info or 'regularMarketPrice' not in info:
            # Fallback: try getting last available price from history
            hist = ticker.history(period="1d")
            if hist.empty:
                return {
                    "status": "data_unavailable",
                    "message": f"Market data for {symbol_or_name} is currently unavailable.",
                    "symbol": resolved_symbol
                }
            
            current_price = float(hist['Close'].iloc[-1])
            currency = info.get('currency', 'USD')
        else:
            current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
            currency = info.get('currency', 'USD')
        
        # Get additional info
        exchange = info.get('exchange', 'Unknown')
        market_state = info.get('marketState', 'Unknown')
        previous_close = info.get('previousClose', 0)
        day_change = current_price - previous_close if previous_close else 0
        day_change_pct = (day_change / previous_close * 100) if previous_close else 0
        
        return {
            "status": "success",
            "symbol": resolved_symbol,
            "name": info.get('shortName', info.get('longName', symbol_or_name)),
            "price": round(current_price, 2),
            "currency": currency,
            "exchange": exchange,
            "previous_close": round(previous_close, 2) if previous_close else None,
            "day_change": round(day_change, 2),
            "day_change_percent": round(day_change_pct, 2),
            "market_state": market_state,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching price for {symbol_or_name}: {e}")
        return {
            "status": "data_unavailable",
            "message": f"Market data for {symbol_or_name} is currently unavailable.",
            "error": str(e)
        }


def format_price_response(data: Dict) -> str:
    """
    Format price data into a readable string for the LLM context.
    
    Args:
        data: Response from get_realtime_price()
    
    Returns:
        Formatted string for LLM context
    """
    if data.get("status") != "success":
        return data.get("message", "Market data is currently unavailable.")
    
    change_symbol = "+" if data['day_change'] >= 0 else ""
    
    return f"""
REAL-TIME MARKET DATA (from Yahoo Finance):
- Stock: {data['name']} ({data['symbol']})
- Current Price: {data['currency']} {data['price']}
- Day Change: {change_symbol}{data['day_change']} ({change_symbol}{data['day_change_percent']}%)
- Previous Close: {data['currency']} {data['previous_close']}
- Exchange: {data['exchange']}
- Market State: {data['market_state']}
- Timestamp: {data['timestamp']}
"""


# ============ TEST ============
if __name__ == "__main__":
    # Test with Infosys
    print("=" * 50)
    print("Testing Infosys (Indian Stock):")
    result = get_realtime_price("Infosys")
    print(result)
    print(format_price_response(result))
    
    # Test with Microsoft
    print("=" * 50)
    print("Testing Microsoft (US Stock):")
    result = get_realtime_price("Microsoft")
    print(result)
    print(format_price_response(result))
    
    # Test with NIFTY
    print("=" * 50)
    print("Testing NIFTY 50 (Index):")
    result = get_realtime_price("nifty 50")
    print(result)
    print(format_price_response(result))
