#!/usr/bin/env python3
"""
Database connection test script
Run this to verify database connection before deployment
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import test_database_connection, engine
from app.config import settings

async def main():
    print("🔍 Testing database connection...")
    print(f"Database URL: {settings.DATABASE_URL[:20]}...")
    
    try:
        # Test connection
        if await test_database_connection():
            print("✅ Database connection successful!")
            
            # Test creating tables
            from app.database import Base
            from app.models import *
            
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created successfully!")
            
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)