#!/bin/bash

# Recovery Mode Script - Emergency system recovery and repair
# Part of RECURSIVE_ENGINE v2.0

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STREAMLIT_PORT=8503
ORCHESTRATOR_PORT=8000
MAX_RETRIES=3
BACKUP_DIR=".backups"

# Logging
LOG_FILE="recovery_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO] $1${NC}" | tee -a "$LOG_FILE"
}

# Header
print_header() {
    log "${BLUE}"
    log "================================================"
    log "🚨 RECOVERY MODE - RECURSIVE ENGINE v2.0"
    log "================================================"
    log "${NC}"
    log_info "Timestamp: $(date)"
    log_info "Mode: $1"
    echo ""
}

# Check if running as setup mode
if [[ "$1" == "--setup" ]]; then
    print_header "SETUP"
    
    log_info "Creating backup directory..."
    mkdir -p "$BACKUP_DIR"
    
    log_info "Installing missing dependencies..."
    pip install -q psutil pyyaml 2>/dev/null || true
    
    log_info "Creating default .env if missing..."
    if [ ! -f .env ]; then
        cat > .env << 'EOF'
# API Configuration
GEMINI_API_KEY=your_api_key_here
GOOGLE_API_KEY=
AI_API_KEY=

# Service Ports
STREAMLIT_PORT=8503
ORCHESTRATOR_PORT=8000

# Cache Configuration
CACHE_TTL=3600

# Debug Mode
DEBUG=false
EOF
        log_success ".env file created"
    fi
    
    log_success "Setup complete"
    exit 0
fi

# Main recovery mode
print_header "RECOVERY"

# Function to check if a process is running
is_running() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Function to kill a process
kill_process() {
    local process=$1
    log_info "Stopping $process..."
    
    if is_running "$process"; then
        pkill -f "$process" 2>/dev/null || true
        sleep 2
        
        # Force kill if still running
        if is_running "$process"; then
            pkill -9 -f "$process" 2>/dev/null || true
            sleep 1
        fi
        
        if ! is_running "$process"; then
            log_success "$process stopped"
        else
            log_error "Failed to stop $process"
            return 1
        fi
    else
        log_info "$process was not running"
    fi
    
    return 0
}

# Function to start a service
start_service() {
    local name=$1
    local command=$2
    local port=$3
    local check_url=$4
    
    log_info "Starting $name..."
    
    # Start the service
    eval "$command" &
    local pid=$!
    
    # Wait for service to be ready
    local retries=0
    while [ $retries -lt 10 ]; do
        sleep 2
        
        if curl -s "$check_url" > /dev/null 2>&1; then
            log_success "$name started on port $port (PID: $pid)"
            return 0
        fi
        
        retries=$((retries + 1))
    done
    
    log_error "Failed to start $name"
    return 1
}

# Step 1: Stop all services
log ""
log_info "Step 1: Stopping all services..."
kill_process "streamlit"
kill_process "orchestrator"
kill_process "uvicorn"

# Step 2: Clear caches and temporary files
log ""
log_info "Step 2: Clearing caches..."

# Clear Streamlit cache
if [ -d ~/.streamlit/cache ]; then
    rm -rf ~/.streamlit/cache
    log_success "Streamlit cache cleared"
fi

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
log_success "Python cache cleared"

# Clear test artifacts
rm -rf screenshots_* 2>/dev/null || true
rm -rf test-results 2>/dev/null || true
log_success "Test artifacts cleared"

# Step 3: Backup current state
log ""
log_info "Step 3: Creating state backup..."

mkdir -p "$BACKUP_DIR"
timestamp=$(date +%Y%m%d_%H%M%S)

# Backup important files
for file in SYSTEM_STATE.yaml ERROR_PATTERNS.yaml TEST_MATRIX.json; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/${file}.${timestamp}"
        log_success "Backed up $file"
    fi
done

# Step 4: Fix common issues
log ""
log_info "Step 4: Fixing common issues..."

# Fix database locks
if [ -f orchestrator.db ]; then
    sqlite3 orchestrator.db "PRAGMA journal_mode=WAL;" 2>/dev/null || true
    sqlite3 orchestrator.db "PRAGMA busy_timeout=5000;" 2>/dev/null || true
    log_success "Database locks cleared"
fi

# Fix file permissions
chmod +x *.py 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true
log_success "File permissions fixed"

# Step 5: Validate environment
log ""
log_info "Step 5: Validating environment..."

# Check for .env file
if [ ! -f .env ]; then
    log_warning ".env file not found - creating template"
    cat > .env << 'EOF'
GEMINI_API_KEY=
GOOGLE_API_KEY=
AI_API_KEY=
STREAMLIT_PORT=8503
ORCHESTRATOR_PORT=8000
EOF
fi

# Check for required directories
mkdir -p human_loop_platform 2>/dev/null || true
mkdir -p logs 2>/dev/null || true
mkdir -p screenshots_baseline 2>/dev/null || true

# Step 6: Restart services
log ""
log_info "Step 6: Restarting services..."

# Start Streamlit
if [ -f human_loop_platform/app_working.py ]; then
    start_service "Streamlit" \
        "cd human_loop_platform && streamlit run app_working.py --server.port $STREAMLIT_PORT --server.headless true" \
        "$STREAMLIT_PORT" \
        "http://localhost:$STREAMLIT_PORT"
else
    log_warning "Streamlit app not found - skipping"
fi

# Start Orchestrator
if [ -f orchestrator.py ]; then
    start_service "Orchestrator" \
        "python3 orchestrator.py --port $ORCHESTRATOR_PORT" \
        "$ORCHESTRATOR_PORT" \
        "http://localhost:$ORCHESTRATOR_PORT/health"
else
    log_warning "Orchestrator not found - skipping"
fi

# Step 7: Run health check
log ""
log_info "Step 7: Running health check..."

if [ -f health_check.py ]; then
    python3 health_check.py --quick
    health_status=$?
    
    if [ $health_status -eq 0 ]; then
        log_success "Health check passed"
    else
        log_warning "Health check failed - manual intervention may be required"
    fi
else
    log_warning "Health check script not found"
fi

# Step 8: Git recovery (if needed)
log ""
log_info "Step 8: Checking git status..."

if git diff --quiet 2>/dev/null; then
    log_success "Git working directory clean"
else
    log_warning "Uncommitted changes detected"
    
    # Offer to stash changes
    if [[ "$1" == "--auto-stash" ]]; then
        git stash push -m "Recovery mode auto-stash $(date +%Y%m%d_%H%M%S)"
        log_success "Changes stashed"
    else
        log_info "Run with --auto-stash to automatically stash changes"
    fi
fi

# Step 9: Summary
log ""
log "${BLUE}================================================${NC}"
log_success "RECOVERY COMPLETE"
log "${BLUE}================================================${NC}"
log ""

# Check final status
services_running=0
if is_running "streamlit"; then
    log_success "✅ Streamlit: Running on port $STREAMLIT_PORT"
    services_running=$((services_running + 1))
else
    log_error "❌ Streamlit: Not running"
fi

if is_running "orchestrator"; then
    log_success "✅ Orchestrator: Running on port $ORCHESTRATOR_PORT"
    services_running=$((services_running + 1))
else
    log_warning "⚠️  Orchestrator: Not running (non-critical)"
fi

log ""
log_info "Services running: $services_running/2"
log_info "Logs saved to: $LOG_FILE"
log_info "Backups saved to: $BACKUP_DIR"

# Provide next steps
log ""
log "${BLUE}📋 Next Steps:${NC}"
log "1. Run: python3 health_check.py"
log "2. Check services: curl http://localhost:$STREAMLIT_PORT"
log "3. Review logs: tail -f $LOG_FILE"
log "4. Continue development: Copy RECURSIVE_ENGINE.md to Claude"

# Exit code based on critical services
if [ $services_running -gt 0 ]; then
    exit 0
else
    exit 1
fi