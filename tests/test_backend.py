"""
Simple test to verify backend components work without database
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("Testing Financial Agent Backend Components...")

# Test 1: Configuration loading
print("\n1. Testing configuration...")
try:
    from src.utils.config import config
    print(f"✅ Config loaded - Debug: {config.DEBUG}")
    print(f"   Host: {config.HOST}:{config.PORT}")
    
    missing_keys = config.validate_required_keys()
    if missing_keys:
        print(f"⚠️  Missing API keys: {missing_keys}")
    else:
        print("✅ All API keys configured")
        
except Exception as e:
    print(f"❌ Config error: {e}")

# Test 2: Data collection
print("\n2. Testing data collection...")
try:
    from src.data.collectors import YahooFinanceCollector
    collector = YahooFinanceCollector()
    
    # Test basic stock info
    stock_info = collector.get_stock_info("AAPL")
    if stock_info and stock_info.get('current_price'):
        print(f"✅ Yahoo Finance: AAPL @ ${stock_info['current_price']}")
    else:
        print("⚠️  Yahoo Finance: No price data")
        
    # Test batch prices
    batch_data = collector.get_batch_prices(["AAPL", "GOOGL"])
    if not batch_data.empty:
        print(f"✅ Batch prices: {len(batch_data)} stocks")
    else:
        print("⚠️  Batch prices: No data")
        
except Exception as e:
    print(f"❌ Data collection error: {e}")

# Test 3: Authentication system
print("\n3. Testing authentication...")
try:
    from src.api.auth import AuthManager
    
    # Test password hashing
    password = "testpassword123"
    hashed = AuthManager.get_password_hash(password)
    verified = AuthManager.verify_password(password, hashed)
    
    if verified:
        print("✅ Password hashing works")
    else:
        print("❌ Password hashing failed")
        
    # Test JWT token creation
    token = AuthManager.create_access_token({"sub": "123"})
    payload = AuthManager.verify_token(token)
    
    if payload.get("sub") == "123":
        print("✅ JWT tokens work")
    else:
        print("❌ JWT token failed")
        
except Exception as e:
    print(f"❌ Authentication error: {e}")

# Test 4: Claude analyzer (if API key available)
print("\n4. Testing Claude analyzer...")
try:
    from src.analysis.claude_analyzer import ClaudePortfolioAnalyzer
    
    if config.ANTHROPIC_API_KEY and config.ANTHROPIC_API_KEY != "your_claude_api_key_here":
        analyzer = ClaudePortfolioAnalyzer()
        print("✅ Claude analyzer initialized")
    else:
        print("⚠️  Claude API key not configured - add to .env file")
        
except Exception as e:
    print(f"❌ Claude analyzer error: {e}")

# Test 5: API schemas
print("\n5. Testing API schemas...")
try:
    from src.api.schemas import UserCreate, PortfolioCreate
    
    # Test user schema
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    print(f"✅ User schema: {user_data.email}")
    
    # Test portfolio schema
    portfolio_data = PortfolioCreate(
        symbol="AAPL",
        shares=10.0,
        cost_basis=150.0
    )
    print(f"✅ Portfolio schema: {portfolio_data.symbol}")
    
except Exception as e:
    print(f"❌ Schema error: {e}")

print("\n" + "="*50)
print("Backend component test completed!")
print("Next step: Add your Claude API key to .env and test the full system")
print("="*50)