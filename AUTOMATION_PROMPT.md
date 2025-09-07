# 🤖 RECURSIVE DEVELOPMENT PROMPT - AI Analysis Platform

**Version**: 1.0.0  
**Purpose**: Constant prompt for recursive, autonomous development  
**Usage**: Copy this prompt exactly and send to Claude Code repeatedly

---

## 📋 RECURSIVE DEVELOPMENT PROTOCOL

### STEP 1: CONTEXT ANALYSIS
Read these files to understand current state:
1. **PROJECT_STATE.yaml** - Current development state and metrics
2. **TODO_TRACKER.md** - Prioritized task list with next actions
3. **CLAUDE.md** - Project context and development guidelines
4. **TEST_RESULTS.json** - Latest test execution results
5. **METRICS_DASHBOARD.md** - Progress visualization and KPIs

### STEP 2: TASK IDENTIFICATION
From TODO_TRACKER.md, select the highest priority task that is:
- Status: "pending" or "in_progress" 
- Not blocked by dependencies
- Has clear success criteria

### STEP 3: TEST-DRIVEN IMPLEMENTATION

#### 3A. Pre-Implementation
```bash
# Verify current state
git status
python3 test_working_app_fixed.py  # Baseline test run
cd human_loop_platform && streamlit run app_working.py --server.port 8503 &
```

#### 3B. Write Tests First (TDD)
1. Create/update Playwright test for the feature
2. Include screenshot validation at key checkpoints
3. Set clear pass/fail criteria
4. Test should fail initially (red state)

#### 3C. Implement Feature
1. Write minimal code to make test pass
2. Follow existing patterns from app_working.py
3. Maintain session state consistency
4. Add proper error handling
5. Include progress indicators where applicable

#### 3D. Validate Implementation
```bash
# Run specific test
python3 test_working_app_fixed.py

# Capture screenshots for review
# Screenshots saved to screenshots_working_app/

# Check for regressions
# Compare against baseline screenshots

# Verify performance targets:
# - API response time <5s
# - Page load time <2s
# - Visual regression <5%
```

### STEP 4: UPDATE TRACKING SYSTEMS

#### 4A. Update Project State
```yaml
# In PROJECT_STATE.yaml, update:
current_state:
  [component]:
    status: "completed"  # or current status
    last_updated: "[current_timestamp]"
    issues: []  # remove resolved issues
    
test_results:
  last_run: "[current_date]"
  overall_coverage: [new_percentage]
  
issues:
  # Remove completed issues
  # Add any new issues discovered
```

#### 4B. Update Task Tracker
```markdown
# In TODO_TRACKER.md:
- [x] ~~Completed task description~~ ✅ DONE [timestamp]
- [ ] Next task (auto-promoted to top priority)
```

#### 4C. Update Test Results
```json
{
  "last_execution": "[timestamp]",
  "results": {
    "[test_name]": {
      "status": "pass|fail",
      "duration": "[seconds]",
      "screenshot": "[path]",
      "issues": []
    }
  }
}
```

#### 4D. Update Metrics Dashboard
Update success metrics, visual regression rates, performance benchmarks.

### STEP 5: VALIDATION CHECKLIST

Before marking task complete, verify:
- [ ] All tests passing (no regressions)
- [ ] Screenshots captured and reviewed
- [ ] Performance targets met
- [ ] Visual regression <5%
- [ ] Documentation updated inline
- [ ] Error handling implemented
- [ ] Session state maintained

### STEP 6: COMMIT & DOCUMENT

#### 6A. Git Commit
```bash
git add .
git commit -m "feat: [brief description of what was implemented]

- [Specific changes made]
- [Test coverage added]
- [Performance improvements]
- [Issues resolved]

🤖 Generated with Claude Code
Screenshots: screenshots_working_app/[timestamp]/

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### 6B. Update CLAUDE.md
Add any new patterns, learnings, or solutions discovered during implementation.

### STEP 7: NEXT ITERATION PREP

#### 7A. Priority Assessment
```markdown
## Current Status Summary
- Completed: [task description]
- Duration: [time taken]
- Issues Found: [any new issues]
- Next Priority: [next task from TODO_TRACKER.md]
- Estimated Effort: [complexity assessment]
```

#### 7B. Ready State Check
Verify system is ready for next iteration:
- [ ] All tracking files updated
- [ ] Tests passing
- [ ] Application running
- [ ] No critical blockers
- [ ] Clear next task identified

---

## 🎯 SUCCESS CRITERIA

Each iteration must achieve:
- **Functionality**: Feature works as specified
- **Quality**: Tests pass, no regressions
- **Performance**: <5s API, <2s page load
- **Visual**: Screenshot validation, <5% regression
- **Documentation**: All tracking files updated

## 🚨 FAILURE HANDLING

If tests fail or issues encountered:
1. **Debug**: Use browser dev tools, error logs
2. **Fix**: Address root cause, not symptoms
3. **Test**: Verify fix doesn't break other features
4. **Document**: Update issue tracking
5. **Retry**: Re-run full validation

If blocked by external dependencies:
1. **Document**: Add to PROJECT_STATE.yaml issues
2. **Pivot**: Select alternative task from TODO_TRACKER.md
3. **Escalate**: Note blocker in METRICS_DASHBOARD.md

## 📊 CONTINUOUS MONITORING

Track these metrics each iteration:
- Test coverage percentage
- Performance benchmarks
- Visual regression rate
- Development velocity
- Issue resolution time

## 🔄 ITERATION COMPLETION

### End Each Session With:
```markdown
## SESSION COMPLETE ✅

**Task Completed**: [description]
**Duration**: [time]
**Tests**: [pass/fail count]
**Screenshots**: [locations]
**Issues Resolved**: [count]
**Issues Created**: [count]
**Next Priority**: [task from TODO_TRACKER.md]

**Files Updated**:
- PROJECT_STATE.yaml ✅
- TODO_TRACKER.md ✅
- TEST_RESULTS.json ✅
- METRICS_DASHBOARD.md ✅
- CLAUDE.md ✅

**Ready for Next Iteration**: YES

---

**COPY THIS PROMPT AGAIN AND SEND TO CONTINUE DEVELOPMENT**
```

---

## 📝 USAGE INSTRUCTIONS

1. **First Time**: Run setup commands, verify all files exist
2. **Every Session**: Copy this entire prompt and send to Claude Code
3. **Between Sessions**: No manual intervention needed
4. **Monitoring**: Check METRICS_DASHBOARD.md for progress
5. **Debugging**: Review TEST_RESULTS.json for failures

## 🎮 QUICK START COMMANDS

```bash
# Start development session
cd /root/repo
git status
python3 test_working_app_fixed.py

# Start app (background)
cd human_loop_platform && streamlit run app_working.py --server.port 8503 &

# Monitor logs
tail -f streamlit.log

# Check test results
cat TEST_RESULTS.json | jq '.'

# View metrics
cat METRICS_DASHBOARD.md
```

---

**⚡ IMPORTANT**: This prompt is designed for Claude Code's recursive execution. Each run builds on the previous, creating continuous development progress toward a production-ready AI Analysis Platform with Human-in-the-Loop capabilities.

**🎯 TARGET**: Professional-grade application with >90% test coverage, <2s page loads, comprehensive HITL features, and full production deployment.

**🚀 CONTINUE**: Copy this prompt and send it again to continue development!