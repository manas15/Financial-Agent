# Financial Agent - Updated Architecture

## Free Multi-User Architecture

### Tech Stack
- **Frontend**: Next.js + React (deployed on Vercel)
- **Backend**: FastAPI (deployed on Vercel Serverless)
- **Database**: Supabase PostgreSQL (free tier - 500MB)
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage (for charts/exports)
- **Hosting**: 100% free using Vercel + Supabase free tiers

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Portfolio Table (per user)
```sql
CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR NOT NULL,
    shares FLOAT NOT NULL,
    cost_basis FLOAT NOT NULL,
    purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Price History (shared across users)
```sql
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR NOT NULL,
    date DATE NOT NULL,
    open_price FLOAT,
    high_price FLOAT,
    low_price FLOAT,
    close_price FLOAT NOT NULL,
    volume INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Analysis Cache (per user)
```sql
CREATE TABLE analysis_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    portfolio_snapshot TEXT, -- JSON
    analysis_result TEXT NOT NULL,
    analysis_type VARCHAR NOT NULL, -- daily/weekly/monthly/stock_research
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Watchlist (per user)
```sql
CREATE TABLE watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Data Flow
```
User Login → Supabase Auth → JWT Token
Portfolio Data → User-specific queries
Price Data → Shared cache (all users benefit)
Claude Analysis → User-specific results
```

### Cost Breakdown (Monthly)
- **Hosting**: $0 (Vercel free tier)
- **Database**: $0 (Supabase 500MB free)
- **Authentication**: $0 (Supabase Auth free)
- **Claude API**: $5-10 (usage-based)
- **Alpha Vantage**: $0 (free tier)
- **NewsAPI**: $0 (free tier)

**Total: $5-10/month for unlimited users**

### Deployment Architecture
```
Frontend (Vercel) → Backend API (Vercel Functions) → Supabase DB
     ↓                        ↓                          ↓
Mobile Access          Authentication              Multi-tenant Data
```

### Free Tier Limits
- **Vercel**: 100GB bandwidth, unlimited projects
- **Supabase**: 500MB database, 2GB bandwidth, 50MB storage
- **Expected Usage**: ~50MB database for 3 family members

This architecture supports 2-3 family members easily within free tiers.