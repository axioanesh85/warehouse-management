@echo off
echo 🚀 Setting up Warehouse Management System

REM 1. Check prerequisites
echo.
echo 1. Checking prerequisites...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed. Please install Docker first.
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo ✓ Docker and Docker Compose are installed

REM 2. Build and start services
echo.
echo 2. Building and starting services...
docker-compose down
docker-compose build
docker-compose up -d

REM 3. Wait for database
echo.
echo 3. Waiting for database to be ready...
timeout /t 10 /nobreak >nul

REM 4. Initialize database
echo.
echo 4. Initializing database...
docker-compose exec app python init_db.py

REM 5. Show status
echo.
echo 5. Service status:
docker-compose ps

echo.
echo ✅ Setup complete!
echo.
echo 🌐 Application is running at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 🔐 Login with: admin / admin123

pause