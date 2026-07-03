#!/bin/bash
# CEO Tracker - Start all services
# This script starts the backend, frontend, and Celery worker
#
# Usage:
#   ./start.sh              - Start all services
#   ./start.sh --refresh    - Start all services and trigger feed refresh
#   ./start.sh --reseed     - Recreate database and start all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
REFRESH_FEEDS=false
RESEED_DB=false

for arg in "$@"; do
    case $arg in
        --refresh)
            REFRESH_FEEDS=true
            ;;
        --reseed)
            RESEED_DB=true
            ;;
        *)
            echo -e "${RED}Unknown argument: $arg${NC}"
            echo "Usage: $0 [--refresh] [--reseed]"
            exit 1
            ;;
    esac
done

# Project paths
BACKEND_DIR="/home/fire/ceo-tracker/backend"
FRONTEND_DIR="/home/fire/ceo-tracker/frontend"

# Log directory
LOG_DIR="$BACKEND_DIR/logs"
mkdir -p "$LOG_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  CEO Tracker - Starting All Services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}Port $port is already in use${NC}"
        return 1
    fi
    return 0
}

# Function to stop all services
stop_services() {
    echo ""
    echo -e "${RED}Stopping all services...${NC}"

    # Kill processes by name
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "celery.*workers.tasks" 2>/dev/null || true
    pkill -f "vite.*--mode" 2>/dev/null || true

    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Set trap for cleanup
trap stop_services SIGINT SIGTERM

# Check if ports are available
echo -e "${BLUE}Checking ports...${NC}"
if ! check_port 8000; then
    echo -e "${RED}Backend port 8000 unavailable. Stop existing services first.${NC}"
    exit 1
fi
if ! check_port 3000; then
    echo -e "${RED}Frontend port 3000 unavailable. Stop existing services first.${NC}"
    exit 1
fi

# Check if Valkey is running
echo -e "${BLUE}Checking Valkey...${NC}"
if ! systemctl is-active --quiet valkey; then
    echo -e "${YELLOW}Valkey is not running. Starting it...${NC}"
    sudo systemctl start valkey
    sleep 2
fi

# Navigate to backend and start services
cd "$BACKEND_DIR"

# Handle --reseed option
if [ "$RESEED_DB" = true ]; then
    echo -e "${YELLOW}Recreating database...${NC}"
    source venv/bin/activate
    rm -f ceo_tracker.db
    python init_db.py
    echo -e "${GREEN}Database recreated${NC}"
    echo ""
fi

echo -e "${BLUE}Starting backend...${NC}"
source venv/bin/activate

# Start FastAPI backend (background)
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
    > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}Backend started (PID: $BACKEND_PID)${NC}"
echo -e "  Logs: $LOG_DIR/backend.log"
echo -e "  URL: http://localhost:8000"

# Wait a moment for backend to start
sleep 2

# Start Celery worker (background)
echo -e "${BLUE}Starting Celery worker...${NC}"
nohup celery -A workers.tasks worker --loglevel=info \
    > "$LOG_DIR/celery.log" 2>&1 &
CELERY_PID=$!
echo -e "${GREEN}Celery worker started (PID: $CELERY_PID)${NC}"
echo -e "  Logs: $LOG_DIR/celery.log"

# Start frontend
echo -e "${BLUE}Starting frontend...${NC}"
cd "$FRONTEND_DIR"
nohup npm run dev \
    > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "  Logs: $LOG_DIR/frontend.log"
echo -e "  URL: http://localhost:3000"

# Save PIDs for cleanup
echo "$BACKEND_PID" > "$LOG_DIR/backend.pid"
echo "$CELERY_PID" > "$LOG_DIR/celery.pid"
echo "$FRONTEND_PID" > "$LOG_DIR/frontend.pid"

# Handle --refresh option
if [ "$REFRESH_FEEDS" = true ]; then
    echo ""
    echo -e "${BLUE}Waiting for services to be ready...${NC}"
    sleep 5

    echo -e "${BLUE}Triggering feed refresh...${NC}"

    # Try multiple times in case backend isn't ready yet
    for i in {1..3}; do
        if curl -s -X POST http://localhost:8000/api/feeds/refresh > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Feed refresh triggered${NC}"
            echo -e "${YELLOW}Note: It may take a few minutes to process all 20 feeds${NC}"
            break
        else
            if [ $i -lt 3 ]; then
                echo -e "${YELLOW}Backend not ready, waiting... ($i/3)${NC}"
                sleep 3
            else
                echo -e "${RED}Failed to trigger feed refresh${NC}"
            fi
        fi
    done
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All services started successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Services:${NC}"
echo -e "  • Backend:  http://localhost:8000"
echo -e "  • Frontend: http://localhost:3000"
echo -e "  • API Docs:  http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  • Backend:  tail -f $LOG_DIR/backend.log"
echo -e "  • Celery:   tail -f $LOG_DIR/celery.log"
echo -e "  • Frontend: tail -f $LOG_DIR/frontend.log"
echo ""
echo -e "${BLUE}Usage:${NC}"
echo -e "  $0              - Start all services"
echo -e "  $0 --refresh    - Start and trigger feed refresh"
echo -e "  $0 --reseed     - Recreate database and start"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait indefinitely (until Ctrl+C)
wait
