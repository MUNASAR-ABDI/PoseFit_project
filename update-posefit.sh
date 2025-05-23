#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}          PoseFit Update and Maintenance Script        ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo ""

# Get current date for backup names
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_DIR="./backups/$DATE"

# Function to handle errors
handle_error() {
    echo -e "${RED}ERROR: $1${NC}"
    exit 1
}

# Create backup directory
mkdir -p "$BACKUP_DIR" || handle_error "Failed to create backup directory"

# Backup user data
echo -e "${YELLOW}Backing up user data...${NC}"
cp -r PoseFit_Trainer/AI_PersonTrainer\ backend/user_profiles "$BACKUP_DIR/" || handle_error "Failed to backup user profiles"
cp PoseFit_Trainer/AI_PersonTrainer\ backend/user_data.json "$BACKUP_DIR/" || handle_error "Failed to backup user data"

# Backup saved workouts
echo -e "${YELLOW}Backing up workout videos...${NC}"
mkdir -p "$BACKUP_DIR/saved_workouts"
cp -r PoseFit_Trainer/AI_PersonTrainer\ backend/saved_workouts "$BACKUP_DIR/" || echo -e "${YELLOW}No workout videos to backup${NC}"

# Clean up old log files
echo -e "${YELLOW}Cleaning up log files...${NC}"
find PoseFit_Trainer/AI_PersonTrainer\ backend -name "*.log" -type f -mtime +7 -exec rm {} \; || echo -e "${YELLOW}No old log files to clean up${NC}"

# Update repository if git is available
if command -v git &> /dev/null; then
    echo -e "${YELLOW}Updating code from repository...${NC}"
    git pull || handle_error "Failed to update code from repository"
fi

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Updating using Docker...${NC}"
    
    # Stop containers
    docker-compose down || handle_error "Failed to stop Docker containers"
    
    # Rebuild and start containers
    docker-compose build || handle_error "Failed to build Docker containers"
    docker-compose up -d || handle_error "Failed to start Docker containers"
    
    echo -e "${GREEN}Docker containers updated and restarted successfully${NC}"
else
    echo -e "${YELLOW}Docker not available, using standard update process...${NC}"
    
    # Update backend dependencies
    echo -e "${YELLOW}Updating backend dependencies...${NC}"
    cd PoseFit_Trainer/AI_PersonTrainer\ backend || handle_error "Failed to access backend directory"
    pip install -r requirements.txt --upgrade || handle_error "Failed to update backend dependencies"
    cd ../.. || handle_error "Failed to return to root directory"
    
    # Update frontend dependencies
    echo -e "${YELLOW}Updating frontend dependencies...${NC}"
    cd PoseFit_Trainer/personal-trainer-auth || handle_error "Failed to access frontend directory"
    npm install || handle_error "Failed to update frontend dependencies"
    cd ../.. || handle_error "Failed to return to root directory"
    
    # Restart services if running on Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo -e "${YELLOW}Restarting services...${NC}"
        pkill -f "python.*api_server.py" || echo -e "${YELLOW}No API server process to kill${NC}"
        pkill -f "npm.*dev" || echo -e "${YELLOW}No frontend process to kill${NC}"
        
        # Start services
        bash start-all.sh || handle_error "Failed to start services"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}Restarting services on macOS...${NC}"
        pkill -f "python.*api_server.py" || echo -e "${YELLOW}No API server process to kill${NC}"
        pkill -f "npm.*dev" || echo -e "${YELLOW}No frontend process to kill${NC}"
        
        # Start services
        bash start-all.sh || handle_error "Failed to start services"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo -e "${YELLOW}Please restart services manually on Windows${NC}"
        echo -e "Run: start-services.bat"
    fi
fi

# Clean temp videos
echo -e "${YELLOW}Cleaning temporary video files...${NC}"
rm -rf PoseFit_Trainer/AI_PersonTrainer\ backend/temp_videos/* || echo -e "${YELLOW}No temporary videos to clean${NC}"

echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}Update and maintenance completed successfully!${NC}"
echo -e "${GREEN}Backup saved to: $BACKUP_DIR${NC}"
echo -e "${GREEN}======================================================${NC}"
