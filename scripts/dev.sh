#!/bin/bash
# Luminous API - Local Development Startup Script

echo "Starting Luminous API Platform..."

# Ensure we have a .env file
if [ ! -f .env ]; then
  echo "⚠️ .env file not found. Copying from .env.example..."
  cp .env.example .env
  
  # Generate a local AES key if it's just the placeholder
  if grep -q "0000000000000000000000000000000000000000000000000000000000000000" .env; then
    NEW_KEY=$(openssl rand -hex 32)
    sed -i.bak "s/0000000000000000000000000000000000000000000000000000000000000000/$NEW_KEY/" .env
    echo "✅ Generated new AES encryption key in .env"
  fi
fi

# Load environment variables
source .env

echo "📦 Starting Docker containers (Postgres, Redis, Backend, Frontend, Celery)..."
docker-compose up -d --build

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🔄 Running Alembic database migrations..."
docker-compose exec api alembic upgrade head

echo "🚀 Luminous API Platform is running!"
echo "➡️ Frontend: http://localhost:3000"
echo "➡️ Backend API: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
