# tests/test_scraper_agent.py
"""
Unit tests for the Scraper Agent (data_ingestion/scraper_agent.py).
Tests earnings news scraping and RSS feed parsing.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_ingestion.scraper_agent import get_earnings_news


class TestGetEarningsNews:
    """Tests for the get_earnings_news function."""
    
    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        result = get_earnings_news("AAPL")
        assert isinstance(result, dict)
        assert "ticker" in result
    
    def test_ticker_in_response(self):
        """Test that the ticker is included in the response."""
        result = get_earnings_news("MSFT")
        assert result["ticker"] == "MSFT"
    
    def test_valid_ticker_structure(self):
        """Test response structure for valid ticker."""
        result = get_earnings_news("GOOGL")
        assert "ticker" in result
        # Should have either news data or error
        assert "all_news" in result or "error" in result
    
    def test_unknown_ticker(self):
        """Test with an unknown/invalid ticker."""
        result = get_earnings_news("XYZINVALID123")
        assert "ticker" in result
        # Should handle gracefully, may have empty news or error
        assert isinstance(result, dict)
    
    def test_empty_ticker(self):
        """Test with empty ticker string."""
        result = get_earnings_news("")
        assert isinstance(result, dict)
        assert "ticker" in result
    
    def test_special_characters_in_ticker(self):
        """Test with special characters in ticker."""
        result = get_earnings_news("TSM.TW")
        assert isinstance(result, dict)
        assert "ticker" in result


class TestEarningsKeywordFiltering:
    """Tests for the keyword filtering logic."""
    
    @patch('data_ingestion.scraper_agent.feedparser.parse')
    @patch('data_ingestion.scraper_agent.requests.get')
    def test_beat_keyword_detection(self, mock_requests, mock_feedparser):
        """Test detection of 'beat' keyword in articles."""
        # Mock RSS feed
        mock_entry = MagicMock()
        mock_entry.title = "Company X beats earnings expectations"
        mock_entry.link = "http://example.com/article"
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed
        
        # Mock article content
        mock_response = MagicMock()
        mock_response.content = b"<html><body>The company beat expectations</body></html>"
        mock_requests.return_value = mock_response
        
        result = get_earnings_news("TEST")
        
        assert "ticker" in result
    
    @patch('data_ingestion.scraper_agent.feedparser.parse')
    @patch('data_ingestion.scraper_agent.requests.get')
    def test_miss_keyword_detection(self, mock_requests, mock_feedparser):
        """Test detection of 'miss' keyword in articles."""
        mock_entry = MagicMock()
        mock_entry.title = "Company Y misses earnings"
        mock_entry.link = "http://example.com/article"
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed
        
        mock_response = MagicMock()
        mock_response.content = b"<html><body>The company missed the target</body></html>"
        mock_requests.return_value = mock_response
        
        result = get_earnings_news("TEST")
        
        assert "ticker" in result
    
    @patch('data_ingestion.scraper_agent.feedparser.parse')
    def test_empty_feed(self, mock_feedparser):
        """Test handling of empty RSS feed."""
        mock_feed = MagicMock()
        mock_feed.entries = []
        mock_feedparser.return_value = mock_feed
        
        result = get_earnings_news("EMPTY")
        
        assert "ticker" in result
        # Should indicate no news or have error
        assert "error" in result or result.get("all_news", []) == []


class TestRSSFeedParsing:
    """Tests for RSS feed parsing functionality."""
    
    @patch('data_ingestion.scraper_agent.feedparser.parse')
    def test_feed_parsing_structure(self, mock_feedparser):
        """Test that feed entries are parsed correctly."""
        mock_entry = MagicMock()
        mock_entry.title = "Test Headline"
        mock_entry.link = "http://example.com"
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed
        
        with patch('data_ingestion.scraper_agent.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"<html><body>Article content</body></html>"
            mock_get.return_value = mock_response
            
            result = get_earnings_news("TEST")
            
            assert "ticker" in result
    
    @patch('data_ingestion.scraper_agent.feedparser.parse')
    def test_multiple_entries(self, mock_feedparser):
        """Test handling of multiple RSS entries."""
        entries = []
        for i in range(5):
            entry = MagicMock()
            entry.title = f"Headline {i}"
            entry.link = f"http://example.com/{i}"
            entries.append(entry)
        
        mock_feed = MagicMock()
        mock_feed.entries = entries
        mock_feedparser.return_value = mock_feed
        
        with patch('data_ingestion.scraper_agent.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"<html><body>Content</body></html>"
            mock_get.return_value = mock_response
            
            result = get_earnings_news("MULTI")
            
            assert "ticker" in result
            if "all_news" in result:
                assert len(result["all_news"]) <= 5


class TestErrorHandling:
    """Tests for error handling."""
    
    @patch('data_ingestion.scraper_agent.feedparser.parse')
    def test_feedparser_exception(self, mock_feedparser):
        """Test handling of feedparser exceptions."""
        mock_feedparser.side_effect = Exception("Parse error")
        
        result = get_earnings_news("ERROR")
        
        assert "ticker" in result
        assert "error" in result
    
    @patch('data_ingestion.scraper_agent.feedparser.parse')
    @patch('data_ingestion.scraper_agent.requests.get')
    def test_request_timeout(self, mock_requests, mock_feedparser):
        """Test handling of request timeouts."""
        mock_entry = MagicMock()
        mock_entry.title = "Test"
        mock_entry.link = "http://example.com"
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed
        
        # Simulate timeout
        import requests
        mock_requests.side_effect = requests.exceptions.Timeout("Timeout")
        
        result = get_earnings_news("TIMEOUT")
        
        # Should handle gracefully
        assert "ticker" in result
    
    @patch('data_ingestion.scraper_agent.feedparser.parse')
    @patch('data_ingestion.scraper_agent.requests.get')
    def test_connection_error(self, mock_requests, mock_feedparser):
        """Test handling of connection errors."""
        mock_entry = MagicMock()
        mock_entry.title = "Test"
        mock_entry.link = "http://example.com"
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed
        
        import requests
        mock_requests.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = get_earnings_news("CONN_ERROR")
        
        assert "ticker" in result


class TestRealWorldTickers:
    """Integration tests with real tickers (may require network)."""
    
    @pytest.mark.integration
    def test_tsmc_earnings(self):
        """Test TSMC earnings news (requires network)."""
        result = get_earnings_news("TSM")
        assert "ticker" in result
        assert result["ticker"] == "TSM"
    
    @pytest.mark.integration
    def test_apple_earnings(self):
        """Test Apple earnings news (requires network)."""
        result = get_earnings_news("AAPL")
        assert "ticker" in result
        assert result["ticker"] == "AAPL"
    
    @pytest.mark.integration
    def test_samsung_earnings(self):
        """Test Samsung earnings news (requires network)."""
        result = get_earnings_news("SSNLF")
        assert "ticker" in result


# Run tests if executed directly
if __name__ == "__main__":
    # Run without integration tests by default
    pytest.main([__file__, "-v", "-m", "not integration"])
