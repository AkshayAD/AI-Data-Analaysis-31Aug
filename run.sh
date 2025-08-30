#!/bin/bash
# Simple runner script for AI Data Analysis Team

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}AI Data Analysis Team - Phase 1${NC}"
echo "================================="
echo ""

case "$1" in
    test)
        echo -e "${YELLOW}Running tests...${NC}"
        python3 -m pytest tests/ -v
        ;;
    
    quickstart)
        echo -e "${YELLOW}Running quickstart example...${NC}"
        python3 examples/quickstart.py
        ;;
    
    analyze)
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: ./run.sh analyze <data_file>${NC}"
            exit 1
        fi
        echo -e "${YELLOW}Analyzing $2...${NC}"
        python3 src/python/cli.py analyze "$2"
        ;;
    
    notebook)
        if [ -z "$2" ]; then
            echo -e "${RED}Usage: ./run.sh notebook <notebook_name>${NC}"
            exit 1
        fi
        echo -e "${YELLOW}Running notebook $2...${NC}"
        marimo run "marimo_notebooks/$2.py"
        ;;
    
    cli)
        shift
        python3 src/python/cli.py "$@"
        ;;
    
    *)
        echo "Usage: ./run.sh {test|quickstart|analyze|notebook|cli}"
        echo ""
        echo "Commands:"
        echo "  test        - Run all tests"
        echo "  quickstart  - Run quickstart example"
        echo "  analyze     - Analyze a data file"
        echo "  notebook    - Run a Marimo notebook"
        echo "  cli         - Access full CLI"
        echo ""
        echo "Examples:"
        echo "  ./run.sh test"
        echo "  ./run.sh quickstart"
        echo "  ./run.sh analyze data/sample/sales_data.csv"
        echo "  ./run.sh notebook sales_analysis"
        echo "  ./run.sh cli --help"
        ;;
esac