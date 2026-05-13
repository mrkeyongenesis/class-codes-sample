#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║   🚀 CI/CD Pipeline with Jenkins & GitHub - Quick Start   ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Docker
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found${NC}"

echo ""
echo -e "${YELLOW}📁 Project structure check...${NC}"

# Check required files
required_files=("app.py" "Dockerfile" "docker-compose.yml" "requirements.txt" "test_app.py" "Jenkinsfile")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        exit 1
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📦 Starting services...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Build and start
echo ""
echo -e "${YELLOW}Building Docker images (this may take 2-3 minutes)...${NC}"
docker-compose up --build -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start services${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Services starting...${NC}"

# Wait for services
echo ""
echo -e "${YELLOW}⏳ Waiting for services to be ready (30 seconds)...${NC}"

for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""

# Check services health
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🏥 Health checks...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Flask app
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Flask App - Running${NC}"
else
    echo -e "${YELLOW}⏳ Flask App - Starting${NC}"
fi

# PostgreSQL
if docker-compose exec db pg_isready -U appuser > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL - Ready${NC}"
else
    echo -e "${YELLOW}⏳ PostgreSQL - Starting${NC}"
fi

# Jenkins
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Jenkins - Running${NC}"
else
    echo -e "${YELLOW}⏳ Jenkins - Starting (may take 1-2 minutes)${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo ""
echo -e "${BLUE}📌 Access Points:${NC}"
echo -e "  🌐 Flask App:    ${GREEN}http://localhost:5000${NC}"
echo -e "  🔧 Jenkins:      ${GREEN}http://localhost:8080${NC}"
echo -e "  💾 PostgreSQL:   ${GREEN}localhost:5432${NC}"
echo ""

echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "  1. Open Flask app at http://localhost:5000"
echo -e "  2. Try sending a message"
echo -e "  3. Access Jenkins at http://localhost:8080"
echo -e "  4. Configure GitHub Actions in .github/workflows/"
echo ""

echo -e "${BLUE}📊 Useful Commands:${NC}"
echo -e "  View logs:       ${YELLOW}docker-compose logs -f${NC}"
echo -e "  Run tests:       ${YELLOW}pytest test_app.py -v${NC}"
echo -e "  Stop services:   ${YELLOW}docker-compose down${NC}"
echo -e "  View containers: ${YELLOW}docker-compose ps${NC}"
echo ""

echo -e "${BLUE}📖 Documentation:${NC}"
echo -e "  Setup Guide:     ${YELLOW}cat SETUP_GUIDE.md${NC}"
echo -e "  Flask App:       ${YELLOW}http://localhost:5000${NC}"
echo -e "  Jenkins UI:      ${YELLOW}http://localhost:8080${NC}"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Show initial Jenkins password info
echo ""
echo -e "${YELLOW}🔐 Jenkins Setup (First Time):${NC}"
echo -e "  When Jenkins starts, get initial password with:"
echo -e "  ${YELLOW}docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword${NC}"
echo ""

echo -e "${GREEN}✅ All systems ready! Start building with CI/CD! 🚀${NC}"
echo ""
