# AI Stock Research Tool

An AI-powered stock research platform that combines Claude AI with Yahoo Finance data through MCP (Model Context Protocol) integration. Transform your stock analysis with intelligent, conversational insights restricted to your personal watchlist.

## 🎯 Project Overview

This application has evolved from a traditional portfolio management tool into a focused AI-first stock research platform. The core philosophy: **intelligent analysis of stocks you care about most** - your watchlist.

### Key Features
- 🤖 **Claude AI Integration**: Advanced conversational analysis of stocks
- 📊 **Yahoo Finance MCP**: Real-time market data via custom MCP-style service
- 📋 **Watchlist-Centric**: AI restricted to your tracked stocks for focused analysis
- 💬 **Chat Interface**: Natural language queries about your stocks
- 🚀 **Modern Stack**: Next.js 15.4.2 + FastAPI + SQLAlchemy

## 🏗️ Architecture

### Frontend (Next.js 15.4.2)
- **Single Page Focus**: Direct redirect to watchlist page
- **AI Chat Drawer**: Integrated chat interface for stock analysis
- **Mantine UI**: Professional financial component library
- **TypeScript**: Type-safe development

### Backend (FastAPI + Python)
- **Minimal Routes**: Auth, Watchlist, AI Chat only
- **Claude AI Service**: Intelligent query parsing and analysis
- **Yahoo Finance MCP**: Custom MCP-style data integration
- **SQLAlchemy ORM**: Simple User + Watchlist models

## 📊 Yahoo Finance MCP Integration

Our custom `FinancialMCPService` provides comprehensive real-time financial data:

### Available MCP Tools

#### 1. **Comprehensive Stock Information** (`get_comprehensive_stock_info`)
```python
# Returns complete stock profile
{
  "basic_info": {"name", "sector", "industry", "summary"},
  "price_data": {"current_price", "day_range", "52_week_range", "volume"},
  "financial_metrics": {"market_cap", "pe_ratio", "peg_ratio", "beta"},
  "financial_health": {"revenue", "margins", "roe", "debt_ratio"},
  "dividends": {"yield", "rate", "eps", "shares_outstanding"}
}
```

#### 2. **Historical Stock Prices** (`get_historical_stock_prices`)
```python
# Flexible time periods and intervals
periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "1d", "5d", "1wk", "1mo"]
```

#### 3. **Financial Statements** (`get_financial_statements`)
- Income statements (quarterly/annual)
- Balance sheets (quarterly/annual)  
- Cash flow statements
- JSON-serialized with date indexing

#### 4. **Real-Time News Feed** (`get_stock_news`)
- Yahoo Finance news articles
- Company-specific filtering
- Real-time updates with current date context
- Relevance scoring

#### 5. **Upcoming Events & Earnings** (`get_upcoming_earnings_and_events`)
- Earnings calendar with estimates
- Corporate events and announcements
- Q3 2025 context awareness
- Growth metrics

#### 6. **Analyst Recommendations** (`get_analyst_recommendations`)
- Current buy/hold/sell ratings
- Recent upgrades/downgrades
- Historical recommendation trends
- Consensus analysis

#### 7. **Stock Comparison** (`compare_stocks`)
- Multi-stock analysis (up to 5 stocks)
- Customizable metrics comparison
- Relative performance benchmarking

### AI Query Intelligence

The Claude AI agent automatically determines which MCP tools to use:

```python
# Example Query Patterns:
"Tesla earnings Q3 2025" → get_stock_info + get_news + get_upcoming_events
"AAPL vs MSFT performance" → compare_stocks + get_comprehensive_stock_info  
"Apple financial health" → get_financial_statements + get_stock_info
"Recent NVDA news" → get_news + get_stock_info
"Tesla technical analysis" → get_historical_prices + get_stock_info
```

### Current Market Context (Q3 2025)
- **Date Awareness**: July 23, 2025 context for earnings and events
- **Live Data**: Real-time price movements and market updates
- **News Integration**: Current market developments and analyst actions
- **Event Tracking**: Upcoming Q3 2025 earnings and corporate events

## 🚀 Quick Start

### Prerequisites
```bash
# Backend Requirements
Python 3.8+
pip install -r requirements.txt

# Frontend Requirements  
Node.js 18+
npm install
```

### Environment Setup
Create `.env` file in project root:
```bash
# Required API Keys
ANTHROPIC_API_KEY=your_claude_api_key_here
DATABASE_URL=sqlite:///./financial_agent.db

# Optional Configuration
HOST=localhost
PORT=8000
DEBUG=true
```

### Running the Application

#### Backend Server
```bash
# Start FastAPI server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

#### Frontend Application
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### First Time Setup
1. Navigate to `http://localhost:3000`
2. Register new account or login
3. Add stocks to your watchlist (or use demo mode)
4. Click the robot icon next to any stock to start AI chat

## 💬 Using the AI Chat

### How It Works
1. **Watchlist Integration**: AI can only analyze stocks in your watchlist
2. **Natural Language**: Ask questions in plain English
3. **Smart Context**: AI automatically selects relevant data
4. **Real-Time Data**: Always uses current Yahoo Finance information

### Example Queries
```
"What are the key events coming for Tesla?"
"How is Apple performing compared to Microsoft?"  
"Give me a technical analysis of NVIDIA"
"What's the latest news on Amazon earnings?"
"Should I be concerned about Tesla's debt levels?"
"Compare the growth prospects of these tech stocks"
```

### Demo Mode
If your watchlist is empty, the system provides demo stocks:
- AAPL (Apple Inc.)
- MSFT (Microsoft Corporation)
- GOOGL (Alphabet Inc.)
- AMZN (Amazon.com Inc.)
- TSLA (Tesla Inc.)

## 🛠️ API Reference

### Core Endpoints

#### Watchlist Management
```bash
GET /watchlist/              # Get user's watchlist
POST /watchlist/             # Add stock to watchlist
DELETE /watchlist/{symbol}   # Remove stock from watchlist
```

#### AI Chat
```bash
POST /ai/watchlist/chat      # Chat with AI about watchlist stocks
GET /ai/watchlist/chat-sessions  # Get chat history
```

#### Financial Data (MCP)
```bash
GET /ai/financial-data/{ticker}?data_type=comprehensive
GET /ai/financial-data/{ticker}?data_type=news  
GET /ai/financial-data/{ticker}?data_type=historical&period=1y
POST /ai/compare             # Compare multiple stocks
```

## 🏛️ Project Structure

```
AI Stock Research Tool/
├── 📁 src/                          # Backend Python code
│   ├── 📁 api/
│   │   ├── 📁 routes/              # FastAPI routes
│   │   │   ├── auth_routes.py      # Authentication
│   │   │   ├── watchlist_routes.py # Watchlist management  
│   │   │   └── ai_agent_routes.py  # AI chat endpoints
│   │   ├── schemas.py              # Pydantic models
│   │   └── auth.py                 # Auth utilities
│   ├── 📁 models/
│   │   └── database.py             # SQLAlchemy models (User, Watchlist)
│   ├── 📁 services/
│   │   ├── financial_mcp_service.py # Yahoo Finance MCP integration
│   │   └── claude_ai_agent.py      # Claude AI service
│   └── 📁 utils/
│       └── config.py               # Configuration management
├── 📁 frontend/                     # Next.js frontend
│   └── 📁 src/
│       ├── 📁 app/
│       │   ├── layout.tsx          # Root layout
│       │   ├── page.tsx            # Redirect to watchlist
│       │   └── 📁 watchlist/
│       │       └── page.tsx        # Main watchlist + AI chat page
│       ├── 📁 lib/
│       │   ├── api.ts              # API client
│       │   └── theme.ts            # Mantine theme
│       └── 📁 providers/
│           └── AppProvider.tsx     # React context
├── 📁 tests/                       # Organized test files
│   ├── test_backend.py             # Backend API tests
│   ├── test_claude_api.py          # AI integration tests
│   ├── test_data_collection.py     # Data service tests
│   └── conftest.py                 # Shared fixtures
├── main.py                         # FastAPI app entry point
├── pytest.ini                     # Test configuration
└── README.md                       # This documentation
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# With coverage report
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test files
python -m pytest tests/test_backend.py           # Backend tests
python -m pytest tests/test_claude_api.py        # AI integration 
python -m pytest tests/test_data_collection.py   # Data services
```

### Test Categories
- **🔧 Unit Tests**: Component isolation testing
- **🔗 Integration Tests**: Multi-component workflows  
- **🎯 System Tests**: End-to-end functionality
- **🌐 API Tests**: External service integration (Claude AI, Yahoo Finance)

## 📈 Development Milestones

### ✅ Phase 1: Foundation (Completed)
- [x] Basic FastAPI backend with user authentication
- [x] Next.js frontend with Mantine UI components
- [x] SQLAlchemy database models
- [x] Basic watchlist functionality

### ✅ Phase 2: AI Integration (Completed)
- [x] Claude AI API integration
- [x] Yahoo Finance data collection
- [x] Custom MCP-style service architecture
- [x] Intelligent query parsing and data selection

### ✅ Phase 3: User Experience (Completed)
- [x] Watchlist-integrated chat interface
- [x] Real-time AI conversations
- [x] Session-based chat history
- [x] Mobile-responsive design

### ✅ Phase 4: Data Quality (Completed)
- [x] Enhanced Yahoo Finance data accuracy
- [x] Current date awareness (Q3 2025 context)
- [x] Real-time news integration
- [x] Comprehensive stock analysis

### ✅ Phase 5: Code Organization (Completed)
- [x] Test file organization in `tests/` directory
- [x] Comprehensive refactoring from portfolio tool to AI research tool
- [x] Removal of legacy features (portfolio management, complex analytics)
- [x] Streamlined codebase focused on watchlist + AI chat

### ✅ Phase 6: Production Readiness (Completed)
- [x] Comprehensive documentation
- [x] Code cleanup and optimization
- [x] Security review for sensitive data
- [x] GitHub publication preparation

## 🔐 Security Notes

### Environment Variables
- Never commit `.env` files
- Use environment-specific configurations
- Rotate API keys regularly

### Data Privacy
- User data stored locally in SQLite
- No sensitive financial data persisted
- API keys encrypted in environment variables

### API Security
- JWT-based authentication
- Rate limiting on AI endpoints
- Input validation and sanitization

## 🤝 Contributing

This project follows a focused development approach:

1. **Core Features Only**: Watchlist management + AI chat
2. **MCP Integration**: Yahoo Finance data through custom MCP service
3. **AI-First Design**: Claude AI as the primary interface
4. **Clean Architecture**: Minimal, maintainable codebase

### Development Workflow
```bash
# 1. Clone and setup
git clone <repository-url>
cd ai-stock-research-tool

# 2. Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend setup  
cd frontend
npm install

# 4. Environment configuration
cp .env.example .env
# Edit .env with your API keys

# 5. Run tests
python -m pytest tests/

# 6. Start development servers
python main.py          # Backend on :8000
npm run dev             # Frontend on :3000
```

## 📞 Support

- **Documentation Issues**: Update README.md
- **Bug Reports**: Include steps to reproduce
- **Feature Requests**: Focus on watchlist + AI chat improvements
- **API Questions**: Reference MCP tool documentation above

## 📄 License

This project is developed as an AI-first financial research tool. See license file for usage terms.

---

**AI Stock Research Tool** - Intelligent stock analysis for your watchlist, powered by Claude AI and Yahoo Finance MCP integration.

*Current Version: 2.0.0 (AI-First Architecture)*  
*Last Updated: July 22, 2025*