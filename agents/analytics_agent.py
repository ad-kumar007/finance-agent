# agents/analytics_agent.py
"""
Technical Analysis Agent for the Finance Assistant.
Provides portfolio analytics, technical indicators, and risk exposure analysis.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta


def get_stock_data(symbol: str, period: str = "3mo") -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSMC')
        period: Time period for data ('1mo', '3mo', '6mo', '1y', '2y')
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return pd.DataFrame()
        return hist
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    RSI measures momentum by comparing recent gains vs losses.
    - RSI > 70: Overbought (potential sell signal)
    - RSI < 30: Oversold (potential buy signal)
    
    Args:
        prices: Series of closing prices
        period: RSI calculation period (default 14)
    
    Returns:
        Series of RSI values
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_moving_averages(prices: pd.Series, short: int = 20, long: int = 50) -> Dict[str, pd.Series]:
    """
    Calculate Simple Moving Averages (SMA).
    
    Args:
        prices: Series of closing prices
        short: Short-term MA period (default 20)
        long: Long-term MA period (default 50)
    
    Returns:
        Dict with 'sma_short' and 'sma_long' Series
    """
    return {
        'sma_short': prices.rolling(window=short).mean(),
        'sma_long': prices.rolling(window=long).mean()
    }


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
    """
    Calculate Bollinger Bands.
    
    Bollinger Bands show volatility and potential price breakouts.
    
    Args:
        prices: Series of closing prices
        period: Moving average period (default 20)
        std_dev: Standard deviation multiplier (default 2.0)
    
    Returns:
        Dict with 'middle', 'upper', and 'lower' bands
    """
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    return {
        'middle': middle,
        'upper': middle + (std * std_dev),
        'lower': middle - (std * std_dev)
    }


def calculate_volatility(prices: pd.Series, period: int = 20) -> float:
    """
    Calculate annualized volatility.
    
    Args:
        prices: Series of closing prices
        period: Period for volatility calculation
    
    Returns:
        Annualized volatility as a percentage
    """
    returns = prices.pct_change().dropna()
    volatility = returns.rolling(window=period).std().iloc[-1]
    annualized = volatility * np.sqrt(252) * 100  # 252 trading days
    return round(annualized, 2)


def calculate_beta(stock_prices: pd.Series, market_prices: pd.Series, period: int = 60) -> float:
    """
    Calculate Beta (market sensitivity).
    
    Beta measures how much a stock moves relative to the market.
    - Beta > 1: More volatile than market
    - Beta < 1: Less volatile than market
    - Beta = 1: Moves with market
    
    Args:
        stock_prices: Series of stock closing prices
        market_prices: Series of market index closing prices (e.g., SPY)
        period: Period for calculation
    
    Returns:
        Beta value
    """
    stock_returns = stock_prices.pct_change().dropna().tail(period)
    market_returns = market_prices.pct_change().dropna().tail(period)
    
    # Align the series
    aligned = pd.concat([stock_returns, market_returns], axis=1).dropna()
    if len(aligned) < 10:
        return 1.0  # Default to market beta if insufficient data
    
    covariance = aligned.iloc[:, 0].cov(aligned.iloc[:, 1])
    variance = aligned.iloc[:, 1].var()
    
    if variance == 0:
        return 1.0
    
    return round(covariance / variance, 2)


def get_technical_summary(symbol: str) -> Dict:
    """
    Generate a comprehensive technical analysis summary for a stock.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Dict containing all technical indicators and signals
    """
    data = get_stock_data(symbol, period="6mo")
    
    if data.empty:
        return {"error": f"No data found for {symbol}"}
    
    close = data['Close']
    current_price = close.iloc[-1]
    
    # Calculate indicators
    rsi = calculate_rsi(close)
    current_rsi = rsi.iloc[-1]
    
    mas = calculate_moving_averages(close)
    sma_20 = mas['sma_short'].iloc[-1]
    sma_50 = mas['sma_long'].iloc[-1]
    
    bb = calculate_bollinger_bands(close)
    bb_upper = bb['upper'].iloc[-1]
    bb_lower = bb['lower'].iloc[-1]
    
    volatility = calculate_volatility(close)
    
    # Get market data for beta calculation
    market_data = get_stock_data("SPY", period="6mo")
    if not market_data.empty:
        beta = calculate_beta(close, market_data['Close'])
    else:
        beta = 1.0
    
    # Determine signals
    rsi_signal = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
    trend_signal = "Bullish" if sma_20 > sma_50 else "Bearish" if sma_20 < sma_50 else "Neutral"
    bb_signal = "Near Upper" if current_price > bb_upper * 0.98 else "Near Lower" if current_price < bb_lower * 1.02 else "Within Bands"
    
    # Price changes
    price_1d = ((current_price - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
    price_1w = ((current_price - close.iloc[-5]) / close.iloc[-5]) * 100 if len(close) > 5 else 0
    price_1m = ((current_price - close.iloc[-20]) / close.iloc[-20]) * 100 if len(close) > 20 else 0
    
    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "price_change_1d": round(price_1d, 2),
        "price_change_1w": round(price_1w, 2),
        "price_change_1m": round(price_1m, 2),
        "rsi": round(current_rsi, 2),
        "rsi_signal": rsi_signal,
        "sma_20": round(sma_20, 2),
        "sma_50": round(sma_50, 2),
        "trend_signal": trend_signal,
        "bollinger_upper": round(bb_upper, 2),
        "bollinger_lower": round(bb_lower, 2),
        "bollinger_signal": bb_signal,
        "volatility": volatility,
        "beta": beta,
        "risk_level": "High" if volatility > 30 or beta > 1.5 else "Medium" if volatility > 20 or beta > 1.0 else "Low"
    }


def analyze_risk_exposure(symbols: List[str], region: Optional[str] = None) -> Dict:
    """
    Analyze risk exposure for a portfolio of stocks.
    
    Args:
        symbols: List of stock ticker symbols
        region: Optional region filter (e.g., 'Asia', 'US', 'Europe')
    
    Returns:
        Dict containing portfolio risk analysis
    """
    # Regional stock mappings (simplified)
    asia_tech_stocks = ['TSM', '2330.TW', 'SSNLF', '005930.KS', 'BABA', 'BIDU', '9988.HK']
    us_tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'INTC']
    europe_stocks = ['ASML', 'SAP', 'SHOP']
    
    # Filter by region if specified
    if region:
        region_lower = region.lower()
        if 'asia' in region_lower:
            symbols = [s for s in symbols if s.upper() in [x.upper() for x in asia_tech_stocks]] or ['TSM']
        elif 'us' in region_lower or 'america' in region_lower:
            symbols = [s for s in symbols if s.upper() in [x.upper() for x in us_tech_stocks]] or ['AAPL']
        elif 'europe' in region_lower:
            symbols = [s for s in symbols if s.upper() in [x.upper() for x in europe_stocks]] or ['ASML']
    
    if not symbols:
        symbols = ['TSM']  # Default to TSMC for Asia tech
    
    portfolio_analysis = []
    total_volatility = 0
    total_beta = 0
    
    for symbol in symbols:
        analysis = get_technical_summary(symbol)
        if "error" not in analysis:
            portfolio_analysis.append(analysis)
            total_volatility += analysis.get('volatility', 0)
            total_beta += analysis.get('beta', 1.0)
    
    if not portfolio_analysis:
        return {"error": "Could not analyze any stocks in the portfolio"}
    
    avg_volatility = total_volatility / len(portfolio_analysis)
    avg_beta = total_beta / len(portfolio_analysis)
    
    # Determine overall risk
    high_risk_count = sum(1 for a in portfolio_analysis if a.get('risk_level') == 'High')
    
    if high_risk_count > len(portfolio_analysis) / 2:
        overall_risk = "High"
        risk_summary = "Portfolio has significant exposure to volatile assets. Consider diversification."
    elif avg_volatility > 25:
        overall_risk = "Medium-High"
        risk_summary = "Above-average volatility. Monitor positions closely."
    elif avg_beta > 1.2:
        overall_risk = "Medium"
        risk_summary = "Portfolio is more sensitive to market movements than average."
    else:
        overall_risk = "Low-Medium"
        risk_summary = "Portfolio has moderate risk exposure."
    
    return {
        "region": region or "Global",
        "stocks_analyzed": len(portfolio_analysis),
        "stocks": portfolio_analysis,
        "average_volatility": round(avg_volatility, 2),
        "average_beta": round(avg_beta, 2),
        "overall_risk_level": overall_risk,
        "risk_summary": risk_summary,
        "high_risk_positions": [a['symbol'] for a in portfolio_analysis if a.get('risk_level') == 'High'],
        "generated_at": datetime.now().isoformat()
    }


def get_portfolio_analytics(symbols: List[str]) -> Dict:
    """
    Get comprehensive portfolio analytics.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        Dict containing full portfolio analysis
    """
    if not symbols:
        return {"error": "No symbols provided"}
    
    analyses = []
    for symbol in symbols:
        analysis = get_technical_summary(symbol)
        if "error" not in analysis:
            analyses.append(analysis)
    
    if not analyses:
        return {"error": "Could not analyze any stocks"}
    
    # Aggregate statistics
    bullish = sum(1 for a in analyses if a.get('trend_signal') == 'Bullish')
    bearish = sum(1 for a in analyses if a.get('trend_signal') == 'Bearish')
    overbought = sum(1 for a in analyses if a.get('rsi_signal') == 'Overbought')
    oversold = sum(1 for a in analyses if a.get('rsi_signal') == 'Oversold')
    
    return {
        "total_positions": len(analyses),
        "bullish_trend": bullish,
        "bearish_trend": bearish,
        "neutral_trend": len(analyses) - bullish - bearish,
        "overbought_count": overbought,
        "oversold_count": oversold,
        "individual_analyses": analyses,
        "portfolio_sentiment": "Bullish" if bullish > bearish else "Bearish" if bearish > bullish else "Mixed",
        "generated_at": datetime.now().isoformat()
    }


# Test routine
if __name__ == "__main__":
    print("Testing Analytics Agent...")
    
    # Test single stock analysis
    print("\n=== TSMC Technical Analysis ===")
    tsm_analysis = get_technical_summary("TSM")
    for key, value in tsm_analysis.items():
        print(f"  {key}: {value}")
    
    # Test risk exposure
    print("\n=== Asia Tech Risk Exposure ===")
    risk = analyze_risk_exposure(["TSM", "BABA"], region="Asia")
    print(f"  Overall Risk: {risk.get('overall_risk_level')}")
    print(f"  Summary: {risk.get('risk_summary')}")
    
    # Test portfolio analytics
    print("\n=== Portfolio Analytics ===")
    portfolio = get_portfolio_analytics(["AAPL", "MSFT", "TSM"])
    print(f"  Sentiment: {portfolio.get('portfolio_sentiment')}")
    print(f"  Bullish: {portfolio.get('bullish_trend')}, Bearish: {portfolio.get('bearish_trend')}")
