@echo off
echo 🚀 CUR8.FUN Local Production Test
echo ================================

echo.
echo 📋 Setting up environment...
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo ⚠️  Please edit .env with your actual values before continuing!
    pause
)

echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🐳 Starting PostgreSQL with Docker...
docker-compose up -d db

echo.
echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak > nul

echo.
echo 🌟 Starting app in production mode...
set FLASK_ENV=production
set DATABASE_URL=postgresql://cur8fun:password@localhost:5432/cur8fun_db
gunicorn --config gunicorn.conf.py app:app

echo.
echo 🧪 App should be running on http://localhost:8000
echo 🧪 Run: python test_production.py http://localhost:8000
pause
