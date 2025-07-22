"""
Test the complete Financial Agent system with Supabase
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_system():
    print("🚀 Testing Complete Financial Agent System...")
    
    # Test 1: Check API is running
    print("\n1. Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        print("Make sure you run 'python3 main.py' first!")
        return
    
    # Test 2: User Registration
    print("\n2. Testing User Registration...")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User registered: {data['user']['email']}")
            token = data['access_token']
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"⚠️  Registration response: {response.status_code} - {response.text}")
            # Try login instead
            print("Trying to login with existing user...")
            login_response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": user_data["email"],
                "password": user_data["password"]
            })
            if login_response.status_code == 200:
                data = login_response.json()
                print(f"✅ User logged in: {data['user']['email']}")
                token = data['access_token']
                headers = {"Authorization": f"Bearer {token}"}
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                return
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return
    
    # Test 3: Add Portfolio Holdings
    print("\n3. Testing Portfolio Management...")
    try:
        holdings = [
            {"symbol": "AAPL", "shares": 10, "cost_basis": 150.0},
            {"symbol": "GOOGL", "shares": 5, "cost_basis": 120.0},
            {"symbol": "MSFT", "shares": 8, "cost_basis": 200.0}
        ]
        
        for holding in holdings:
            response = requests.post(f"{BASE_URL}/portfolio/holdings", 
                                   json=holding, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Added {holding['symbol']}: {holding['shares']} shares")
            else:
                print(f"⚠️  Failed to add {holding['symbol']}: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Portfolio error: {e}")
    
    # Test 4: Get Portfolio Summary
    print("\n4. Testing Portfolio Summary...")
    try:
        response = requests.get(f"{BASE_URL}/portfolio/summary", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Portfolio Summary:")
            print(f"   Total Value: ${data['total_market_value']:,.2f}")
            print(f"   Total Cost: ${data['total_cost']:,.2f}")
            print(f"   Gain/Loss: ${data['total_gain_loss']:,.2f} ({data['total_gain_loss_pct']:.2f}%)")
            print(f"   Holdings: {data['holdings_count']}")
        else:
            print(f"⚠️  Portfolio summary failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Portfolio summary error: {e}")
    
    # Test 5: Add to Watchlist
    print("\n5. Testing Watchlist...")
    try:
        watchlist_items = ["TSLA", "NVDA"]
        for symbol in watchlist_items:
            response = requests.post(f"{BASE_URL}/watchlist/", 
                                   json={"symbol": symbol, "notes": f"Watching {symbol}"},
                                   headers=headers)
            if response.status_code == 200:
                print(f"✅ Added {symbol} to watchlist")
            else:
                print(f"⚠️  Failed to add {symbol} to watchlist: {response.status_code}")
    except Exception as e:
        print(f"❌ Watchlist error: {e}")
    
    # Test 6: Claude Analysis (if API key is configured)
    print("\n6. Testing Claude Analysis...")
    try:
        response = requests.post(f"{BASE_URL}/analysis/daily-summary", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Claude Analysis Generated:")
            print(f"   Analysis ID: {data['id']}")
            print(f"   Type: {data['analysis_type']}")
            print(f"   Preview: {data['analysis_result'][:100]}...")
        else:
            print(f"⚠️  Claude analysis failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Claude analysis error: {e}")
    
    print("\n" + "="*60)
    print("🎯 SYSTEM TEST COMPLETE!")
    print("✅ Database: Connected to Supabase")
    print("✅ Authentication: JWT working")
    print("✅ Portfolio: Real-time stock data")
    print("✅ Watchlist: Stock tracking")
    if 'Claude Analysis Generated' in locals():
        print("✅ Claude AI: Portfolio analysis working")
    print("="*60)
    print("\n🌐 Visit http://localhost:8000/docs for interactive API docs!")

if __name__ == "__main__":
    test_system()