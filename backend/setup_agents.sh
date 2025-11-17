#!/bin/bash

# CareAgents AI Setup Script
# This script helps you set up the AI agents system

set -e  # Exit on error

echo "🚀 CareAgents AI Setup"
echo "====================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and add your ANTHROPIC_API_KEY${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check for required environment variables
echo ""
echo "Checking environment variables..."

if grep -q "your-anthropic-api-key" .env 2>/dev/null; then
    echo -e "${RED}✗ ANTHROPIC_API_KEY not set in .env${NC}"
    echo "  Please add your API key to .env file"
    exit 1
else
    echo -e "${GREEN}✓ ANTHROPIC_API_KEY configured${NC}"
fi

# Check PostgreSQL
echo ""
echo "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL client found${NC}"

    # Try to connect
    if psql -h localhost -U postgres -d postgres -c '\q' 2>/dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is running${NC}"

        # Check if database exists
        if psql -h localhost -U postgres -lqt | cut -d \| -f 1 | grep -qw careagents; then
            echo -e "${GREEN}✓ Database 'careagents' exists${NC}"
        else
            echo -e "${YELLOW}Creating database 'careagents'...${NC}"
            createdb -h localhost -U postgres careagents
            echo -e "${GREEN}✓ Database created${NC}"
        fi

        # Run schema
        echo -e "${YELLOW}Setting up database schema...${NC}"
        if [ -f "database/postgresql/scripts/create_tables.sql" ]; then
            psql -h localhost -U postgres -d careagents -f database/postgresql/scripts/create_tables.sql
            echo -e "${GREEN}✓ Database schema created${NC}"
        else
            echo -e "${RED}✗ SQL file not found${NC}"
        fi
    else
        echo -e "${RED}✗ Cannot connect to PostgreSQL${NC}"
        echo "  Please start PostgreSQL: brew services start postgresql"
        exit 1
    fi
else
    echo -e "${RED}✗ PostgreSQL not found${NC}"
    echo "  Install: brew install postgresql"
    exit 1
fi

# Check Redis
echo ""
echo "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✓ Redis client found${NC}"

    # Try to ping Redis
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}Starting Redis...${NC}"
        if command -v brew &> /dev/null; then
            brew services start redis
            sleep 2
            if redis-cli ping &> /dev/null; then
                echo -e "${GREEN}✓ Redis started${NC}"
            else
                echo -e "${RED}✗ Failed to start Redis${NC}"
                exit 1
            fi
        else
            echo -e "${RED}✗ Redis is not running${NC}"
            echo "  Start Redis: redis-server"
            exit 1
        fi
    fi
else
    echo -e "${RED}✗ Redis not found${NC}"
    echo "  Install: brew install redis"
    exit 1
fi

# Check Python and dependencies
echo ""
echo "Checking Python dependencies..."
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✓ uv package manager found${NC}"
    echo -e "${YELLOW}Syncing dependencies...${NC}"
    uv sync
    echo -e "${GREEN}✓ Dependencies installed${NC}"
elif command -v pip &> /dev/null; then
    echo -e "${YELLOW}uv not found, using pip...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ No package manager found${NC}"
    echo "  Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Verify your .env file has correct credentials"
echo "2. Start the server:"
echo "   ${GREEN}python main_agents.py${NC}"
echo ""
echo "3. Test the API:"
echo "   ${GREEN}curl http://localhost:8000/health${NC}"
echo ""
echo "4. Connect via WebSocket:"
echo "   ${GREEN}websocat ws://localhost:8000/ws/chat/test-session${NC}"
echo ""
echo "📚 Documentation:"
echo "   - README: agents/README.md"
echo "   - Quick Start: agents/QUICKSTART.md"
echo "   - Summary: ../AGENTS_IMPLEMENTATION_SUMMARY.md"
echo ""
echo "Happy coding! 🚀"
