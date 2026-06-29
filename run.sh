#!/bin/bash
# Quick start script for CookingSite

set -e

echo "🍳 CookingSite - Quick Start"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env exists
if [ ! -f backend/.env ]; then
  echo -e "${YELLOW}Creating backend/.env from .env.example${NC}"
  cp .env.example backend/.env
  echo -e "${RED}⚠️  Please edit backend/.env and add OPENAI_API_KEY${NC}"
fi

# Function to run component
run_component() {
  local name=$1
  local cmd=$2
  echo -e "${GREEN}Starting $name...${NC}"
  eval "$cmd" &
  sleep 2
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
  echo -e "${RED}Python 3 not found${NC}"
  exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
  echo -e "${RED}Node.js not found${NC}"
  exit 1
fi

# Check Docker (optional)
if ! command -v docker &> /dev/null; then
  echo -e "${YELLOW}Docker not found - you'll need PostgreSQL running locally${NC}"
fi

# Setup Backend
echo ""
echo -e "${GREEN}=== Setting up Backend ===${NC}"
cd backend

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate venv
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
  source venv/Scripts/activate
fi

echo "Installing dependencies..."
pip install -q -r requirements.txt

cd ..

# Start PostgreSQL if Docker available
if command -v docker &> /dev/null; then
  echo ""
  echo -e "${GREEN}Starting PostgreSQL container...${NC}"
  docker run -d \
    --name cookingsite-db \
    -e POSTGRES_USER=cookingsite \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=cookingsite \
    -p 5432:5432 \
    postgres:16-alpine 2>/dev/null || echo "PostgreSQL container already running"
  sleep 3
fi

# Setup Frontend
echo ""
echo -e "${GREEN}=== Setting up Frontend ===${NC}"
cd frontend
npm install -q
cd ..

# Start components
echo ""
echo -e "${GREEN}=== Starting Components ===${NC}"
echo ""
echo -e "${YELLOW}Backend running on http://localhost:8000${NC}"
echo -e "${YELLOW}Frontend running on http://localhost:3000${NC}"
echo -e "${YELLOW}API Docs at http://localhost:8000/docs${NC}"
echo ""

# Start Backend
run_component "Backend" "cd backend && source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null ; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

# Start Frontend
run_component "Frontend" "cd frontend && npm run dev"

# Wait for user interrupt
echo -e "${GREEN}✅ All services started!${NC}"
echo "Press Ctrl+C to stop"
wait
