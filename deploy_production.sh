#!/bin/bash

# Enterprise AI Data Analysis Platform - Production Deployment Script
# Usage: ./deploy_production.sh [streamlit|docker|local]

set -e

echo "🚀 Enterprise AI Data Analysis Platform - Production Deployment"
echo "==============================================================="

# Check for deployment type
DEPLOY_TYPE=${1:-streamlit}

# Function to check dependencies
check_dependencies() {
    echo "📦 Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 is not installed"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null; then
        echo "❌ pip is not installed"
        exit 1
    fi
    
    echo "✅ Dependencies check passed"
}

# Function to install Python packages
install_packages() {
    echo "📦 Installing Python packages..."
    pip install --break-system-packages -r requirements.txt
    echo "✅ Python packages installed"
}

# Function to setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    # Create .streamlit directory if it doesn't exist
    mkdir -p .streamlit
    
    # Check if secrets.toml exists
    if [ ! -f .streamlit/secrets.toml ]; then
        echo "⚠️  Creating secrets.toml template..."
        cat > .streamlit/secrets.toml << EOF
# Streamlit Secrets Configuration
# IMPORTANT: Replace with your actual Gemini API key for production

GEMINI_API_KEY = "YOUR_ACTUAL_GEMINI_API_KEY_HERE"
EOF
        echo "⚠️  Please edit .streamlit/secrets.toml and add your GEMINI_API_KEY"
    fi
    
    echo "✅ Environment setup complete"
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    
    # Install Playwright browsers if needed
    if command -v playwright &> /dev/null; then
        python3 -m playwright install chromium --with-deps 2>/dev/null || true
    fi
    
    echo "✅ Tests preparation complete"
}

# Function to deploy locally
deploy_local() {
    echo "🏠 Deploying locally..."
    
    check_dependencies
    install_packages
    setup_environment
    
    echo "📊 Starting Streamlit application..."
    python3 -m streamlit run streamlit_app_enterprise.py \
        --server.port 8501 \
        --server.headless true \
        --browser.gatherUsageStats false
}

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Deploying with Docker..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ docker-compose is not installed"
        exit 1
    fi
    
    setup_environment
    
    echo "🏗️ Building Docker containers..."
    docker-compose build
    
    echo "🚀 Starting Docker containers..."
    docker-compose up -d
    
    echo "✅ Docker deployment complete"
    echo "📊 Application available at http://localhost:8501"
}

# Function to prepare for Streamlit Cloud
deploy_streamlit_cloud() {
    echo "☁️ Preparing for Streamlit Cloud deployment..."
    
    check_dependencies
    setup_environment
    
    # Check git status
    if ! command -v git &> /dev/null; then
        echo "❌ Git is not installed"
        exit 1
    fi
    
    echo "📋 Deployment Checklist for Streamlit Cloud:"
    echo "---------------------------------------------"
    echo "1. ✅ Requirements.txt is ready"
    echo "2. ✅ Main app file: streamlit_app_enterprise.py"
    echo "3. ⚠️  Add GEMINI_API_KEY in Streamlit Cloud secrets"
    echo ""
    echo "📝 Next Steps:"
    echo "1. Push your code to GitHub:"
    echo "   git add ."
    echo "   git commit -m 'Deploy to Streamlit Cloud'"
    echo "   git push origin $(git branch --show-current)"
    echo ""
    echo "2. Go to https://share.streamlit.io"
    echo "3. Connect your GitHub repository"
    echo "4. Select branch: $(git branch --show-current)"
    echo "5. Main file: streamlit_app_enterprise.py"
    echo "6. Add secrets in Advanced Settings:"
    echo "   GEMINI_API_KEY = \"your-api-key\""
    echo ""
    echo "✅ Streamlit Cloud preparation complete"
}

# Main execution
case $DEPLOY_TYPE in
    local)
        deploy_local
        ;;
    docker)
        deploy_docker
        ;;
    streamlit)
        deploy_streamlit_cloud
        ;;
    *)
        echo "Usage: $0 [streamlit|docker|local]"
        echo "  streamlit - Prepare for Streamlit Cloud deployment"
        echo "  docker    - Deploy using Docker"
        echo "  local     - Deploy locally with Streamlit"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process complete!"
echo "================================"
echo ""
echo "📧 Demo Accounts:"
echo "  Manager:   manager@company.com / manager123"
echo "  Analyst:   analyst@company.com / analyst123"
echo "  Associate: associate@company.com / associate123"
echo ""
echo "⚠️  Remember to set your GEMINI_API_KEY for AI features!"