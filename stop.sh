#!/bin/bash
# CEO Tracker - Stop all services

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping CEO Tracker services...${NC}"

# Kill processes by name
pkill -f "uvicorn app.main:app" 2>/dev/null && echo -e "${GREEN}✓ Backend stopped${NC}" || echo -e "${YELLOW}✓ Backend not running${NC}"
pkill -f "celery.*workers.tasks" 2>/dev/null && echo -e "${GREEN}✓ Celery worker stopped${NC}" || echo -e "${YELLOW}✓ Celery worker not running${NC}"
pkill -f "vite.*--mode" 2>/dev/null && echo -e "${GREEN}✓ Frontend stopped${NC}" || echo -e "${YELLOW}✓ Frontend not running${NC}"

# Clean up PID files
rm -f /home/fire/ceo-tracker/backend/logs/*.pid 2>/dev/null

echo -e "${GREEN}All services stopped${NC}"
