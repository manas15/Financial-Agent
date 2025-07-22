from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.models.database import get_db, User, Watchlist
from src.api.schemas import (
    WatchlistCreate, WatchlistResponse, SuccessResponse
)
from src.api.auth import get_current_active_user
import yfinance as yf
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/watchlist", tags=["research-watchlist"])

@router.post("/", response_model=WatchlistResponse)
async def add_to_watchlist(
    watchlist_data: WatchlistCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add stock to research watchlist"""
    try:
        # Verify stock exists using Yahoo Finance directly
        ticker = yf.Ticker(watchlist_data.symbol.upper())
        info = ticker.info
        
        if not info or not info.get('currentPrice') and not info.get('regularMarketPrice'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock {watchlist_data.symbol} not found"
            )
        
        # Check if already in watchlist
        existing = db.query(Watchlist).filter(
            Watchlist.symbol == watchlist_data.symbol.upper(),
            Watchlist.user_id == current_user.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock {watchlist_data.symbol} is already in your watchlist"
            )
        
        # Add to watchlist
        watchlist_item = Watchlist(
            symbol=watchlist_data.symbol.upper(),
            user_id=current_user.id,
            notes=watchlist_data.notes
        )
        
        db.add(watchlist_item)
        db.commit()
        db.refresh(watchlist_item)
        
        # Get current price and market data
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0.0)
        previous_close = info.get('previousClose', current_price)
        change = float(current_price) - float(previous_close) if current_price and previous_close else 0.0
        change_percent = (change / float(previous_close)) * 100 if previous_close else 0.0
        volume = info.get('volume', 0)
        
        return WatchlistResponse(
            id=watchlist_item.id,
            symbol=watchlist_item.symbol,
            current_price=float(current_price) if current_price else 0.0,
            change=change,
            change_percent=change_percent,
            volume=volume,
            notes=watchlist_item.notes,
            added_date=watchlist_item.created_at.date()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add stock to watchlist"
        )

@router.get("/", response_model=List[WatchlistResponse])
async def get_watchlist(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's research watchlist with current prices"""
    try:
        watchlist_items = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()
        
        if not watchlist_items:
            return []
        
        result = []
        for item in watchlist_items:
            try:
                # Get current market data
                ticker = yf.Ticker(item.symbol)
                info = ticker.info
                
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0.0)
                previous_close = info.get('previousClose', current_price)
                change = float(current_price) - float(previous_close) if current_price and previous_close else 0.0
                change_percent = (change / float(previous_close)) * 100 if previous_close else 0.0
                volume = info.get('volume', 0)
                
                result.append(WatchlistResponse(
                    id=item.id,
                    symbol=item.symbol,
                    current_price=float(current_price) if current_price else 0.0,
                    change=change,
                    change_percent=change_percent,
                    volume=volume,
                    notes=item.notes,
                    added_date=item.created_at.date()
                ))
            except Exception as e:
                logger.error(f"Error getting data for {item.symbol}: {e}")
                # Return item with default values if data fetch fails
                result.append(WatchlistResponse(
                    id=item.id,
                    symbol=item.symbol,
                    current_price=0.0,
                    change=0.0,
                    change_percent=0.0,
                    volume=0,
                    notes=item.notes,
                    added_date=item.created_at.date()
                ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve watchlist"
        )

@router.delete("/{symbol}", response_model=SuccessResponse)
async def remove_from_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove stock from research watchlist"""
    try:
        watchlist_item = db.query(Watchlist).filter(
            Watchlist.symbol == symbol.upper(),
            Watchlist.user_id == current_user.id
        ).first()
        
        if not watchlist_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock {symbol} not found in your watchlist"
            )
        
        db.delete(watchlist_item)
        db.commit()
        
        return SuccessResponse(
            message=f"Stock {symbol} removed from watchlist successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove stock from watchlist"
        )