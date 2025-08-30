#!/bin/bash

# End-to-End Test Runner Script

echo "🧪 AI Data Analysis Platform - E2E Test Suite"
echo "============================================="

# Check if Streamlit is running
if ! pgrep -f streamlit > /dev/null; then
    echo "⚠️  Streamlit not running. Starting application..."
    streamlit run streamlit_app_v3.py --server.headless true --server.port 8501 &
    STREAMLIT_PID=$!
    echo "Waiting for Streamlit to start..."
    sleep 5
else
    echo "✅ Streamlit is already running"
    STREAMLIT_PID=""
fi

# Install Playwright browsers if needed
echo "📦 Setting up Playwright browsers..."
playwright install chromium firefox webkit 2>/dev/null || true

# Run tests
echo "🚀 Running E2E tests..."
echo ""

# Run with different options based on environment
if [ "$1" == "--headed" ]; then
    echo "Running in headed mode (visible browser)..."
    pytest tests/e2e/test_user_journeys.py \
        --headed \
        --slowmo 500 \
        --browser chromium \
        -v
elif [ "$1" == "--debug" ]; then
    echo "Running in debug mode..."
    PWDEBUG=1 pytest tests/e2e/test_user_journeys.py \
        --headed \
        --browser chromium \
        -v -s
else
    echo "Running in headless mode..."
    pytest tests/e2e/test_user_journeys.py \
        --browser chromium \
        --browser firefox \
        --browser webkit \
        -v \
        --html=test-report.html \
        --self-contained-html
fi

TEST_RESULT=$?

# Cleanup
if [ ! -z "$STREAMLIT_PID" ]; then
    echo ""
    echo "🛑 Stopping Streamlit..."
    kill $STREAMLIT_PID 2>/dev/null
fi

# Report results
echo ""
echo "============================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All tests passed successfully!"
else
    echo "❌ Some tests failed. Check the report for details."
fi
echo "============================================="

# Open report if tests were run in headless mode and failed
if [ $TEST_RESULT -ne 0 ] && [ "$1" != "--headed" ] && [ "$1" != "--debug" ]; then
    if [ -f "test-report.html" ]; then
        echo "📊 Test report saved to: test-report.html"
    fi
fi

exit $TEST_RESULT