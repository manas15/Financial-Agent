"""
Test Claude API specifically
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Claude API Integration...")

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key or api_key == "your_claude_api_key_here":
    print("❌ No Claude API key found.")
    print("Please edit the .env file and replace 'your_claude_api_key_here' with your actual API key from https://console.anthropic.com/")
    print("Your API key should start with 'sk-ant-'")
else:
    print(f"✅ Claude API key found (length: {len(api_key)})")
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized")
        
        # Test simple API call
        print("🔄 Testing API call...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Respond with exactly: 'Claude API is working for Financial Agent'"}
            ]
        )
        
        result = response.content[0].text
        print(f"✅ Claude API Response: {result}")
        
        if "Claude API is working" in result:
            print("🎉 Claude API is fully functional!")
        else:
            print("⚠️  Claude API responded but with unexpected content")
            
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        if "Invalid API key" in str(e):
            print("The API key appears to be invalid. Please check:")
            print("1. Key is copied correctly from console.anthropic.com")
            print("2. Key starts with 'sk-ant-'") 
            print("3. You have billing set up in your Anthropic account")

print("\nIf Claude API is working, you can now test the full portfolio analysis!")
print("Run: python3 main.py")
print("Then visit: http://localhost:8000/docs")