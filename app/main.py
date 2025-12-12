from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import test_database_connection
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Warehouse Management System...")
    
    # Test database connection
    db_connected = await test_database_connection()
    if not db_connected:
        logger.error("❌ Database connection failed! Application may not work properly.")
    
    # Create tables and default user
    from app.utils import initialize_database
    await initialize_database()
    
    logger.info("✅ Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down application...")

app = FastAPI(
    title="Warehouse Management System",
    description="Income & Expenses Management",
    version="1.0.0",
    lifespan=lifespan
)