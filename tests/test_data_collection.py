import pytest
import pandas as pd
from src.data.collectors import YahooFinanceCollector, AlphaVantageCollector

class TestYahooFinanceCollector:
    
    def setup_method(self):
        self.collector = YahooFinanceCollector()
    
    def test_get_stock_info_valid_symbol(self):
        """Test getting stock info for a valid symbol"""
        result = self.collector.get_stock_info("AAPL")
        
        assert isinstance(result, dict)
        assert result.get('symbol') == "AAPL"
        assert 'current_price' in result
        assert 'market_cap' in result
    
    def test_get_stock_info_invalid_symbol(self):
        """Test getting stock info for invalid symbol"""
        result = self.collector.get_stock_info("INVALIDSTOCK123")
        
        # Should return empty dict or dict with minimal data
        assert isinstance(result, dict)
    
    def test_get_historical_data_valid_symbol(self):
        """Test getting historical data"""
        result = self.collector.get_historical_data("AAPL", "5d")
        
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert 'Close' in result.columns
            assert 'Volume' in result.columns
            assert 'Symbol' in result.columns
    
    def test_get_batch_prices(self):
        """Test getting batch prices"""
        symbols = ["AAPL", "GOOGL", "MSFT"]
        result = self.collector.get_batch_prices(symbols)
        
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert 'symbol' in result.columns
            assert 'price' in result.columns
    
    def test_get_batch_prices_empty_list(self):
        """Test batch prices with empty symbol list"""
        result = self.collector.get_batch_prices([])
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty

class TestAlphaVantageCollector:
    
    def setup_method(self):
        self.collector = AlphaVantageCollector()
    
    def test_get_company_overview_no_api_key(self):
        """Test company overview without API key"""
        collector = AlphaVantageCollector(api_key=None)
        result = collector.get_company_overview("AAPL")
        
        assert isinstance(result, dict)
        assert result == {}  # Should return empty dict without API key
    
    @pytest.mark.skipif(not AlphaVantageCollector().api_key, 
                       reason="Alpha Vantage API key not available")
    def test_get_company_overview_with_api_key(self):
        """Test company overview with API key (skipped if no key)"""
        result = self.collector.get_company_overview("AAPL")
        
        assert isinstance(result, dict)
        # If API key is valid, should have data
        if result:
            assert 'Symbol' in result or 'symbol' in result

if __name__ == "__main__":
    # Simple test runner
    print("Running data collection tests...")
    
    # Test Yahoo Finance
    yf_collector = YahooFinanceCollector()
    print("\n1. Testing Yahoo Finance stock info...")
    aapl_info = yf_collector.get_stock_info("AAPL")
    print(f"AAPL current price: ${aapl_info.get('current_price', 'N/A')}")
    
    print("\n2. Testing batch prices...")
    batch_prices = yf_collector.get_batch_prices(["AAPL", "GOOGL", "MSFT"])
    print(f"Batch prices shape: {batch_prices.shape}")
    if not batch_prices.empty:
        print(batch_prices[['symbol', 'price']].head())
    
    print("\n3. Testing historical data...")
    hist_data = yf_collector.get_historical_data("AAPL", "5d")
    print(f"Historical data shape: {hist_data.shape}")
    
    print("\nData collection tests completed!")