from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date, datetime

# User authentication schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Watchlist schemas (for research stock lists)
class WatchlistCreate(BaseModel):
    symbol: str
    notes: Optional[str] = None
    
    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper().strip()

class WatchlistResponse(BaseModel):
    id: int
    symbol: str
    current_price: Optional[float]
    change: Optional[float] = 0.0
    change_percent: Optional[float] = 0.0
    volume: Optional[int] = 0
    notes: Optional[str]
    added_date: date
    
    class Config:
        from_attributes = True

# Generic response schemas
class SuccessResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
    status_code: int = 400