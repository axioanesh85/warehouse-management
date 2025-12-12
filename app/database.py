from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Get database URL from settings
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

# Log the database URL (masked for security)
if DATABASE_URL:
    masked_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    logger.info(f"Database URL: ***@{masked_url}")
else:
    logger.error("DATABASE_URL is not set!")
    raise ValueError("DATABASE_URL environment variable is required")

# Create async engine
try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300,  # Recycle connections every 5 minutes
    )
    logger.info("✅ Database engine created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}")
    raise

# Create async session
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db():
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def test_database_connection():
    """Test database connection"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False