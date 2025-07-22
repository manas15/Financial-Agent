"""
AI Agent API Routes
Provides endpoints for conversational financial AI assistant
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import logging

from src.models.database import get_db, Watchlist
from src.services.claude_ai_agent import claude_agent
from src.services.financial_mcp_service import financial_mcp_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai-agent"])

# Request/Response Models
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"
    user_context: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    financial_data_used: Optional[dict] = None
    session_id: str
    timestamp: str
    error: Optional[str] = None

class StockAnalysisRequest(BaseModel):
    ticker: str
    analysis_type: Optional[str] = "comprehensive"  # comprehensive, quick, technical, fundamental

class ComparisonRequest(BaseModel):
    tickers: List[str]
    focus: Optional[str] = "general"  # general, growth, value, risk, dividends

class PortfolioAnalysisRequest(BaseModel):
    tickers: List[str]
    user_goals: Optional[str] = ""
    risk_tolerance: Optional[str] = "moderate"  # conservative, moderate, aggressive

class WatchlistChatRequest(BaseModel):
    query: str
    ticker: Optional[str] = None  # Specific stock to focus on
    user_id: Optional[int] = None

class ChatSession(BaseModel):
    session_id: str
    ticker: Optional[str]
    title: str
    last_message: str
    timestamp: str
    message_count: int

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with the AI financial assistant
    """
    try:
        result = await claude_agent.analyze_query(
            query=request.query,
            session_id=request.session_id,
            user_context=request.user_context
        )
        
        if "error" in result:
            return ChatResponse(
                response=result.get("response", "An error occurred"),
                session_id=request.session_id,
                timestamp=result.get("timestamp", ""),
                error=result["error"]
            )
        
        return ChatResponse(
            response=result["response"],
            financial_data_used=result.get("financial_data_used"),
            session_id=result["session_id"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat request"
        )

@router.post("/analyze/{ticker}")
async def analyze_stock(
    ticker: str,
    request: StockAnalysisRequest = None,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered stock analysis
    """
    try:
        # Use ticker from path, fallback to request body
        symbol = ticker.upper()
        
        result = await claude_agent.get_stock_summary(symbol)
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return {
            "ticker": symbol,
            "analysis": result["response"],
            "data_sources": result.get("financial_data_used", {}),
            "timestamp": result["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing stock {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze stock {ticker}"
        )

@router.post("/compare")
async def compare_stocks(
    request: ComparisonRequest,
    db: Session = Depends(get_db)
):
    """
    AI-powered stock comparison
    """
    try:
        if len(request.tickers) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 tickers required for comparison"
            )
        
        if len(request.tickers) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 tickers allowed for comparison"
            )
        
        tickers = [t.upper() for t in request.tickers]
        result = await claude_agent.compare_stocks_analysis(tickers)
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return {
            "tickers": tickers,
            "comparison": result["response"],
            "data_sources": result.get("financial_data_used", {}),
            "timestamp": result["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing stocks: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to compare stocks"
        )

@router.post("/portfolio/analyze")
async def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    AI-powered portfolio analysis and recommendations
    """
    try:
        if not request.tickers:
            raise HTTPException(
                status_code=400,
                detail="At least 1 ticker required for portfolio analysis"
            )
        
        tickers = [t.upper() for t in request.tickers]
        result = await claude_agent.portfolio_analysis(
            portfolio_tickers=tickers,
            user_goals=f"{request.user_goals} Risk tolerance: {request.risk_tolerance}"
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return {
            "portfolio": tickers,
            "analysis": result["response"],
            "data_sources": result.get("financial_data_used", {}),
            "user_goals": request.user_goals,
            "risk_tolerance": request.risk_tolerance,
            "timestamp": result["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze portfolio"
        )

@router.get("/financial-data/{ticker}")
async def get_financial_data(
    ticker: str,
    data_type: str = "comprehensive",  # comprehensive, historical, statements, news, recommendations
    period: Optional[str] = "1y",
    db: Session = Depends(get_db)
):
    """
    Get raw financial data (MCP-style) for a stock
    """
    try:
        symbol = ticker.upper()
        
        if data_type == "comprehensive":
            result = await financial_mcp_service.get_comprehensive_stock_info(symbol)
        elif data_type == "historical":
            result = await financial_mcp_service.get_historical_stock_prices(symbol, period=period)
        elif data_type == "statements":
            result = await financial_mcp_service.get_financial_statements(symbol, "income_stmt")
        elif data_type == "news":
            result = await financial_mcp_service.get_stock_news(symbol)
        elif data_type == "recommendations":
            result = await financial_mcp_service.get_analyst_recommendations(symbol)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid data_type. Use: comprehensive, historical, statements, news, recommendations"
            )
        
        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching financial data for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch financial data for {ticker}"
        )

@router.get("/conversation-history/{session_id}")
async def get_conversation_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get conversation history for a session
    """
    try:
        history = claude_agent.conversation_history.get(session_id, [])
        return {
            "session_id": session_id,
            "history": history,
            "total_exchanges": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error fetching conversation history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch conversation history"
        )

@router.delete("/conversation-history/{session_id}")
async def clear_conversation_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Clear conversation history for a session
    """
    try:
        if session_id in claude_agent.conversation_history:
            del claude_agent.conversation_history[session_id]
        
        return {
            "message": f"Conversation history cleared for session {session_id}",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear conversation history"
        )

@router.post("/watchlist/chat")
async def chat_with_watchlist_stock(
    request: WatchlistChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat about stocks in user's watchlist only
    """
    try:
        # For now, we'll work without user authentication
        # In production, you'd get user_id from JWT token
        user_id = request.user_id or 1
        
        # Get user's watchlist
        user_watchlist = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
        watchlist_symbols = [item.symbol for item in user_watchlist]
        
        # If no watchlist, provide a demo/default watchlist for testing
        demo_mode = False
        if not watchlist_symbols:
            # Demo watchlist for unauthenticated users or empty watchlists
            watchlist_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
            demo_mode = True
        
        # Create session ID based on ticker if specified
        session_id = f"watchlist_{request.ticker or 'general'}_{user_id}"
        
        # Add watchlist context to query - no more demo mode messaging
        context_query = f"{request.query}\n\nAvailable stocks for analysis: {', '.join(watchlist_symbols)}"
        
        if request.ticker:
            if request.ticker.upper() not in watchlist_symbols:
                # Allow analysis of any stock, but note watchlist status
                context_query = f"Focus on {request.ticker}: {request.query}\n\nNote: {request.ticker} is not in the user's watchlist but analysis is available."
            else:
                context_query = f"Focus on {request.ticker}: {request.query}"
        
        # Use Claude agent to analyze
        result = await claude_agent.analyze_query(
            query=context_query,
            session_id=session_id,
            user_context={
                "watchlist": watchlist_symbols,
                "focused_ticker": request.ticker,
                "platform": "watchlist_chat"
            }
        )
        
        if "error" in result:
            return ChatResponse(
                response=result.get("response", "An error occurred"),
                session_id=session_id,
                timestamp=result.get("timestamp", ""),
                error=result["error"]
            )
        
        return ChatResponse(
            response=result["response"],
            financial_data_used=result.get("financial_data_used"),
            session_id=result["session_id"],
            timestamp=result["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in watchlist chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process watchlist chat request"
        )

@router.get("/watchlist/chat-sessions")
async def get_watchlist_chat_sessions(
    user_id: Optional[int] = 1,
    db: Session = Depends(get_db)
):
    """
    Get all chat sessions for watchlist stocks
    """
    try:
        # Get user's watchlist
        user_watchlist = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
        watchlist_symbols = [item.symbol for item in user_watchlist]
        
        # Filter conversation history for watchlist sessions
        watchlist_sessions = []
        
        for session_id, history in claude_agent.conversation_history.items():
            if session_id.startswith(f"watchlist_") and f"_{user_id}" in session_id:
                if history:
                    last_message = history[-1]
                    
                    # Extract ticker from session_id
                    parts = session_id.split('_')
                    ticker = parts[1] if len(parts) > 1 and parts[1] != 'general' else None
                    
                    # Generate session title
                    if ticker and ticker in watchlist_symbols:
                        title = f"{ticker} Analysis"
                    else:
                        title = "Watchlist Discussion"
                    
                    session = ChatSession(
                        session_id=session_id,
                        ticker=ticker,
                        title=title,
                        last_message=last_message["user_query"][:100] + "..." if len(last_message["user_query"]) > 100 else last_message["user_query"],
                        timestamp=last_message["timestamp"],
                        message_count=len(history)
                    )
                    watchlist_sessions.append(session)
        
        # Sort by timestamp (most recent first)
        watchlist_sessions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return {
            "sessions": watchlist_sessions,
            "total_sessions": len(watchlist_sessions),
            "watchlist_symbols": watchlist_symbols
        }
        
    except Exception as e:
        logger.error(f"Error fetching watchlist chat sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch chat sessions"
        )

@router.delete("/watchlist/chat-sessions/{session_id}")
async def delete_watchlist_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a specific watchlist chat session
    """
    try:
        if session_id in claude_agent.conversation_history:
            del claude_agent.conversation_history[session_id]
        
        return {
            "message": f"Chat session {session_id} deleted successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete chat session"
        )