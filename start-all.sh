#!/bin/bash
# PoseFit Startup Script

# Colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Store the root directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}            PoseFit Application Starter${NC}"
echo -e "${GREEN}======================================================${NC}"
echo ""

# Check if required directories exist
if [ ! -d "$ROOT_DIR/PoseFit_Trainer/AI_PersonTrainer backend" ]; then
    echo -e "${RED}ERROR: Backend directory not found!${NC}"
    echo -e "${RED}Please ensure the project structure is correct.${NC}"
    exit 1
fi

if [ ! -d "$ROOT_DIR/PoseFit_Trainer/personal-trainer-auth" ]; then
    echo -e "${RED}ERROR: Frontend directory not found!${NC}"
    echo -e "${RED}Please ensure the project structure is correct.${NC}"
    exit 1
fi

if [ ! -d "$ROOT_DIR/PoseFit_assistant" ]; then
    echo -e "${RED}ERROR: PoseFit Assistant directory not found!${NC}"
    echo -e "${RED}Please ensure the project structure is correct.${NC}"
    exit 1
fi

if [ ! -d "$ROOT_DIR/posefit-landing" ]; then
    echo -e "${RED}ERROR: PoseFit Landing directory not found!${NC}"
    echo -e "${RED}Please ensure the project structure is correct.${NC}"
    exit 1
fi

# Check for Python installation
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python is not installed or not in PATH!${NC}"
    echo -e "${RED}Please install Python and ensure it's added to your PATH.${NC}"
    exit 1
fi

# Check for Node.js installation
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed or not in PATH!${NC}"
    echo -e "${RED}Please install Node.js and ensure it's added to your PATH.${NC}"
    exit 1
fi

# Check .env file exists, if not generate it
if [ ! -f "$ROOT_DIR/PoseFit_Trainer/AI_PersonTrainer backend/.env" ]; then
    echo -e "${YELLOW}Creating .env file and generating secret key...${NC}"
    cd "$ROOT_DIR/PoseFit_Trainer/AI_PersonTrainer backend"
    python3 generate_key.py
    cd "$ROOT_DIR"
fi

# Check for Docker presence (optional)
if command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker is available. Would you like to use Docker? (y/n)${NC}"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Starting with Docker...${NC}"
        docker-compose up -d
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}======================================================${NC}"
            echo -e "${GREEN}Application started successfully with Docker!${NC}"
            echo -e "${CYAN}The landing page is available at: http://localhost:4000${NC}"
            echo -e "${CYAN}The PoseFit Assistant is available at: http://localhost:3001${NC}"
            echo -e "${CYAN}The PoseFit Trainer is available at: http://localhost:3000${NC}"
            echo -e "${CYAN}The backend API is available at: http://localhost:8002${NC}"
            echo -e "${CYAN}API documentation: http://localhost:8002/api/docs${NC}"
            echo -e "${GREEN}======================================================${NC}"
            echo ""
            echo -e "${YELLOW}Press any key to exit...${NC}"
            read -n 1
            exit 0
        else
            echo -e "${YELLOW}Docker failed to start. Falling back to direct execution...${NC}"
        fi
    fi
fi

# Clean temp videos directory
echo -e "${YELLOW}Cleaning temporary video files...${NC}"
if [ -d "$ROOT_DIR/PoseFit_Trainer/AI_PersonTrainer backend/temp_videos" ]; then
    rm -f "$ROOT_DIR/PoseFit_Trainer/AI_PersonTrainer backend/temp_videos/"*
fi

# Check for and kill processes using port 8002
echo -e "${YELLOW}Checking for processes using port 8002...${NC}"
PORT_PID=$(lsof -i:8002 -t 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo -e "${YELLOW}Found process(es) using port 8002, terminating...${NC}"
    kill -9 $PORT_PID 2>/dev/null
fi

# Kill any existing processes
echo -e "${YELLOW}Checking for existing processes...${NC}"
pkill -f "python.*api_server.py" || true
pkill -f "node.*npm run dev" || true
pkill -f "node.*convex dev" || true
pkill -f "uvicorn" || true

# First, start the API server
echo -e "${YELLOW}Starting backend API server...${NC}"
cd "$ROOT_DIR/PoseFit_Trainer/AI_PersonTrainer backend" && python3 api_server.py &
API_SERVER_PID=$!

# Wait a moment to ensure API server starts first
echo -e "${YELLOW}Waiting for API server to initialize...${NC}"
sleep 5

# Check if port 8002 is in use by our process
if nc -z localhost 8002 &>/dev/null; then
    echo -e "${GREEN}API server appears to be running on port 8002.${NC}"
else
    echo -e "${YELLOW}WARNING: API server may not have started correctly.${NC}"
    echo -e "${YELLOW}Please check the API Server window for errors.${NC}"
    read -n 1
fi

# Start the PoseFit Trainer frontend
echo -e "${YELLOW}Starting PoseFit Trainer frontend...${NC}"
cd "$ROOT_DIR/PoseFit_Trainer/personal-trainer-auth" && PORT=3000 npm run dev &
TRAINER_PID=$!

# Start the Convex development server for PoseFit Assistant
echo -e "${YELLOW}Starting Convex development server...${NC}"
cd "$ROOT_DIR/PoseFit_assistant" && npx convex dev &
CONVEX_PID=$!

# Start the PoseFit Assistant
echo -e "${YELLOW}Starting PoseFit Assistant...${NC}"
cd "$ROOT_DIR/PoseFit_assistant" && PORT=3001 npm run dev &
ASSISTANT_PID=$!

# Start the Landing Page
echo -e "${YELLOW}Starting PoseFit Landing Page...${NC}"
cd "$ROOT_DIR/posefit-landing" && PORT=4000 npm run dev &
LANDING_PID=$!

echo ""
echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}All services are starting. Please wait a moment for them to initialize.${NC}"
echo ""
echo -e "${CYAN}The landing page is available at: http://localhost:4000${NC}"
echo -e "${CYAN}The PoseFit Assistant is available at: http://localhost:3001${NC}"
echo -e "${CYAN}The PoseFit Trainer is available at: http://localhost:3000${NC}"
echo -e "${CYAN}The backend API is available at: http://localhost:8002${NC}"
echo -e "${CYAN}API documentation: http://localhost:8002/api/docs${NC}"
echo ""
echo -e "${YELLOW}If you have connection issues:${NC}"
echo -e "${YELLOW}  1. Ensure Python is installed with all required packages${NC}"
echo -e "${YELLOW}  2. Ensure Node.js is installed${NC}"
echo -e "${YELLOW}  3. Check that required ports are free (8002, 3000, 3001, 4000)${NC}"
echo -e "${GREEN}======================================================${NC}"
echo ""
echo -e "${GREEN}Services started successfully!${NC}"
echo -e "${YELLOW}Press Ctrl+C to exit and stop all services...${NC}"

# Keep script running and capture Ctrl+C to gracefully shutdown
trap 'echo -e "\n${YELLOW}Shutting down services...${NC}"; kill $API_SERVER_PID $TRAINER_PID $ASSISTANT_PID $LANDING_PID $CONVEX_PID 2>/dev/null; echo -e "${GREEN}Services stopped.${NC}"; exit 0' INT
wait 