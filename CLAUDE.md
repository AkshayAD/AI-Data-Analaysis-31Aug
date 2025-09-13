# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Commands

### Running Services
```bash
# Main Streamlit application (port 8503)
cd human_loop_platform && streamlit run app_working.py --server.port 8503

# LangGraph orchestrator for HITL features (port 8000)
python3 orchestrator.py --port 8000

# Both services together
streamlit run human_loop_platform/app_working.py --server.port 8503 &
python3 orchestrator.py --port 8000 &
```

### Testing
```bash
# Run specific test suites
python3 test_working_app_fixed.py        # Main app functionality (100% pass)
python3 test_hitl_workflow.py            # HITL approval workflow (100% pass)
python3 test_orchestrator_integration.py # Orchestrator integration (83% pass)
python3 test_caching_simple.py           # Caching validation (100% pass)

# Run single test function
python3 -m pytest test_hitl_workflow.py::test_low_confidence_escalation -v -s

# Full test harness with reporting
python3 test_harness.py

# Playwright UI tests with screenshots
python3 test_working_app_fixed.py  # Screenshots saved to screenshots_working_app/
```

### System Management
```bash
# Health check and recovery
python3 health_check.py          # Full system health check
python3 health_check.py --quick  # Quick check (critical systems only)
bash recovery_mode.sh            # Emergency recovery (restarts services, clears cache)
bash recovery_mode.sh --setup    # Initial environment setup

# View system state
cat SYSTEM_STATE.yaml | grep -A5 "current_execution"
cat TEST_MATRIX.json | jq '.summary'
grep "errors_encountered" SYSTEM_STATE.yaml
```

### Development Workflow
```bash
# Code formatting
black human_loop_platform/app_working.py --line-length 88

# Install dependencies
pip install --break-system-packages -r human_loop_platform/requirements.txt

# Environment setup
cp .env.example .env  # Then add your GEMINI_API_KEY
```

## Architecture Overview

### Service Architecture
```
┌─────────────────────────────────────────────────────┐
│  Streamlit App (app_working.py)                      │
│  Port: 8503                                          │
│  - 3-stage workflow (Input → Plan → Analysis)        │
│  - Session state management                          │
│  - Gemini API integration                            │
└────────────────┬────────────────────────────────────┘
                 │ HTTP/WebSocket
┌────────────────▼────────────────────────────────────┐
│  LangGraph Orchestrator (orchestrator.py)            │
│  Port: 8000                                          │
│  - HITL approval workflow                            │
│  - Task state management                             │
│  - Risk-based escalation                             │
└─────────────────────────────────────────────────────┘
```

### Key Files and Their Roles

**Application Core:**
- `human_loop_platform/app_working.py` - Main Streamlit application with 3-stage workflow
- `orchestrator.py` - LangGraph workflow engine for HITL features
- `human_loop_platform/orchestrator_bridge.py` - Communication layer between Streamlit and orchestrator
- `human_loop_platform/backend/ai_teammates/manager_v2.py` - Gemini API integration layer

**Recursive Development System:**
- `RECURSIVE_ENGINE.md` - Autonomous development instructions with self-healing
- `SYSTEM_STATE.yaml` - Unified state tracking (replaces multiple tracking files)
- `ERROR_PATTERNS.yaml` - Error database with 25+ automated solutions
- `TASK_PIPELINE.md` - Task prioritization and dependency management
- `TEST_MATRIX.json` - Test execution tracking and failure analysis

**Testing Infrastructure:**
- `test_working_app_fixed.py` - Main application E2E tests with Playwright
- `test_hitl_workflow.py` - HITL approval workflow tests (100% pass)
- `test_orchestrator_integration.py` - Integration tests for orchestrator
- `test_harness.py` - Automated test runner with reporting

## Critical Implementation Details

### Session State Keys
The Streamlit app relies on these session state variables:
```python
st.session_state.current_stage     # 0, 1, or 2 - controls navigation
st.session_state.uploaded_data     # User's DataFrame
st.session_state.api_key          # Gemini API key
st.session_state.api_status       # 'connected', 'failed', or None
st.session_state.generated_plan   # AI-generated analysis plan
st.session_state.chat_history     # Conversation history
st.session_state.pending_approvals # HITL tasks awaiting approval
```

### Error Handling Pattern
```python
from app_working import retry_api_call, categorize_error

# All API calls should use retry logic
response = retry_api_call(api_function, max_retries=3, delay=1.0)

# Errors are categorized for appropriate handling
error_type = categorize_error(str(e))  # Returns: auth/rate_limit/network/policy/unknown
```

### Environment Variables
Priority order for API key loading:
1. `GEMINI_API_KEY`
2. `GOOGLE_API_KEY` 
3. `AI_API_KEY`
4. User input fallback

### HITL Workflow Timing
The Human-in-the-Loop workflow requires specific timing considerations:
- Tasks transition from "pending" to "awaiting_human_review" in 1-3 seconds
- Always wait for proper status before attempting approval/rejection
- WebSocket updates broadcast in real-time during status transitions
- Approval/rejection endpoints require tasks to be in "awaiting_human_review" status

### WebSocket Implementation
Real-time updates are handled via WebSocket connections:
- **Endpoint**: `ws://localhost:8000/ws/{client_id}`
- **Manager**: `ConnectionManager` class in `orchestrator.py`
- **Bridge**: `orchestrator_bridge.py` handles Streamlit integration
- **Updates**: Task status changes, approval notifications, workflow progress
- **Connection**: Auto-reconnects with exponential backoff

### UI Component Visibility
Streamlit UI components are conditionally rendered:
- **Tabs**: Only appear after data upload (Stage 2)
- **Pending Approvals**: Requires `ORCHESTRATOR_AVAILABLE` and `orchestrator_connected`
- **API Status**: Shows in sidebar when orchestrator is available
- **Testing**: UI tests should verify API endpoints rather than visual elements

### LangGraph Workflow Architecture
The orchestrator uses LangGraph for HITL workflow management:
- **Nodes**: `data_validation`, `ai_analysis`, `human_review`, `finalization`
- **Flow**: `data_validation` → `ai_analysis` → `human_review` (conditional) → `finalization`
- **State**: Maintained in `WorkflowState` with confidence scoring
- **Checkpointer**: Memory-based for development, can use Redis for production
- **Conditional Logic**: Routes to human review when `requires_human_review=True` or confidence <0.7

### Test Execution Patterns

**Parallel Test Groups:**
- Group 1: `test_working_app_fixed.py`, `test_api_connection_status.py` (can run parallel)
- Group 2: `test_orchestrator_integration.py`, `test_hitl_workflow.py` (require orchestrator)
- Group 3: Error handling tests (can run parallel)

**Service Dependencies:**
- Streamlit must be running for: `test_working_app_fixed.py`, `test_hitl_workflow.py`
- Orchestrator must be running for: `test_orchestrator_integration.py`, `test_hitl_workflow.py`

### Performance Targets
- API response time: <5s (currently 7.2s)
- Page load time: <2s (currently 1.8s ✓)
- Test pass rate: >90% (currently 95%+ ✓)
- Cache hit rate: >80% (currently 65%)
- HITL workflow response: 1-3s (optimal timing ✓)

## Recursive Development Mode

To activate autonomous development:
1. Run `python3 health_check.py` to verify system health
2. Copy entire content of `RECURSIVE_ENGINE.md`
3. Send to Claude Code in new session
4. System will self-heal errors and complete tasks autonomously

The system guarantees:
- Minimum 1 task/hour progress
- 95%+ automatic error recovery
- Pattern learning from failures
- Rollback protection with git stash
- 100% HITL test coverage