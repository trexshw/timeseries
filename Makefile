.PHONY: help build up down logs test clean setup

# Default target
help:
	@echo "Available commands:"
	@echo "  build    - Build all Docker images"
	@echo "  up       - Start all services"
	@echo "  down     - Stop all services"
	@echo "  logs     - Show logs from all services"
	@echo "  test     - Run all tests"
	@echo "  clean    - Clean up containers and volumes"
	@echo "  setup    - Setup the development environment"

# Build all Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Run backend tests
test-backend:
	cd backend && python -m pytest

# Run frontend tests
test-frontend:
	cd frontend && npm test

# Run all tests
test: test-backend test-frontend

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Setup development environment
setup:
	@echo "Setting up development environment..."
	@echo "1. Starting InfluxDB..."
	docker-compose up -d influxdb
	@echo "2. Waiting for InfluxDB to be ready..."
	sleep 10
	@echo "3. Creating sample data..."
	cd backend && python scripts/setup.py
	@echo "4. Starting all services..."
	docker-compose up -d
	@echo "✅ Setup complete! Access the application at http://localhost:3000"

# Development helpers
dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm start

# Linting and formatting
lint-backend:
	cd backend && black . && flake8 . && mypy .

lint-frontend:
	cd frontend && npm run lint

lint: lint-backend lint-frontend

# Database operations
db-shell:
	docker-compose exec influxdb influx

db-backup:
	docker-compose exec influxdb influx backup /tmp/backup

db-restore:
	docker-compose exec influxdb influx restore /tmp/backup
