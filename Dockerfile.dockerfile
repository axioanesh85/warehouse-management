# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run as non-root user
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

USER user

# Start command with retry logic
CMD ["sh", "-c", " \
    echo '🚀 Starting application...' && \
    echo '📊 Testing database connection...' && \
    python -c \"\
import asyncio, sys; \
from app.database import test_database_connection; \
async def test(): \
    for i in range(5): \
        try: \
            if await test_database_connection(): \
                print('✅ Database connection successful'); \
                return True \
            else: \
                print(f\"Attempt {i+1}/5: Database connection failed, retrying...\"); \
                await asyncio.sleep(5) \
        except Exception as e: \
            print(f\"Attempt {i+1}/5: Error - {e}\"); \
            await asyncio.sleep(5) \
    print('❌ Failed to connect to database after 5 attempts'); \
    return False \
asyncio.run(test())\" && \
    echo '🗄️ Running database migrations...' && \
    alembic upgrade head && \
    echo '👤 Creating default admin user...' && \
    python -c \"\
import asyncio; \
from app.utils import create_default_admin; \
asyncio.run(create_default_admin())\" && \
    echo '🌐 Starting server...' && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} \
    "]