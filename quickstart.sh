#!/bin/bash

# Quick Start Script for HITL AI Platform
# This script sets up and verifies the development environment

set -e  # Exit on error

echo "======================================"
echo "🚀 HITL AI Platform Quick Start"
echo "======================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Step 1: Check Python version
echo "1. Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    print_status "Python $python_version is installed (>= $required_version required)"
else
    print_error "Python $python_version is too old. Please install Python >= $required_version"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
echo "2. Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Step 3: Install dependencies
echo ""
echo "3. Installing dependencies..."
echo "   This may take a few minutes..."

# Core dependencies
pip install --quiet --upgrade pip
pip install --quiet streamlit pandas numpy plotly google-generativeai

# LangGraph and orchestration
pip install --quiet langgraph langchain fastapi uvicorn websockets

# Testing tools
pip install --quiet playwright pytest pytest-asyncio

# Install Playwright browsers
echo "   Installing Playwright browsers..."
playwright install chromium --quiet

print_status "Dependencies installed"

# Step 4: Create necessary directories
echo ""
echo "4. Creating project directories..."
mkdir -p screenshots/orchestrator/{baseline,current,diff}
mkdir -p test_data
mkdir -p logs
mkdir -p data/sample
print_status "Directories created"

# Step 5: Start the orchestrator
echo ""
echo "5. Starting LangGraph Orchestrator..."
echo "   Running on http://localhost:8000"

# Start orchestrator in background
python orchestrator.py --port 8000 > logs/orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!
sleep 5  # Wait for startup

# Check if orchestrator is running
if curl -s http://localhost:8000/ > /dev/null; then
    print_status "Orchestrator is running (PID: $ORCHESTRATOR_PID)"
else
    print_error "Orchestrator failed to start. Check logs/orchestrator.log"
    exit 1
fi

# Step 6: Run tests
echo ""
echo "6. Running verification tests..."
python test_orchestrator.py > logs/test_results.log 2>&1

if [ $? -eq 0 ]; then
    print_status "All tests passed!"
else
    print_warning "Some tests failed. Check logs/test_results.log"
fi

# Step 7: Start the Streamlit app
echo ""
echo "7. Starting Streamlit application..."
echo "   Running on http://localhost:8503"

cd human_loop_platform
streamlit run app_working.py --server.port 8503 > ../logs/streamlit.log 2>&1 &
STREAMLIT_PID=$!
cd ..
sleep 5

print_status "Streamlit is running (PID: $STREAMLIT_PID)"

# Step 8: Display summary
echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "🌐 Services Running:"
echo "   - LangGraph Orchestrator: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Streamlit App: http://localhost:8503"
echo ""
echo "📁 Important Files:"
echo "   - Development Plan: HITL_DEVELOPMENT_PLAN.md"
echo "   - Claude Guide: CLAUDE.md"
echo "   - Prompt Templates: PROMPT_ENGINEERING_GUIDE.md"
echo "   - Deliverables: DELIVERABLES_SUMMARY.md"
echo ""
echo "📊 Logs:"
echo "   - Orchestrator: logs/orchestrator.log"
echo "   - Tests: logs/test_results.log"
echo "   - Streamlit: logs/streamlit.log"
echo ""
echo "🔧 Next Steps:"
echo "   1. Open http://localhost:8503 in your browser"
echo "   2. Upload test data and configure Gemini API"
echo "   3. Submit tasks via http://localhost:8000/docs"
echo "   4. Review screenshots in screenshots/orchestrator/"
echo ""
echo "💡 Tips:"
echo "   - Stop orchestrator: kill $ORCHESTRATOR_PID"
echo "   - Stop Streamlit: kill $STREAMLIT_PID"
echo "   - View logs: tail -f logs/*.log"
echo "   - Run specific test: python test_orchestrator.py::TestOrchestratorUnit"
echo ""
echo "📚 For detailed instructions, see HITL_DEVELOPMENT_PLAN.md"
echo ""

# Save PIDs for cleanup
echo "ORCHESTRATOR_PID=$ORCHESTRATOR_PID" > .pids
echo "STREAMLIT_PID=$STREAMLIT_PID" >> .pids

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash
if [ -f .pids ]; then
    source .pids
    echo "Stopping services..."
    kill $ORCHESTRATOR_PID 2>/dev/null && echo "✓ Orchestrator stopped"
    kill $STREAMLIT_PID 2>/dev/null && echo "✓ Streamlit stopped"
    rm .pids
    echo "All services stopped"
else
    echo "No services running (no .pids file found)"
fi
EOF

chmod +x stop.sh
print_status "Created stop.sh script to stop all services"

echo ""
echo "======================================"
echo "🎉 Ready to develop!"
echo "======================================"