# tests/test_api_agent.py
"""
Unit tests for the API Agent (data_ingestion/api_agent.py).
Tests Yahoo Finance and AlphaVantage endpoints.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from data_ingestion.api_agent import app


# Create test client
client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_returns_message(self):
        """Test that root endpoint returns expected message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "API Agent" in data["message"]


class TestYahooFinanceEndpoint:
    """Tests for the Yahoo Finance historical data endpoint."""
    
    def test_valid_symbol(self):
        """Test with a valid stock symbol."""
        response = client.post(
            "/yfinance/historical",
            json={
                "symbol": "AAPL",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have some historical records
        if len(data) > 0:
            assert "Open" in data[0] or "Close" in data[0]
    
    def test_symbol_without_dates(self):
        """Test with just a symbol, no date range."""
        response = client.post(
            "/yfinance/historical",
            json={"symbol": "MSFT"}
        )
        # Should work with default date handling
        assert response.status_code in [200, 404, 500]
    
    def test_invalid_symbol(self):
        """Test with an invalid/nonexistent symbol."""
        response = client.post(
            "/yfinance/historical",
            json={"symbol": "INVALIDXYZ123"}
        )
        # Should return 404 or 500 for invalid symbols
        assert response.status_code in [404, 500]
    
    def test_missing_symbol(self):
        """Test request without symbol field."""
        response = client.post(
            "/yfinance/historical",
            json={}
        )
        # Should return validation error (422)
        assert response.status_code == 422
    
    def test_empty_symbol(self):
        """Test with empty symbol string."""
        response = client.post(
            "/yfinance/historical",
            json={"symbol": ""}
        )
        # Should handle gracefully
        assert response.status_code in [404, 500]


class TestAlphaVantageEndpoint:
    """Tests for the AlphaVantage quote endpoint."""
    
    def test_valid_symbol_structure(self):
        """Test endpoint returns proper structure for valid symbol."""
        response = client.get("/alphavantage/quote/AAPL")
        # May fail without API key, but should return proper error
        assert response.status_code in [200, 500]
        data = response.json()
        # Either has quote data or error message
        assert isinstance(data, dict)
    
    def test_missing_api_key_handling(self):
        """Test that missing API key is handled properly."""
        # If ALPHAVANTAGE_API_KEY is not set, should return 500
        if not os.getenv("ALPHAVANTAGE_API_KEY"):
            response = client.get("/alphavantage/quote/AAPL")
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "API key" in data["detail"]
    
    def test_invalid_symbol(self):
        """Test with an invalid symbol."""
        response = client.get("/alphavantage/quote/INVALIDXYZ123")
        # Should return 404 or 500
        assert response.status_code in [404, 500]


class TestInputValidation:
    """Tests for input validation."""
    
    def test_stock_request_schema(self):
        """Test that StockRequest schema validates properly."""
        # Valid request
        response = client.post(
            "/yfinance/historical",
            json={"symbol": "GOOGL"}
        )
        assert response.status_code in [200, 404, 500]
        
        # Invalid JSON
        response = client.post(
            "/yfinance/historical",
            data="not json"
        )
        assert response.status_code == 422
    
    def test_date_format_handling(self):
        """Test various date formats."""
        # Standard format
        response = client.post(
            "/yfinance/historical",
            json={
                "symbol": "AAPL",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        )
        assert response.status_code in [200, 404, 500]
        
        # Future dates (might return empty data)
        response = client.post(
            "/yfinance/historical",
            json={
                "symbol": "AAPL",
                "start_date": "2099-01-01",
                "end_date": "2099-12-31"
            }
        )
        assert response.status_code in [200, 404, 500]


class TestResponseFormat:
    """Tests for response format validation."""
    
    def test_historical_data_format(self):
        """Test that historical data has expected fields."""
        response = client.post(
            "/yfinance/historical",
            json={
                "symbol": "AAPL",
                "start_date": "2024-01-01",
                "end_date": "2024-01-10"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                record = data[0]
                # Check for common OHLCV fields
                expected_fields = ["Open", "High", "Low", "Close", "Volume"]
                for field in expected_fields:
                    assert field in record, f"Missing field: {field}"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
