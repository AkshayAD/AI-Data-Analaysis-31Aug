# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 Project Overview

This is an AI-powered data analysis platform with human-in-the-loop (HITL) capabilities. The system is being transformed from a basic Streamlit app into a production-ready platform using LangGraph for orchestration, Marimo for reactive notebooks, and Playwright for visual testing.

## 🚀 Quick Start Commands

### Running the Application
```bash
# Current working version (Streamlit)
cd human_loop_platform && streamlit run app_working.py --server.port 8503

# Future Marimo version (in development)
marimo run marimo_app.py --port 2718

# LangGraph orchestrator (in development)
python orchestrator.py --debug --port 8000
```

### Testing
```bash
# Run Playwright visual tests with screenshots
python3 test_working_app.py  # Captures screenshots in screenshots_working_app/

# Run comprehensive test suite
python3 test_complete_functionality.py  # Full UI testing

# Visual regression testing (in development)
playwright test tests/visual/ --headed  # See browser during tests
```

### Dependencies
```bash
# Minimal dependencies (root level)
pip install -r requirements.txt

# Full platform dependencies (includes testing)
pip install -r human_loop_platform/requirements.txt

# Development dependencies (includes Marimo, LangGraph)
pip install -r requirements-dev.txt  # To be created
```

## 🏗️ Architecture Overview

### Current State (Working)
```
human_loop_platform/
├── app_working.py         # ✅ WORKING - Main Streamlit app with Gemini integration
├── app_v2.py             # ⚠️ Has navigation issues
├── app.py                # ⚠️ Original with import problems
└── backend/
    └── ai_teammates/
        └── manager_v2.py  # ✅ WORKING - Real Gemini API integration
```

### Target Architecture (In Development)
```
├── orchestrator.py        # LangGraph orchestration with HITL
├── marimo_app.py         # Marimo reactive notebook (replacing Streamlit)
├── agents/               # Intelligent agents for different tasks
├── workflows/            # Automated workflow definitions
└── tests/
    └── visual/          # Playwright visual regression tests
```

## 🔑 Critical Information

### Gemini API Integration
- **Test API Key**: `AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8` (used in tests)
- **Available Models**: `gemini-pro`, `gemini-1.5-pro`, `gemini-2.5-flash`
- **Rate Limits**: 60 requests/min on free tier
- **Integration Point**: `backend/ai_teammates/manager_v2.py`

### Session State Management
The application uses Streamlit session state for navigation. Critical keys:
- `current_stage`: Controls which stage (0, 1, 2) is displayed
- `uploaded_data`: User's DataFrame
- `api_key`: Gemini API credentials
- `generated_plan`: AI-generated analysis plan
- `chat_history`: Conversation context

### Known Issues & Solutions

#### Issue 1: Streamlit Import Errors
**Problem**: `FileUploader` import fails
**Solution**: Use `from components.FileUploader import MultiFormatFileUploader as FileUploader`

#### Issue 2: Playwright Tests Fail with Streamlit
**Problem**: Dynamic rendering causes selector issues
**Solution**: 
- Use longer timeouts (30000ms)
- Wait for network idle: `await page.goto(url, wait_until='networkidle')`
- Streamlit expanders are pre-expanded by default

#### Issue 3: Navigation Between Stages
**Problem**: Direct navigation fails
**Solution**: Use `st.session_state.current_stage` and `st.rerun()`

## 📋 Development Workflow

### 1. Iterative Development Pattern
```python
# STEP 1: Write test first (TDD)
"Create a test for [feature] that:
- Captures screenshots at key points
- Validates expected behavior
- Checks visual regression"

# STEP 2: Implement feature
"Implement [feature] to pass the test:
- Use existing patterns from app_working.py
- Maintain session state consistency
- Include error handling"

# STEP 3: Validate with screenshots
"Run test and verify:
- Screenshots match expectations
- No visual regression >5%
- Performance <2s response time"
```

### 2. Adding New Features

#### For Streamlit Components
```python
# Always initialize session state
if 'new_feature' not in st.session_state:
    st.session_state.new_feature = default_value

# Use callbacks for navigation
def navigate_to_stage(stage_num):
    st.session_state.current_stage = stage_num
    st.rerun()

# Handle file uploads properly
uploaded_file = st.file_uploader("Choose file", type=['csv', 'xlsx'])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    st.session_state.uploaded_data = df
```

#### For AI Integration
```python
# Always wrap API calls in try-except
try:
    genai.configure(api_key=st.session_state.api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
except Exception as e:
    st.error(f"AI Error: {str(e)}")
    # Provide fallback response
```

### 3. Testing Strategy

#### Visual Testing Pattern
```python
# Capture baseline
await page.screenshot(path="baseline/feature.png")

# Make changes
await page.click("button")
await page.wait_for_timeout(2000)

# Capture current state
await page.screenshot(path="current/feature.png")

# Compare (allow 5% difference)
# Use external tool or Playwright's built-in comparison
```

#### Data Testing Pattern
```python
# Create consistent test data
def create_test_data():
    np.random.seed(42)  # Always use seed for consistency
    return pd.DataFrame({
        'column1': np.random.randn(100),
        'column2': np.random.choice(['A', 'B', 'C'], 100)
    })
```

## 🚨 Human-in-the-Loop Implementation

### Current HITL Features (Basic)
- Manual API key entry
- Business objective input
- Plan editing capability
- Manual export triggers

### Target HITL Features (Advanced)
```python
# Risk-based escalation
if confidence_score < 0.7:
    await request_human_review(task_id, context)

# Parallel feedback
feedback_task = asyncio.create_task(collect_human_feedback())
continue_execution()  # Don't block

# Continuous learning
log_human_correction(original, corrected, context)
trigger_model_update()
```

### Approval Workflow Pattern
```python
# Using LangGraph (future implementation)
from langgraph import StateGraph, State

class ApprovalState(State):
    needs_approval: bool
    confidence: float
    human_decision: Optional[str]

workflow = StateGraph(ApprovalState)
workflow.add_node("ai_analysis", ai_analysis_node)
workflow.add_node("human_review", human_review_node)
workflow.add_conditional_edges(
    "ai_analysis",
    lambda x: x.needs_approval,
    {True: "human_review", False: "complete"}
)
```

## 🔧 Common Development Tasks

### Adding a New Analysis Stage
1. Create new page file: `frontend/pages/0X_StageName.py`
2. Add navigation in `app_working.py`
3. Update session state management
4. Add tests with screenshots
5. Update this CLAUDE.md

### Updating AI Prompts
1. Edit prompts in `backend/ai_teammates/manager_v2.py`
2. Test with different inputs
3. Capture output screenshots
4. Validate quality metrics

### Implementing Visual Tests
1. Create baseline: `playwright test --update-snapshots`
2. Add test in `tests/visual/`
3. Run regression: `playwright test tests/visual/`
4. Review diffs in `test-results/`

## 📊 Performance Optimization

### Current Bottlenecks
- Gemini API calls: ~3-5 seconds
- File upload processing: ~1-2 seconds for large files
- Visualization rendering: ~1 second

### Optimization Strategies
```python
# Cache API responses
@st.cache_data(ttl=3600)
def get_ai_response(prompt_hash):
    return model.generate_content(prompt)

# Lazy load visualizations
if st.checkbox("Show visualizations"):
    render_charts()

# Batch API calls
responses = await asyncio.gather(*[
    model.generate_content(prompt) for prompt in prompts
])
```

## 🐛 Debugging Guide

### Common Issues

#### 1. "Module not found" Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Add to path if needed
sys.path.append(str(Path(__file__).parent.parent))
```

#### 2. Session State Loss
```python
# Always check initialization
if 'key' not in st.session_state:
    st.session_state.key = default_value

# Use callbacks for state changes
st.button("Click", on_click=callback_function)
```

#### 3. Playwright Test Failures
```bash
# Run with debug output
DEBUG=pw:api playwright test

# Use headed mode to see browser
playwright test --headed

# Increase timeouts
page.set_default_timeout(60000)
```

## 🚀 Migration Path to Production

### Phase 1: Current Streamlit → Enhanced Streamlit
- Add comprehensive error handling ✅
- Implement caching ⏳
- Add performance monitoring ⏳
- Create visual tests ✅

### Phase 2: Streamlit → Marimo
- Convert components to reactive cells
- Implement SQL support
- Add AI-native features
- Maintain feature parity

### Phase 3: Add LangGraph Orchestration
- Implement stateful workflows
- Add approval nodes
- Create agent system
- Enable parallel execution

### Phase 4: Production Deployment
- Set up CI/CD pipeline
- Implement monitoring
- Add security scanning
- Create documentation

## 📝 Code Style Guidelines

### Python Style
- Use Black formatter (line-length=88)
- Type hints for all functions
- Docstrings for public methods
- Error handling with specific exceptions

### Testing Style
- Descriptive test names: `test_should_x_when_y`
- Arrange-Act-Assert pattern
- One assertion per test (when possible)
- Use fixtures for common setup

### Git Commit Style
- Prefix: feat|fix|test|docs|refactor
- Present tense: "Add feature" not "Added feature"
- Reference issue numbers
- Keep under 72 characters

## 🔄 Continuous Improvement

### After Each Development Session
1. Update this CLAUDE.md with learnings
2. Add new patterns discovered
3. Document any workarounds
4. Update test baselines if needed

### Weekly Reviews
1. Analyze test coverage reports
2. Review visual regression results
3. Check performance metrics
4. Update architecture diagrams

### Key Metrics to Track
- Test coverage (target: >80%)
- Visual regression rate (<5%)
- API response time (<5s)
- Page load time (<2s)
- Error rate (<1%)

## 🆘 When Stuck

### Troubleshooting Steps
1. Check this CLAUDE.md first
2. Review test outputs and screenshots
3. Check session state values
4. Review browser console (for Streamlit)
5. Check API response format

### Getting Help
- Review `HITL_DEVELOPMENT_PLAN.md` for detailed implementation guide
- Check `FINAL_TEST_REPORT.md` for known issues
- Look at working examples in `app_working.py`
- Use test files as reference implementations

## 🎯 Priority Focus Areas

### Immediate (This Week)
1. Fix remaining test failures in Playwright suite
2. Implement basic HITL approval flow
3. Add visual regression baselines
4. Create Marimo proof-of-concept

### Short-term (Next 2 Weeks)
1. Complete LangGraph integration
2. Implement parallel feedback system
3. Add comprehensive monitoring
4. Create user documentation

### Long-term (This Month)
1. Full production deployment
2. Advanced agent system
3. Continuous learning pipeline
4. Performance optimization

---

**Remember**: This is a living document. Update it with every significant learning or pattern discovered. The goal is to make future development sessions as productive as possible.