"""
Pytest configuration and shared fixtures for Financial Agent tests
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test environment variables
TEST_DATABASE_URL = "sqlite:///./test_financial_agent.db"
TEST_ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "test-key")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_stock_symbols():
    """Sample stock symbols for testing"""
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }

@pytest.fixture
def sample_watchlist_data():
    """Sample watchlist data for testing"""
    return [
        {"symbol": "AAPL", "user_id": 1},
        {"symbol": "MSFT", "user_id": 1},
        {"symbol": "GOOGL", "user_id": 1}
    ]

@pytest.fixture
def mock_yahoo_finance_data():
    """Mock Yahoo Finance API response data"""
    return {
        "ticker": "AAPL",
        "basic_info": {
            "longName": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics"
        },
        "price_data": {
            "currentPrice": 150.00,
            "previousClose": 149.50,
            "dayHigh": 151.00,
            "dayLow": 148.00
        },
        "financial_metrics": {
            "marketCap": 2500000000000,
            "trailingPE": 25.5,
            "beta": 1.2
        }
    }

@pytest.fixture
def mock_claude_response():
    """Mock Claude AI API response"""
    return {
        "response": "Based on the financial data provided, Apple Inc. (AAPL) shows strong fundamentals...",
        "financial_data_used": {
            "get_stock_info": {"ticker": "AAPL"}
        },
        "session_id": "test_session",
        "timestamp": "2025-07-23T00:00:00"
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Set test environment variables
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["TESTING"] = "true"
    
    yield
    
    # Cleanup after test
    if "TESTING" in os.environ:
        del os.environ["TESTING"]

@pytest.fixture
def client():
    """FastAPI test client fixture"""
    from fastapi.testclient import TestClient
    try:
        from main import app
        return TestClient(app)
    except ImportError:
        pytest.skip("FastAPI app not available for testing")

@pytest.fixture
async def async_client():
    """Async FastAPI test client fixture"""
    from httpx import AsyncClient
    try:
        from main import app
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    except ImportError:
        pytest.skip("FastAPI app not available for async testing")