from sqlalchemy import select
from app.database import engine, Base, AsyncSessionLocal
from app.models import User
from app.auth import get_password_hash
import logging

logger = logging.getLogger(__name__)

async def initialize_database():
    """Initialize database: create tables and default admin user"""
    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")
        
        # Create default admin user
        await create_default_admin()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def create_default_admin():
    """Create default admin user if it doesn't exist"""
    async with AsyncSessionLocal() as db:
        try:
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
                logger.info("✅ Default admin user created: username=admin, password=admin123")
            else:
                logger.info("ℹ️ Admin user already exists")
                
        except Exception as e:
            logger.error(f"❌ Failed to create admin user: {e}")
            await db.rollback()