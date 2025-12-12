import asyncio
import os
import sys

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models import *
from app.auth import get_password_hash

async def init_database():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")
    
    # Create default admin user
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        
        # Check if admin exists
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                username="admin",
                email="admin@warehouse.com",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role="superuser",
                is_active=True
            )
            db.add(admin)
            await db.commit()
            print("✅ Default admin created: username=admin, password=admin123")
        else:
            print("ℹ️ Admin user already exists")

if __name__ == "__main__":
    asyncio.run(init_database())