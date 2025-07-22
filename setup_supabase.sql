-- Financial Agent Database Schema for Supabase
-- Run this in the Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio holdings table
CREATE TABLE IF NOT EXISTS public.portfolio (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    symbol VARCHAR NOT NULL,
    shares DECIMAL(15,6) NOT NULL,
    cost_basis DECIMAL(15,2) NOT NULL,
    purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Price history table (shared across users)
CREATE TABLE IF NOT EXISTS public.price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(15,2),
    high_price DECIMAL(15,2),
    low_price DECIMAL(15,2),
    close_price DECIMAL(15,2) NOT NULL,
    volume BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analysis cache table
CREATE TABLE IF NOT EXISTS public.analysis_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    portfolio_snapshot TEXT, -- JSON string
    analysis_result TEXT NOT NULL,
    analysis_type VARCHAR NOT NULL, -- daily, weekly, monthly, stock_research
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Watchlist table
CREATE TABLE IF NOT EXISTS public.watchlist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    symbol VARCHAR NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON public.portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_symbol ON public.portfolio(symbol);
CREATE INDEX IF NOT EXISTS idx_price_history_symbol_date ON public.price_history(symbol, date);
CREATE INDEX IF NOT EXISTS idx_analysis_cache_user_id ON public.analysis_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_cache_type ON public.analysis_cache(analysis_type);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON public.watchlist(user_id);

-- Add unique constraint to prevent duplicate portfolio entries
CREATE UNIQUE INDEX IF NOT EXISTS idx_portfolio_user_symbol 
ON public.portfolio(user_id, symbol);

-- Add unique constraint to prevent duplicate price history
CREATE UNIQUE INDEX IF NOT EXISTS idx_price_history_symbol_date_unique 
ON public.price_history(symbol, date);

-- Add unique constraint to prevent duplicate watchlist entries
CREATE UNIQUE INDEX IF NOT EXISTS idx_watchlist_user_symbol 
ON public.watchlist(user_id, symbol);

-- Set up Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.watchlist ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view own profile" ON public.users
FOR SELECT USING (auth.uid() = id::text::uuid);

CREATE POLICY "Users can update own profile" ON public.users
FOR UPDATE USING (auth.uid() = id::text::uuid);

-- RLS Policies for portfolio table
CREATE POLICY "Users can view own portfolio" ON public.portfolio
FOR SELECT USING (auth.uid() = user_id::text::uuid);

CREATE POLICY "Users can insert own portfolio" ON public.portfolio
FOR INSERT WITH CHECK (auth.uid() = user_id::text::uuid);

CREATE POLICY "Users can update own portfolio" ON public.portfolio
FOR UPDATE USING (auth.uid() = user_id::text::uuid);

CREATE POLICY "Users can delete own portfolio" ON public.portfolio
FOR DELETE USING (auth.uid() = user_id::text::uuid);

-- RLS Policies for analysis_cache table
CREATE POLICY "Users can view own analysis" ON public.analysis_cache
FOR SELECT USING (auth.uid() = user_id::text::uuid);

CREATE POLICY "Users can insert own analysis" ON public.analysis_cache
FOR INSERT WITH CHECK (auth.uid() = user_id::text::uuid);

CREATE POLICY "Users can delete own analysis" ON public.analysis_cache
FOR DELETE USING (auth.uid() = user_id::text::uuid);

-- RLS Policies for watchlist table
CREATE POLICY "Users can view own watchlist" ON public.watchlist
FOR SELECT USING (auth.uid() = user_id::text::uuid);

CREATE POLICY "Users can insert own watchlist" ON public.watchlist
FOR INSERT WITH CHECK (auth.uid() = user_id::text::uuid);

CREATE POLICY "Users can delete own watchlist" ON public.watchlist
FOR DELETE USING (auth.uid() = user_id::text::uuid);

-- Price history is readable by all authenticated users (shared data)
CREATE POLICY "Authenticated users can view price history" ON public.price_history
FOR SELECT USING (auth.role() = 'authenticated');

-- Only service role can insert price history (for our backend)
CREATE POLICY "Service role can manage price history" ON public.price_history
FOR ALL USING (auth.role() = 'service_role');

-- Add updated_at trigger function
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add updated_at triggers
CREATE TRIGGER handle_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_portfolio_updated_at
    BEFORE UPDATE ON public.portfolio
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();