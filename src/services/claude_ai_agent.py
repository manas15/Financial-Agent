"""
Claude AI Agent Service
Provides intelligent financial analysis and conversational capabilities
"""

from anthropic import Anthropic
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

from src.services.financial_mcp_service import financial_mcp_service
from src.utils.config import config

logger = logging.getLogger(__name__)

class ClaudeFinancialAgent:
    """
    Claude AI agent specialized for financial analysis and stock research
    """
    
    def __init__(self):
        self.client = None
        self.conversation_history = {}  # Store conversation context per session
        
        # Initialize Claude client if API key is available
        try:
            if hasattr(config, 'ANTHROPIC_API_KEY') and config.ANTHROPIC_API_KEY:
                self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
            else:
                logger.warning("ANTHROPIC_API_KEY not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {e}")
    
    def _get_system_prompt(self) -> str:
        """
        System prompt for the financial AI agent
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_quarter = f"Q{((datetime.now().month - 1) // 3) + 1} {datetime.now().year}"
        
        return f"""You are an expert financial analyst and investment advisor AI agent with access to comprehensive real-time financial data from Yahoo Finance. Today's date is {current_date} and we are currently in {current_quarter}.

CRITICAL: You have access to REAL, CURRENT financial data. Do not claim data limitations or "demo mode" - analyze the provided data confidently and thoroughly.

Your capabilities include:
- Real-time stock data analysis with current prices and metrics
- Current news analysis from Yahoo Finance with market developments
- Upcoming earnings calendar and scheduled events
- Financial statement analysis (income statements, balance sheets, cash flows)
- Company comparisons and sector analysis  
- Technical analysis and trend identification
- Risk assessment and portfolio recommendations
- Analyst recommendations and recent upgrades/downgrades

Guidelines for responses:
- ALWAYS use the current financial data provided to you - it is real and accurate
- Emphasize current date context ({current_date}) and current quarter ({current_quarter})
- When asked about "upcoming" or "coming" events, use the news and events data provided
- Extract specific information from news articles, especially earnings dates and announcements
- Never claim "limited data access" or "demo mode" - you have comprehensive Yahoo Finance data
- Base all analysis on the actual financial data provided in the context
- Provide specific metrics, ratios, and data points from the provided information
- Use professional terminology while remaining accessible
- When making recommendations, clearly state they are not financial advice

When financial data is provided to you, analyze:
- Current price movements and trading metrics
- Recent news headlines and summaries for market developments
- Upcoming earnings dates mentioned in news articles
- Financial ratios and performance metrics
- Analyst recommendations and recent changes
- Company fundamentals and growth indicators

Always provide confident, data-driven analysis based on the real financial information available to you."""

    async def _fetch_financial_data(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch financial data using our MCP-style service
        """
        try:
            if tool_name == "get_stock_info":
                return await financial_mcp_service.get_comprehensive_stock_info(kwargs.get("ticker"))
            elif tool_name == "get_historical_prices":
                return await financial_mcp_service.get_historical_stock_prices(
                    kwargs.get("ticker"),
                    kwargs.get("period", "1mo"),
                    kwargs.get("interval", "1d")
                )
            elif tool_name == "get_financial_statements":
                return await financial_mcp_service.get_financial_statements(
                    kwargs.get("ticker"),
                    kwargs.get("statement_type", "income_stmt"),
                    kwargs.get("quarterly", False)
                )
            elif tool_name == "get_news":
                return await financial_mcp_service.get_stock_news(
                    kwargs.get("ticker"),
                    kwargs.get("limit", 10)
                )
            elif tool_name == "get_upcoming_events":
                return await financial_mcp_service.get_upcoming_earnings_and_events(kwargs.get("ticker"))
            elif tool_name == "get_recommendations":
                return await financial_mcp_service.get_analyst_recommendations(kwargs.get("ticker"))
            elif tool_name == "compare_stocks":
                return await financial_mcp_service.compare_stocks(
                    kwargs.get("tickers", []),
                    kwargs.get("metrics")
                )
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error fetching financial data with {tool_name}: {e}")
            return {"error": str(e)}

    def _parse_query_for_data_needs(self, query: str) -> List[Dict[str, Any]]:
        """
        Analyze user query to determine what financial data to fetch
        """
        query_lower = query.lower()
        data_requests = []
        
        # Extract ticker symbols (improved regex pattern)
        import re
        # Look for patterns like AAPL, $AAPL, or ticker symbols in context
        ticker_patterns = [
            r'\$([A-Z]{1,5})\b',  # $AAPL format
            r'\b([A-Z]{2,5})\s+(?:stock|shares?|ticker|company)\b',  # AAPL stock
            r'(?:stock|ticker|symbol)\s+([A-Z]{2,5})\b',  # stock AAPL
            r'\b([A-Z]{2,5})\s+(?:vs?\.?|versus|compared?)\s+([A-Z]{2,5})\b',  # AAPL vs MSFT
            r'\b([A-Z]{2,5})(?:\s*,\s*([A-Z]{2,5}))*\b'  # AAPL, MSFT, GOOGL
        ]
        
        tickers = []
        for pattern in ticker_patterns:
            matches = re.findall(pattern, query.upper())
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        tickers.extend([m for m in match if m and len(m) >= 2])
                    else:
                        if match and len(match) >= 2:
                            tickers.append(match)
        
        # Remove duplicates and common false positives
        false_positives = {'WHAT', 'WHEN', 'WHERE', 'WHICH', 'WILL', 'WITH', 'FROM', 'THAT', 'THIS', 'THEY', 'HAVE', 'BEEN', 'WERE', 'WOULD', 'COULD', 'SHOULD', 'ABOUT', 'STOCK', 'PRICE', 'MARKET', 'TRADE', 'INVEST', 'ANALYSIS', 'COMPANY'}
        tickers = list(set([t for t in tickers if t not in false_positives and len(t) >= 2]))
        
        if not tickers:
            # Common company name to ticker mapping
            name_to_ticker = {
                "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL", 
                "tesla": "TSLA", "amazon": "AMZN", "facebook": "META",
                "nvidia": "NVDA", "netflix": "NFLX", "spotify": "SPOT"
            }
            
            for name, ticker in name_to_ticker.items():
                if name in query_lower:
                    tickers.append(ticker)
        
        if tickers:
            primary_ticker = tickers[0]
            
            # Determine what data to fetch based on query keywords
            if any(word in query_lower for word in ["compare", "vs", "versus", "against"]):
                data_requests.append({"tool": "compare_stocks", "tickers": tickers[:3]})  # Limit to 3 for comparison
            
            if any(word in query_lower for word in ["historical", "price history", "chart", "performance"]):
                period = "1y"  # Default to 1 year
                if "6 month" in query_lower or "6m" in query_lower:
                    period = "6mo"
                elif "3 month" in query_lower or "3m" in query_lower:
                    period = "3mo"
                elif "2 year" in query_lower or "2y" in query_lower:
                    period = "2y"
                
                data_requests.append({"tool": "get_historical_prices", "ticker": primary_ticker, "period": period})
            
            if any(word in query_lower for word in ["financial", "statement", "income", "balance sheet", "cash flow"]):
                statement_type = "income_stmt"
                if "balance sheet" in query_lower:
                    statement_type = "balance_sheet"
                elif "cash flow" in query_lower:
                    statement_type = "cashflow"
                
                quarterly = "quarterly" in query_lower or "q1" in query_lower or "q2" in query_lower
                data_requests.append({
                    "tool": "get_financial_statements", 
                    "ticker": primary_ticker, 
                    "statement_type": statement_type,
                    "quarterly": quarterly
                })
            
            if any(word in query_lower for word in ["news", "latest", "recent", "announcement"]):
                data_requests.append({"tool": "get_news", "ticker": primary_ticker})
            
            if any(word in query_lower for word in ["upcoming", "events", "earnings", "coming", "future", "calendar", "scheduled"]):
                data_requests.append({"tool": "get_upcoming_events", "ticker": primary_ticker})
            
            if any(word in query_lower for word in ["analyst", "recommendation", "upgrade", "downgrade", "rating"]):
                data_requests.append({"tool": "get_recommendations", "ticker": primary_ticker})
            
            # Always get basic stock info for context
            if not data_requests or any(word in query_lower for word in ["analysis", "overview", "info", "about"]):
                data_requests.append({"tool": "get_stock_info", "ticker": primary_ticker})
        
        return data_requests

    async def analyze_query(
        self, 
        query: str, 
        session_id: str = "default",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze user query and provide intelligent financial insights
        """
        if not self.client:
            return {
                "error": "Claude AI client not configured. Please set ANTHROPIC_API_KEY.",
                "response": "I'm unable to provide AI analysis without proper configuration."
            }
        
        try:
            # Initialize session history if needed
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            # Determine what financial data to fetch
            data_requests = self._parse_query_for_data_needs(query)
            
            # If user_context has a focused_ticker, prioritize that over parsed tickers
            if user_context and user_context.get("focused_ticker"):
                focused_ticker = user_context["focused_ticker"].upper()
                # Override any ticker found in data_requests with the focused ticker
                for request in data_requests:
                    if "ticker" in request:
                        request["ticker"] = focused_ticker
                    elif "tickers" in request:
                        request["tickers"] = [focused_ticker]
            
            # Fetch required financial data
            financial_data = {}
            for request in data_requests:
                tool_name = request.pop("tool")
                data = await self._fetch_financial_data(tool_name, **request)
                financial_data[tool_name] = data
            
            # Prepare context for Claude
            context = f"""
User Query: {query}

Financial Data Available:
{json.dumps(financial_data, indent=2, default=str)}

User Context: {user_context or 'No additional context provided'}

Previous Conversation: {self.conversation_history[session_id][-3:] if self.conversation_history[session_id] else 'No previous conversation'}
"""
            
            # Generate response using Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.1,
                system=self._get_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": context
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            # Update conversation history
            self.conversation_history[session_id].append({
                "timestamp": datetime.now().isoformat(),
                "user_query": query,
                "ai_response": response_text[:500] + "..." if len(response_text) > 500 else response_text  # Truncate for history
            })
            
            # Keep only last 10 exchanges
            if len(self.conversation_history[session_id]) > 10:
                self.conversation_history[session_id] = self.conversation_history[session_id][-10:]
            
            return {
                "response": response_text,
                "financial_data_used": financial_data,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in Claude analysis: {e}")
            return {
                "error": str(e),
                "response": "I encountered an error while analyzing your query. Please try again or rephrase your question."
            }
    
    async def get_stock_summary(self, ticker: str) -> Dict[str, Any]:
        """
        Get a comprehensive AI-generated summary for a stock
        """
        query = f"Provide a comprehensive analysis of {ticker} stock including current performance, financial health, growth prospects, risks, and investment recommendation."
        return await self.analyze_query(query, session_id=f"summary_{ticker}")
    
    async def compare_stocks_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        """
        AI-powered comparison of multiple stocks
        """
        tickers_str = ", ".join(tickers)
        query = f"Compare and analyze {tickers_str} stocks. Provide detailed comparison of their financial metrics, growth prospects, risks, and which might be better investments and why."
        return await self.analyze_query(query, session_id=f"comparison_{'-'.join(tickers)}")
    
    async def portfolio_analysis(self, portfolio_tickers: List[str], user_goals: str = "") -> Dict[str, Any]:
        """
        Analyze an entire portfolio and provide recommendations
        """
        tickers_str = ", ".join(portfolio_tickers)
        query = f"Analyze my portfolio containing {tickers_str}. Provide diversification analysis, risk assessment, performance evaluation, and recommendations for improvement. User goals: {user_goals}"
        return await self.analyze_query(query, session_id="portfolio_analysis")

# Global instance
claude_agent = ClaudeFinancialAgent()