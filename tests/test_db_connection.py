#!/usr/bin/env python3

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test database connection with different configurations"""
    
    db_configs = [
        # Try with just 'postgres' username (port 5432)
        f"postgresql://postgres:iufnb4EPDiTffka5@aws-0-us-west-1.pooler.supabase.com:5432/postgres",
        
        # Try with just 'postgres' username (port 6543) 
        f"postgresql://postgres:iufnb4EPDiTffka5@aws-0-us-west-1.pooler.supabase.com:6543/postgres",
        
        # Current config (port 5432)
        f"postgresql://postgres.rwnkeqmqwoedtrfzlaal:iufnb4EPDiTffka5@aws-0-us-west-1.pooler.supabase.com:5432/postgres",
        
        # Original config (port 6543) 
        f"postgresql://postgres.rwnkeqmqwoedtrfzlaal:iufnb4EPDiTffka5@aws-0-us-west-1.pooler.supabase.com:6543/postgres",
        
        # Direct connection
        f"postgresql://postgres:iufnb4EPDiTffka5@db.rwnkeqmqwoedtrfzlaal.supabase.co:5432/postgres"
    ]
    
    for i, db_url in enumerate(db_configs, 1):
        print(f"\n--- Testing Configuration {i} ---")
        print(f"URL: {db_url}")
        
        try:
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ SUCCESS: Connected to PostgreSQL")
            print(f"Version: {version[0]}")
            
            # Test if our tables exist
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            tables = cursor.fetchall()
            print(f"Tables found: {[table[0] for table in tables]}")
            
            cursor.close()
            conn.close()
            return db_url  # Return the working URL
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
    
    return None

if __name__ == "__main__":
    working_url = test_connection()
    if working_url:
        print(f"\n🎉 Use this working URL: {working_url}")
    else:
        print(f"\n❌ No working database URL found")