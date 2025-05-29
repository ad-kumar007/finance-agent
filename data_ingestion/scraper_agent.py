# data_ingestion/scraper_agent.py

import feedparser
import requests
from bs4 import BeautifulSoup

def get_earnings_news(ticker):
    rss_url = f"https://news.google.com/rss/search?q={ticker}+earnings"
    
    try:
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            return {"ticker": ticker, "error": "No news found in RSS feed."}

        all_headlines = []
        relevant_headlines = []

        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link
            all_headlines.append(title)

            try:
                response = requests.get(link, timeout=5)
                soup = BeautifulSoup(response.content, "html.parser")
                text = soup.get_text().lower()
            except Exception as e:
                continue  # Skip to next article if this one fails

            if any(keyword in text for keyword in ["beat", "beats", "miss", "missed", "surprise", "falls short"]):
                relevant_headlines.append(title)

        return {
            "ticker": ticker,
            "relevant_earnings_news": relevant_headlines or ["No strong signals found."],
            "all_news": all_headlines
        }

    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

# For testing
if __name__ == "__main__":
    print(get_earnings_news("TSMC"))
    print(get_earnings_news("Samsung"))
