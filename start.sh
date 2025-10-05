#!/bin/bash

echo "🚀 Starting MyWave application with PostgreSQL and MinIO..."

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Initialize database
echo "🗄️ Initializing database..."
python3 init_db_simple.py

# Show status
echo "📊 Service status:"
docker-compose ps

echo ""
echo "🎉 All services are running!"
echo ""
echo "📋 Service URLs:"
echo "  🌐 Frontend: http://localhost"
echo "  🔧 Backend API: http://localhost:8000"
echo "  📊 API Docs: http://localhost:8000/docs"
echo "  🗄️ PostgreSQL: localhost:5432"
echo "  📦 MinIO Console: http://localhost:9001"
echo "  📦 MinIO API: http://localhost:9000"
echo ""
echo "🔑 MinIO Credentials:"
echo "  Username: minioadmin"
echo "  Password: minioadmin123"
echo ""
echo "🔑 PostgreSQL Credentials:"
echo "  Database: mywave"
echo "  Username: mywave"
echo "  Password: mywave_password"
echo ""
echo "To stop all services: docker-compose down"
echo "To view logs: docker-compose logs -f"
