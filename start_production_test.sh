#!/bin/bash

echo "🚀 CUR8.FUN Local Production Test"
echo "================================"

echo
echo "📋 Setting up environment..."
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual values before continuing!"
    read -p "Press Enter to continue..."
fi

echo
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo
echo "🐳 Starting PostgreSQL with Docker..."
docker-compose up -d db

echo
echo "⏳ Waiting for database to be ready..."
sleep 10

echo
echo "🌟 Starting app in production mode..."
export FLASK_ENV=production
export DATABASE_URL=postgresql://cur8fun:password@localhost:5432/cur8fun_db
gunicorn --config gunicorn.conf.py app:app &

echo
echo "🧪 App should be running on http://localhost:8000"
echo "🧪 Run: python test_production.py http://localhost:8000"

# Test the app
sleep 5
python test_production.py http://localhost:8000
