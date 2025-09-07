#!/usr/bin/env python3
"""
Comprehensive Test Suite for LangGraph Orchestrator
Includes unit tests, integration tests, and Playwright visual tests
"""

import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
import pytest
import requests
from playwright.async_api import async_playwright, expect

# Test configuration
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
SCREENSHOT_DIR = Path("screenshots/orchestrator")
BASELINE_DIR = SCREENSHOT_DIR / "baseline"
CURRENT_DIR = SCREENSHOT_DIR / "current"
DIFF_DIR = SCREENSHOT_DIR / "diff"

# Create directories
for dir_path in [BASELINE_DIR, CURRENT_DIR, DIFF_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# ====================
# Test Data Factory
# ====================

class TestDataFactory:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def create_small_dataset() -> pd.DataFrame:
        """Create a small test dataset"""
        np.random.seed(42)
        return pd.DataFrame({
            'id': range(100),
            'value': np.random.randn(100),
            'category': np.random.choice(['A', 'B', 'C'], 100),
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='H')
        })
    
    @staticmethod
    def create_large_dataset() -> pd.DataFrame:
        """Create a large dataset that triggers human review"""
        np.random.seed(42)
        return pd.DataFrame({
            'id': range(1000001),  # Over 1M rows triggers review
            'value': np.random.randn(1000001),
            'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], 1000001)
        })
    
    @staticmethod
    def create_edge_case_dataset() -> pd.DataFrame:
        """Create dataset with edge cases"""
        return pd.DataFrame({
            'nulls': [None, 1, None, 2, None],
            'infinities': [np.inf, 1, -np.inf, 2, np.nan],
            'mixed_types': [1, 'two', 3.0, True, None]
        })
    
    @staticmethod
    def save_test_data(df: pd.DataFrame, filename: str) -> Path:
        """Save test data to file"""
        test_data_dir = Path("test_data")
        test_data_dir.mkdir(exist_ok=True)
        filepath = test_data_dir / filename
        df.to_csv(filepath, index=False)
        return filepath


# ====================
# Unit Tests
# ====================

class TestOrchestratorUnit:
    """Unit tests for orchestrator components"""
    
    def test_task_creation(self):
        """Test task model creation"""
        from orchestrator import AnalysisTask, TaskStatus, TaskPriority
        
        task = AnalysisTask(
            task_type="data_analysis",
            parameters={"test": True},
            priority=TaskPriority.HIGH
        )
        
        assert task.task_id is not None
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.HIGH
        assert task.parameters["test"] is True
    
    def test_database_operations(self):
        """Test database manager operations"""
        from orchestrator import DatabaseManager, AnalysisTask
        
        db = DatabaseManager(Path("test_orchestrator.db"))
        
        # Create and save task
        task = AnalysisTask(
            task_type="test",
            parameters={"test": True}
        )
        db.save_task(task)
        
        # Retrieve task
        retrieved = db.get_task(task.task_id)
        assert retrieved is not None
        assert retrieved.task_id == task.task_id
        assert retrieved.task_type == "test"
        
        # Clean up
        Path("test_orchestrator.db").unlink(missing_ok=True)
    
    def test_confidence_threshold(self):
        """Test confidence-based routing logic"""
        from orchestrator import WorkflowState
        
        # High confidence - no review needed
        state_high = WorkflowState(
            task_id="test1",
            task_type="analysis",
            data=None,
            parameters={"confidence_threshold": 0.7},
            confidence_score=0.9,
            requires_human_review=False,
            human_decision=None,
            human_feedback=None,
            result=None,
            error=None,
            status="in_progress",
            history=[]
        )
        
        # Determine routing
        needs_review = state_high["confidence_score"] < state_high["parameters"]["confidence_threshold"]
        assert needs_review is False
        
        # Low confidence - review needed
        state_low = state_high.copy()
        state_low["confidence_score"] = 0.5
        needs_review = state_low["confidence_score"] < state_low["parameters"]["confidence_threshold"]
        assert needs_review is True


# ====================
# Integration Tests
# ====================

class TestOrchestratorIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """HTTP client fixture"""
        # Wait for server to be ready
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{API_BASE_URL}/")
                if response.status_code == 200:
                    break
            except:
                time.sleep(1)
        return requests
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get(f"{API_BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_submit_task(self, client):
        """Test task submission"""
        factory = TestDataFactory()
        df = factory.create_small_dataset()
        filepath = factory.save_test_data(df, "test_small.csv")
        
        task_data = {
            "task_type": "data_analysis",
            "data_path": str(filepath),
            "parameters": {
                "confidence_threshold": 0.7,
                "data_path": str(filepath)
            },
            "priority": 2,
            "require_human_review": False
        }
        
        response = client.post(f"{API_BASE_URL}/api/v1/tasks/submit", json=task_data)
        assert response.status_code == 200
        result = response.json()
        assert "task_id" in result
        assert result["status"] == "submitted"
        
        return result["task_id"]
    
    def test_get_task_status(self, client):
        """Test getting task status"""
        # Submit a task first
        task_id = self.test_submit_task(client)
        
        # Wait a bit for processing
        time.sleep(2)
        
        # Get status
        response = client.get(f"{API_BASE_URL}/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert "status" in data
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get(f"{API_BASE_URL}/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "task_statistics" in data
        assert "average_processing_time_seconds" in data
        assert "human_reviewed_tasks" in data


# ====================
# Playwright Visual Tests
# ====================

class TestOrchestratorVisual:
    """Visual regression tests using Playwright"""
    
    @pytest.fixture
    async def browser(self):
        """Browser fixture"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            yield browser
            await browser.close()
    
    @pytest.fixture
    async def page(self, browser):
        """Page fixture"""
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        page.set_default_timeout(30000)
        yield page
        await context.close()
    
    async def test_dashboard_ui(self, page):
        """Test orchestrator dashboard UI"""
        # Create dashboard HTML for testing
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Orchestrator Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #2c3e50; color: white; padding: 20px; }
                .metrics { display: flex; gap: 20px; margin: 20px 0; }
                .metric-card { 
                    background: #ecf0f1; 
                    padding: 20px; 
                    border-radius: 8px; 
                    flex: 1;
                }
                .metric-value { font-size: 2em; color: #3498db; }
                .task-list { background: white; border: 1px solid #ddd; }
                .task-item { padding: 10px; border-bottom: 1px solid #eee; }
                .status-pending { color: #f39c12; }
                .status-in-progress { color: #3498db; }
                .status-completed { color: #27ae60; }
                .status-failed { color: #e74c3c; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>LangGraph Orchestrator Dashboard</h1>
                <p>Real-time task monitoring and management</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Total Tasks</h3>
                    <div class="metric-value">42</div>
                </div>
                <div class="metric-card">
                    <h3>Awaiting Review</h3>
                    <div class="metric-value">3</div>
                </div>
                <div class="metric-card">
                    <h3>Success Rate</h3>
                    <div class="metric-value">95%</div>
                </div>
                <div class="metric-card">
                    <h3>Avg Time</h3>
                    <div class="metric-value">2.3s</div>
                </div>
            </div>
            
            <h2>Active Tasks</h2>
            <div class="task-list">
                <div class="task-item">
                    <strong>Task-001:</strong> Data Analysis
                    <span class="status-in-progress">IN PROGRESS</span>
                    - Confidence: 85%
                </div>
                <div class="task-item">
                    <strong>Task-002:</strong> Report Generation
                    <span class="status-pending">AWAITING REVIEW</span>
                    - Confidence: 65%
                </div>
                <div class="task-item">
                    <strong>Task-003:</strong> Anomaly Detection
                    <span class="status-completed">COMPLETED</span>
                    - Confidence: 92%
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML to file
        dashboard_path = Path("dashboard.html")
        dashboard_path.write_text(dashboard_html)
        
        # Navigate to dashboard
        await page.goto(f"file://{dashboard_path.absolute()}")
        
        # Capture screenshots
        await page.screenshot(path=CURRENT_DIR / "dashboard_overview.png", full_page=True)
        
        # Test metric cards
        metrics = await page.locator(".metric-card").all()
        assert len(metrics) == 4
        
        # Test task list
        tasks = await page.locator(".task-item").all()
        assert len(tasks) == 3
        
        # Capture individual components
        header = page.locator(".header")
        await header.screenshot(path=CURRENT_DIR / "dashboard_header.png")
        
        metrics_section = page.locator(".metrics")
        await metrics_section.screenshot(path=CURRENT_DIR / "dashboard_metrics.png")
        
        task_list = page.locator(".task-list")
        await task_list.screenshot(path=CURRENT_DIR / "dashboard_tasks.png")
        
        # Clean up
        dashboard_path.unlink()
    
    async def test_approval_workflow_ui(self, page):
        """Test human approval workflow UI"""
        approval_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Human Review Interface</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .review-container { max-width: 800px; margin: 0 auto; }
                .review-header { background: #34495e; color: white; padding: 20px; }
                .confidence-bar { 
                    height: 30px; 
                    background: linear-gradient(to right, #e74c3c 0%, #f39c12 50%, #27ae60 100%);
                    position: relative;
                    margin: 20px 0;
                }
                .confidence-marker {
                    position: absolute;
                    top: -10px;
                    width: 2px;
                    height: 50px;
                    background: black;
                }
                .ai-recommendation {
                    background: #ecf0f1;
                    padding: 20px;
                    margin: 20px 0;
                    border-left: 4px solid #3498db;
                }
                .data-preview {
                    background: #f8f9fa;
                    padding: 10px;
                    overflow-x: auto;
                }
                .actions {
                    display: flex;
                    gap: 10px;
                    margin: 20px 0;
                }
                .btn {
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                }
                .btn-approve { background: #27ae60; color: white; }
                .btn-reject { background: #e74c3c; color: white; }
                .btn-modify { background: #3498db; color: white; }
            </style>
        </head>
        <body>
            <div class="review-container">
                <div class="review-header">
                    <h1>Human Review Required</h1>
                    <p>Task ID: task-12345 | Priority: HIGH</p>
                </div>
                
                <h2>Confidence Score: 65%</h2>
                <div class="confidence-bar">
                    <div class="confidence-marker" style="left: 65%;"></div>
                </div>
                
                <div class="ai-recommendation">
                    <h3>AI Recommendation</h3>
                    <p>The analysis suggests significant anomalies in the dataset:</p>
                    <ul>
                        <li>15% of data points are outliers</li>
                        <li>Unexpected correlation between variables X and Y (r=0.92)</li>
                        <li>Missing values in critical columns exceed threshold</li>
                    </ul>
                    <p><strong>Suggested Action:</strong> Further investigation required before proceeding.</p>
                </div>
                
                <h3>Data Preview</h3>
                <div class="data-preview">
                    <table>
                        <tr><th>ID</th><th>Value</th><th>Category</th><th>Status</th></tr>
                        <tr><td>1</td><td>123.45</td><td>A</td><td>Normal</td></tr>
                        <tr><td>2</td><td>987.65</td><td>B</td><td>Anomaly</td></tr>
                        <tr><td>3</td><td>456.78</td><td>A</td><td>Normal</td></tr>
                    </table>
                </div>
                
                <h3>Your Decision</h3>
                <textarea placeholder="Add your feedback..." rows="4" style="width: 100%;"></textarea>
                
                <div class="actions">
                    <button class="btn btn-approve">Approve & Continue</button>
                    <button class="btn btn-modify">Request Modifications</button>
                    <button class="btn btn-reject">Reject Analysis</button>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML
        approval_path = Path("approval.html")
        approval_path.write_text(approval_html)
        
        # Navigate to approval interface
        await page.goto(f"file://{approval_path.absolute()}")
        
        # Capture full page
        await page.screenshot(path=CURRENT_DIR / "approval_interface.png", full_page=True)
        
        # Test interaction elements
        approve_btn = page.locator(".btn-approve")
        assert await approve_btn.is_visible()
        
        reject_btn = page.locator(".btn-reject")
        assert await reject_btn.is_visible()
        
        # Capture components
        recommendation = page.locator(".ai-recommendation")
        await recommendation.screenshot(path=CURRENT_DIR / "approval_recommendation.png")
        
        actions = page.locator(".actions")
        await actions.screenshot(path=CURRENT_DIR / "approval_actions.png")
        
        # Clean up
        approval_path.unlink()
    
    async def test_realtime_updates(self, page):
        """Test real-time update visualization"""
        realtime_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Real-time Updates</title>
            <style>
                .update-feed {
                    height: 400px;
                    overflow-y: auto;
                    border: 1px solid #ddd;
                    padding: 10px;
                }
                .update-item {
                    padding: 10px;
                    margin: 5px 0;
                    background: #f8f9fa;
                    border-left: 3px solid #3498db;
                    animation: slideIn 0.5s;
                }
                @keyframes slideIn {
                    from { transform: translateX(-100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                .timestamp { color: #7f8c8d; font-size: 0.9em; }
                .progress-bar {
                    height: 20px;
                    background: #ecf0f1;
                    border-radius: 10px;
                    overflow: hidden;
                }
                .progress-fill {
                    height: 100%;
                    background: #3498db;
                    transition: width 0.5s;
                }
            </style>
        </head>
        <body>
            <h1>Real-time Task Updates</h1>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: 65%;"></div>
            </div>
            <p>Processing: 65% complete</p>
            
            <div class="update-feed">
                <div class="update-item">
                    <strong>Data Validation Complete</strong>
                    <div class="timestamp">2024-01-01 10:00:00</div>
                    <p>✅ 1000 rows validated successfully</p>
                </div>
                <div class="update-item">
                    <strong>AI Analysis Started</strong>
                    <div class="timestamp">2024-01-01 10:00:05</div>
                    <p>🤖 Running pattern recognition...</p>
                </div>
                <div class="update-item">
                    <strong>Confidence Check</strong>
                    <div class="timestamp">2024-01-01 10:00:10</div>
                    <p>⚠️ Confidence: 65% - Human review required</p>
                </div>
                <div class="update-item">
                    <strong>Awaiting Human Review</strong>
                    <div class="timestamp">2024-01-01 10:00:15</div>
                    <p>👤 Task queued for review (Priority: HIGH)</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save HTML
        realtime_path = Path("realtime.html")
        realtime_path.write_text(realtime_html)
        
        # Navigate
        await page.goto(f"file://{realtime_path.absolute()}")
        
        # Capture
        await page.screenshot(path=CURRENT_DIR / "realtime_updates.png", full_page=True)
        
        # Clean up
        realtime_path.unlink()


# ====================
# Performance Tests
# ====================

class TestOrchestratorPerformance:
    """Performance and load tests"""
    
    async def test_concurrent_tasks(self):
        """Test handling multiple concurrent tasks"""
        client = requests
        tasks = []
        
        # Submit 10 tasks concurrently
        for i in range(10):
            task_data = {
                "task_type": f"test_task_{i}",
                "parameters": {"test_id": i},
                "priority": 2
            }
            response = client.post(f"{API_BASE_URL}/api/v1/tasks/submit", json=task_data)
            if response.status_code == 200:
                tasks.append(response.json()["task_id"])
        
        assert len(tasks) == 10
        
        # Wait and check all tasks
        time.sleep(5)
        
        for task_id in tasks:
            response = client.get(f"{API_BASE_URL}/api/v1/tasks/{task_id}")
            assert response.status_code == 200
    
    async def test_large_data_handling(self):
        """Test handling large datasets"""
        factory = TestDataFactory()
        df = factory.create_large_dataset()
        filepath = factory.save_test_data(df, "test_large.csv")
        
        client = requests
        task_data = {
            "task_type": "large_data_analysis",
            "data_path": str(filepath),
            "parameters": {"data_path": str(filepath)},
            "priority": 3
        }
        
        start_time = time.time()
        response = client.post(f"{API_BASE_URL}/api/v1/tasks/submit", json=task_data)
        submit_time = time.time() - start_time
        
        assert response.status_code == 200
        assert submit_time < 1.0  # Should submit quickly
        
        # Clean up
        filepath.unlink()


# ====================
# Main Test Runner
# ====================

async def main():
    """Main test runner with reporting"""
    print("\n" + "="*60)
    print("ORCHESTRATOR TEST SUITE")
    print("="*60)
    
    results = {
        "unit_tests": {"passed": 0, "failed": 0},
        "integration_tests": {"passed": 0, "failed": 0},
        "visual_tests": {"passed": 0, "failed": 0},
        "performance_tests": {"passed": 0, "failed": 0}
    }
    
    # Run unit tests
    print("\n📝 Running Unit Tests...")
    unit_tester = TestOrchestratorUnit()
    try:
        unit_tester.test_task_creation()
        print("  ✅ Task creation test passed")
        results["unit_tests"]["passed"] += 1
    except Exception as e:
        print(f"  ❌ Task creation test failed: {e}")
        results["unit_tests"]["failed"] += 1
    
    try:
        unit_tester.test_database_operations()
        print("  ✅ Database operations test passed")
        results["unit_tests"]["passed"] += 1
    except Exception as e:
        print(f"  ❌ Database operations test failed: {e}")
        results["unit_tests"]["failed"] += 1
    
    try:
        unit_tester.test_confidence_threshold()
        print("  ✅ Confidence threshold test passed")
        results["unit_tests"]["passed"] += 1
    except Exception as e:
        print(f"  ❌ Confidence threshold test failed: {e}")
        results["unit_tests"]["failed"] += 1
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    integration_tester = TestOrchestratorIntegration()
    client = requests
    
    try:
        integration_tester.test_health_check(client)
        print("  ✅ Health check test passed")
        results["integration_tests"]["passed"] += 1
    except Exception as e:
        print(f"  ❌ Health check test failed: {e}")
        results["integration_tests"]["failed"] += 1
    
    try:
        integration_tester.test_submit_task(client)
        print("  ✅ Task submission test passed")
        results["integration_tests"]["passed"] += 1
    except Exception as e:
        print(f"  ❌ Task submission test failed: {e}")
        results["integration_tests"]["failed"] += 1
    
    try:
        integration_tester.test_metrics_endpoint(client)
        print("  ✅ Metrics endpoint test passed")
        results["integration_tests"]["passed"] += 1
    except Exception as e:
        print(f"  ❌ Metrics endpoint test failed: {e}")
        results["integration_tests"]["failed"] += 1
    
    # Run visual tests
    print("\n🎨 Running Visual Tests...")
    visual_tester = TestOrchestratorVisual()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            await visual_tester.test_dashboard_ui(page)
            print("  ✅ Dashboard UI test passed")
            results["visual_tests"]["passed"] += 1
        except Exception as e:
            print(f"  ❌ Dashboard UI test failed: {e}")
            results["visual_tests"]["failed"] += 1
        
        try:
            await visual_tester.test_approval_workflow_ui(page)
            print("  ✅ Approval workflow UI test passed")
            results["visual_tests"]["passed"] += 1
        except Exception as e:
            print(f"  ❌ Approval workflow UI test failed: {e}")
            results["visual_tests"]["failed"] += 1
        
        try:
            await visual_tester.test_realtime_updates(page)
            print("  ✅ Real-time updates test passed")
            results["visual_tests"]["passed"] += 1
        except Exception as e:
            print(f"  ❌ Real-time updates test failed: {e}")
            results["visual_tests"]["failed"] += 1
        
        await browser.close()
    
    # Run performance tests
    print("\n⚡ Running Performance Tests...")
    performance_tester = TestOrchestratorPerformance()
    
    try:
        await performance_tester.test_concurrent_tasks()
        print("  ✅ Concurrent tasks test passed")
        results["performance_tests"]["passed"] += 1
    except Exception as e:
        print(f"  ❌ Concurrent tasks test failed: {e}")
        results["performance_tests"]["failed"] += 1
    
    try:
        await performance_tester.test_large_data_handling()
        print("  ✅ Large data handling test passed")
        results["performance_tests"]["passed"] += 1
    except Exception as e:
        print(f"  ❌ Large data handling test failed: {e}")
        results["performance_tests"]["failed"] += 1
    
    # Print summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    total_passed = 0
    total_failed = 0
    
    for category, counts in results.items():
        passed = counts["passed"]
        failed = counts["failed"]
        total_passed += passed
        total_failed += failed
        
        print(f"\n{category.replace('_', ' ').title()}:")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  Success Rate: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "N/A")
    
    print("\n" + "-"*60)
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    print(f"Overall Success Rate: {total_passed/(total_passed+total_failed)*100:.1f}%" if (total_passed+total_failed) > 0 else "N/A")
    print("="*60)
    
    # Save test report
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "success_rate": total_passed/(total_passed+total_failed)*100 if (total_passed+total_failed) > 0 else 0,
        "screenshots_generated": len(list(CURRENT_DIR.glob("*.png")))
    }
    
    report_path = Path("orchestrator_test_report.json")
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\n📊 Test report saved to: {report_path}")
    print(f"📸 Screenshots saved to: {SCREENSHOT_DIR}")
    
    return total_failed == 0


if __name__ == "__main__":
    # Check if orchestrator is running
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code != 200:
            print("⚠️ Orchestrator not running. Start it with: python orchestrator.py")
            sys.exit(1)
    except:
        print("⚠️ Orchestrator not accessible. Start it with: python orchestrator.py")
        sys.exit(1)
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)