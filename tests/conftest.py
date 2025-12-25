# tests/conftest.py
"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
import os

# Add project root to path for all tests
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires network)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


@pytest.fixture
def sample_ticker():
    """Provide a sample stock ticker for testing."""
    return "AAPL"


@pytest.fixture
def sample_tickers():
    """Provide a list of sample tickers for testing."""
    return ["AAPL", "MSFT", "GOOGL", "TSM"]


@pytest.fixture
def sample_question():
    """Provide a sample question for testing."""
    return "Did TSMC beat earnings expectations?"


@pytest.fixture
def sample_earnings_text():
    """Provide sample earnings data for testing."""
    return """
    TSMC reported its Q1 2025 earnings with an EPS of $2.01, 
    beating the analyst expectation of $1.93. Revenue grew 22% YoY.
    """
