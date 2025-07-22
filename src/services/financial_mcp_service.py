"""
MCP-style Financial Data Service
Provides comprehensive financial data similar to MCP servers but integrated directly into our FastAPI backend
"""

import yfinance as yf
import pandas as pd
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FinancialMCPService:
    """
    Financial data service that provides MCP-style tools for comprehensive stock analysis
    """
    
    def __init__(self):
        self.cache = {}  # Simple caching mechanism
        
    async def get_historical_stock_prices(
        self, 
        ticker: str, 
        period: str = "1mo", 
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """
        Get historical stock prices for a given ticker symbol
        
        Args:
            ticker: The ticker symbol (e.g., "AAPL")
            period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        """
        try:
            company = yf.Ticker(ticker)
            hist_data = company.history(period=period, interval=interval)
            
            if hist_data.empty:
                return {"error": f"No historical data found for {ticker}"}
            
            # Convert to JSON serializable format
            hist_data = hist_data.reset_index()
            hist_data['Date'] = hist_data['Date'].dt.strftime('%Y-%m-%d')
            
            return {
                "ticker": ticker,
                "period": period,
                "interval": interval,
                "data": hist_data.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error getting historical data for {ticker}: {e}")
            return {"error": str(e)}
    
    async def get_comprehensive_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive stock information including all available data points
        """
        try:
            company = yf.Ticker(ticker)
            info = company.info
            
            # Get additional data
            hist = company.history(period="1d")
            year_hist = company.history(period="1y")
            
            # Calculate additional metrics
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            
            comprehensive_data = {
                "ticker": ticker,
                "basic_info": {
                    "longName": info.get("longName"),
                    "shortName": info.get("shortName"),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "country": info.get("country"),
                    "website": info.get("website"),
                    "businessSummary": info.get("businessSummary", "")[:500] + "..." if info.get("businessSummary") else None
                },
                "price_data": {
                    "currentPrice": current_price,
                    "previousClose": info.get("previousClose"),
                    "open": info.get("open"),
                    "dayLow": info.get("dayLow"),
                    "dayHigh": info.get("dayHigh"),
                    "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                    "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                    "volume": info.get("volume"),
                    "averageVolume": info.get("averageVolume")
                },
                "financial_metrics": {
                    "marketCap": info.get("marketCap"),
                    "enterpriseValue": info.get("enterpriseValue"),
                    "trailingPE": info.get("trailingPE"),
                    "forwardPE": info.get("forwardPE"),
                    "pegRatio": info.get("pegRatio"),
                    "priceToBook": info.get("priceToBook"),
                    "priceToSales": info.get("priceToSalesTrailing12Months"),
                    "beta": info.get("beta")
                },
                "financial_health": {
                    "totalRevenue": info.get("totalRevenue"),
                    "grossProfits": info.get("grossProfits"),
                    "operatingMargins": info.get("operatingMargins"),
                    "profitMargins": info.get("profitMargins"),
                    "returnOnEquity": info.get("returnOnEquity"),
                    "returnOnAssets": info.get("returnOnAssets"),
                    "debtToEquity": info.get("debtToEquity"),
                    "currentRatio": info.get("currentRatio"),
                    "quickRatio": info.get("quickRatio")
                },
                "dividends_earnings": {
                    "dividendYield": info.get("dividendYield"),
                    "dividendRate": info.get("dividendRate"),
                    "trailingEps": info.get("trailingEps"),
                    "forwardEps": info.get("forwardEps"),
                    "sharesOutstanding": info.get("sharesOutstanding"),
                    "bookValue": info.get("bookValue")
                }
            }
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive stock info for {ticker}: {e}")
            return {"error": str(e)}
    
    async def get_financial_statements(
        self, 
        ticker: str, 
        statement_type: str = "income_stmt",
        quarterly: bool = False
    ) -> Dict[str, Any]:
        """
        Get financial statements (income statement, balance sheet, cash flow)
        
        Args:
            ticker: Stock ticker symbol
            statement_type: income_stmt, balance_sheet, or cashflow
            quarterly: If True, get quarterly data; otherwise annual
        """
        try:
            company = yf.Ticker(ticker)
            
            if statement_type == "income_stmt":
                data = company.quarterly_income_stmt if quarterly else company.income_stmt
            elif statement_type == "balance_sheet":
                data = company.quarterly_balance_sheet if quarterly else company.balance_sheet
            elif statement_type == "cashflow":
                data = company.quarterly_cashflow if quarterly else company.cashflow
            else:
                return {"error": f"Invalid statement type: {statement_type}"}
            
            if data.empty:
                return {"error": f"No {statement_type} data found for {ticker}"}
            
            # Convert to JSON serializable format
            result = []
            for column in data.columns:
                date_str = column.strftime("%Y-%m-%d") if isinstance(column, pd.Timestamp) else str(column)
                date_obj = {"date": date_str}
                
                for index, value in data[column].items():
                    date_obj[index] = None if pd.isna(value) else value
                
                result.append(date_obj)
            
            return {
                "ticker": ticker,
                "statement_type": statement_type,
                "quarterly": quarterly,
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Error getting {statement_type} for {ticker}: {e}")
            return {"error": str(e)}
    
    async def get_stock_news(self, ticker: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get latest news for a stock
        """
        try:
            company = yf.Ticker(ticker)
            news = company.news
            
            if not news:
                return {"error": f"No news found for {ticker}"}
            
            processed_news = []
            for article in news[:limit]:
                # Handle different news format structures
                if isinstance(article, dict):
                    title = ""
                    summary = ""
                    url = ""
                    published_at = ""
                    provider = ""
                    
                    # Try different possible structures
                    if "content" in article and article["content"]:
                        content = article["content"]
                        title = content.get("title", "")
                        summary = content.get("summary", "")
                        url = content.get("canonicalUrl", {}).get("url", "") if content.get("canonicalUrl") else ""
                    else:
                        # Direct structure
                        title = article.get("title", "")
                        summary = article.get("summary", "")
                        url = article.get("link", "")
                    
                    published_at = article.get("publishedAt", article.get("providerPublishTime", ""))
                    provider = article.get("provider", {}).get("displayName", "") if article.get("provider") else article.get("publisher", "")
                    
                    if title:  # Only add if we have at least a title
                        processed_news.append({
                            "title": title,
                            "summary": summary,
                            "url": url,
                            "publishedAt": published_at,
                            "provider": provider
                        })
            
            return {
                "ticker": ticker,
                "news": processed_news,
                "current_date": datetime.now().strftime("%Y-%m-%d"),
                "data_freshness": "Real-time from Yahoo Finance"
            }
            
        except Exception as e:
            logger.error(f"Error getting news for {ticker}: {e}")
            return {"error": str(e)}
    
    async def get_upcoming_earnings_and_events(self, ticker: str) -> Dict[str, Any]:
        """
        Get upcoming earnings and key events for a stock
        """
        try:
            company = yf.Ticker(ticker)
            
            # Get company calendar data (earnings dates, etc.)
            calendar_data = {}
            
            try:
                # Try to get earnings calendar
                calendar = company.calendar
                if calendar is not None and not calendar.empty:
                    calendar_data["earnings_calendar"] = calendar.to_dict('records')
            except:
                calendar_data["earnings_calendar"] = []
            
            # Get basic company info for additional context
            info = company.info
            
            # Extract relevant upcoming event information
            upcoming_events = {
                "ticker": ticker,
                "current_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "current_quarter": f"Q{((datetime.now().month - 1) // 3) + 1} {datetime.now().year}",
                "earnings_calendar": calendar_data.get("earnings_calendar", []),
                "company_info": {
                    "name": info.get("longName", ""),
                    "sector": info.get("sector", ""),
                    "industry": info.get("industry", ""),
                    "nextEarningsDate": info.get("nextEarningsDate"),
                    "lastEarningsDate": info.get("lastEarningsDate"),
                    "earningsQuarterlyGrowth": info.get("earningsQuarterlyGrowth"),
                    "revenueQuarterlyGrowth": info.get("revenueQuarterlyGrowth")
                },
                "note": "For specific upcoming events, recent news and earnings announcements should be checked"
            }
            
            return upcoming_events
            
        except Exception as e:
            logger.error(f"Error getting upcoming events for {ticker}: {e}")
            return {"error": str(e)}
    
    async def get_analyst_recommendations(self, ticker: str) -> Dict[str, Any]:
        """
        Get analyst recommendations and upgrades/downgrades
        """
        try:
            company = yf.Ticker(ticker)
            
            recommendations = {}
            
            # Get current recommendations
            try:
                rec_data = company.recommendations
                if not rec_data.empty:
                    recommendations["current"] = rec_data.to_dict('records')
            except:
                recommendations["current"] = []
            
            # Get upgrades/downgrades
            try:
                upgrades_data = company.upgrades_downgrades
                if not upgrades_data.empty:
                    # Get recent upgrades/downgrades (last 6 months)
                    cutoff_date = pd.Timestamp.now() - pd.DateOffset(months=6)
                    recent = upgrades_data[upgrades_data.index >= cutoff_date]
                    recommendations["recent_changes"] = recent.reset_index().to_dict('records')
            except:
                recommendations["recent_changes"] = []
            
            return {
                "ticker": ticker,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations for {ticker}: {e}")
            return {"error": str(e)}
    
    async def compare_stocks(self, tickers: List[str], metrics: List[str] = None) -> Dict[str, Any]:
        """
        Compare multiple stocks across key metrics
        """
        if metrics is None:
            metrics = ["marketCap", "trailingPE", "priceToBook", "returnOnEquity", "profitMargins", "beta"]
        
        comparison_data = {}
        
        for ticker in tickers:
            try:
                stock_info = await self.get_comprehensive_stock_info(ticker)
                if "error" not in stock_info:
                    comparison_data[ticker] = {}
                    
                    # Extract requested metrics
                    for metric in metrics:
                        value = None
                        for category in ["price_data", "financial_metrics", "financial_health", "dividends_earnings"]:
                            if category in stock_info and metric in stock_info[category]:
                                value = stock_info[category][metric]
                                break
                        comparison_data[ticker][metric] = value
                        
            except Exception as e:
                logger.error(f"Error comparing stock {ticker}: {e}")
                comparison_data[ticker] = {"error": str(e)}
        
        return {
            "comparison": comparison_data,
            "metrics": metrics
        }

# Global instance
financial_mcp_service = FinancialMCPService()