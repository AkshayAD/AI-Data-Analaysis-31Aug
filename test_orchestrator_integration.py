#!/usr/bin/env python3
"""
Test Suite for TASK-007: LangGraph Orchestrator Integration
Tests the integration between Streamlit app and LangGraph orchestrator
"""

import asyncio
import json
import time
import tempfile
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import requests
from playwright.async_api import async_playwright
import websocket
import threading

# Configuration
STREAMLIT_URL = "http://localhost:8503"
ORCHESTRATOR_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
SCREENSHOT_DIR = Path("screenshots_orchestrator_integration")
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Test data
TEST_API_KEY = "AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8"
TEST_OBJECTIVE = "Analyze customer behavior patterns and predict churn"

class TestOrchestratorIntegration:
    """Tests for orchestrator integration with Streamlit"""
    
    def test_orchestrator_service_running(self):
        """Test that orchestrator service is accessible"""
        print("\n" + "="*60)
        print("🧪 TEST: Orchestrator Service Status")
        print("="*60)
        
        try:
            # Check health endpoint
            response = requests.get(f"{ORCHESTRATOR_URL}/health", timeout=5)
            
            if response.status_code == 200:
                print("  ✅ Orchestrator service is running")
                health_data = response.json()
                print(f"  📊 Status: {health_data.get('status', 'unknown')}")
                print(f"  📊 Version: {health_data.get('version', 'unknown')}")
                return True
            else:
                print(f"  ❌ Orchestrator returned status: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("  ❌ Cannot connect to orchestrator service")
            print(f"     Please start it with: python orchestrator.py --port 8000")
            return False
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_websocket_connection(self):
        """Test WebSocket connection to orchestrator"""
        print("\n" + "="*60)
        print("🧪 TEST: WebSocket Connection")
        print("="*60)
        
        try:
            # Create WebSocket connection
            ws = websocket.WebSocket()
            ws.connect(f"{WS_URL}/test-client")
            
            # Send test message
            test_msg = json.dumps({"type": "ping"})
            ws.send(test_msg)
            
            # Wait for response (with timeout)
            ws.settimeout(5)
            response = ws.recv()
            
            if response:
                print("  ✅ WebSocket connection established")
                print(f"  📊 Response: {response[:100]}")
                ws.close()
                return True
            else:
                print("  ❌ No response from WebSocket")
                ws.close()
                return False
                
        except Exception as e:
            print(f"  ❌ WebSocket connection failed: {str(e)}")
            return False
    
    def test_task_submission_api(self):
        """Test task submission via orchestrator API"""
        print("\n" + "="*60)
        print("🧪 TEST: Task Submission API")
        print("="*60)
        
        try:
            # Create test task
            task_data = {
                "task_type": "data_analysis",
                "parameters": {
                    "objective": TEST_OBJECTIVE,
                    "data_sample": "test data sample"
                },
                "priority": 2,
                "confidence_threshold": 0.7
            }
            
            # Submit task
            response = requests.post(
                f"{ORCHESTRATOR_URL}/tasks",
                json=task_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("task_id")
                print(f"  ✅ Task submitted successfully")
                print(f"  📊 Task ID: {task_id}")
                return task_id
            else:
                print(f"  ❌ Task submission failed: {response.status_code}")
                print(f"     Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error submitting task: {str(e)}")
            return None
    
    def test_streamlit_orchestrator_bridge(self):
        """Test that Streamlit can communicate with orchestrator"""
        print("\n" + "="*60)
        print("🧪 TEST: Streamlit-Orchestrator Bridge")
        print("="*60)
        
        # Check if bridge module exists
        bridge_file = Path("human_loop_platform/orchestrator_bridge.py")
        
        if bridge_file.exists():
            print("  ✅ Orchestrator bridge module exists")
            
            # Try importing it
            try:
                import sys
                sys.path.append("human_loop_platform")
                import orchestrator_bridge
                
                print("  ✅ Bridge module imports successfully")
                
                # Check for required functions
                required_functions = [
                    "connect_to_orchestrator",
                    "submit_task",
                    "get_task_status",
                    "handle_websocket_updates"
                ]
                
                for func_name in required_functions:
                    if hasattr(orchestrator_bridge, func_name):
                        print(f"  ✅ Function '{func_name}' found")
                    else:
                        print(f"  ❌ Function '{func_name}' missing")
                        return False
                
                return True
                
            except ImportError as e:
                print(f"  ❌ Failed to import bridge module: {str(e)}")
                return False
        else:
            print("  ❌ Orchestrator bridge module not found")
            print(f"     Expected at: {bridge_file}")
            return False

async def test_ui_integration():
    """Test UI integration with orchestrator"""
    print("\n" + "="*60)
    print("🧪 TEST: UI Integration with Orchestrator")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to Streamlit app
            await page.goto(STREAMLIT_URL, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # Take screenshot
            await page.screenshot(path=SCREENSHOT_DIR / "01_initial.png")
            
            # Check for orchestrator status indicator
            orchestrator_status = await page.query_selector('text=Orchestrator Status')
            if orchestrator_status:
                print("  ✅ Orchestrator status indicator found in UI")
                
                # Check status value
                status_element = await page.query_selector('[data-testid="orchestrator-status"]')
                if status_element:
                    status = await status_element.inner_text()
                    print(f"  📊 Status: {status}")
                    
                    if "Connected" in status:
                        print("  ✅ Orchestrator connected")
                    else:
                        print("  ⚠️ Orchestrator not connected")
            else:
                print("  ❌ No orchestrator status indicator in UI")
                return False
            
            # Check for HITL workflow button
            hitl_button = await page.query_selector('button:has-text("Enable HITL Workflow")')
            if hitl_button:
                print("  ✅ HITL workflow button found")
                
                # Click to enable
                await hitl_button.click()
                await page.wait_for_timeout(1000)
                
                # Check for confirmation
                confirmation = await page.query_selector('text=HITL workflow enabled')
                if confirmation:
                    print("  ✅ HITL workflow can be enabled")
                else:
                    print("  ⚠️ HITL workflow enable confirmation not found")
            else:
                print("  ❌ HITL workflow button not found")
            
            await page.screenshot(path=SCREENSHOT_DIR / "02_orchestrator_ui.png")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_ui.png")
            return False
        finally:
            await browser.close()

async def test_end_to_end_workflow():
    """Test complete end-to-end workflow with orchestrator"""
    print("\n" + "="*60)
    print("🧪 TEST: End-to-End Workflow")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to app
            await page.goto(STREAMLIT_URL, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # Create test data
            test_df = pd.DataFrame({
                'customer_id': range(1, 101),
                'age': np.random.randint(18, 70, 100),
                'purchase_amount': np.random.uniform(10, 500, 100),
                'churn_risk': np.random.choice([0, 1], 100)
            })
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                test_df.to_csv(f, index=False)
                test_file = f.name
            
            # Upload file
            file_input = await page.wait_for_selector('input[type="file"]', timeout=5000)
            await file_input.set_input_files(test_file)
            await page.wait_for_timeout(2000)
            
            # Enter objective
            objective_input = await page.query_selector('textarea')
            if objective_input:
                await objective_input.fill(TEST_OBJECTIVE)
            
            # Enable HITL workflow
            hitl_checkbox = await page.query_selector('input[type="checkbox"][id*="hitl"]')
            if hitl_checkbox:
                await hitl_checkbox.check()
                print("  ✅ HITL workflow enabled")
            
            # Submit to orchestrator
            submit_button = await page.query_selector('button:has-text("Submit to Orchestrator")')
            if submit_button:
                await submit_button.click()
                print("  ✅ Task submitted to orchestrator")
                
                # Wait for task ID
                await page.wait_for_timeout(2000)
                task_id_element = await page.query_selector('[data-testid="task-id"]')
                if task_id_element:
                    task_id = await task_id_element.inner_text()
                    print(f"  📊 Task ID: {task_id}")
                
                # Check for real-time updates
                await page.wait_for_timeout(3000)
                status_updates = await page.query_selector('[data-testid="status-updates"]')
                if status_updates:
                    updates = await status_updates.inner_text()
                    print(f"  ✅ Real-time updates received")
                    print(f"  📊 Updates: {updates[:200]}...")
                
                await page.screenshot(path=SCREENSHOT_DIR / "03_workflow_complete.png")
                return True
            else:
                print("  ❌ Submit to orchestrator button not found")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_workflow.png")
            return False
        finally:
            await browser.close()

def main():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("🚀 ORCHESTRATOR INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Streamlit URL: {STREAMLIT_URL}")
    print(f"Orchestrator URL: {ORCHESTRATOR_URL}")
    print("="*60)
    
    # Initialize test suite
    test_suite = TestOrchestratorIntegration()
    
    # Run tests
    results = {
        "Orchestrator Service": test_suite.test_orchestrator_service_running(),
        "WebSocket Connection": test_suite.test_websocket_connection(),
        "Task Submission API": test_suite.test_task_submission_api() is not None,
        "Bridge Module": test_suite.test_streamlit_orchestrator_bridge(),
    }
    
    # Run async tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    results["UI Integration"] = loop.run_until_complete(test_ui_integration())
    results["End-to-End Workflow"] = loop.run_until_complete(test_end_to_end_workflow())
    
    # Save results
    results_file = SCREENSHOT_DIR / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "tests": results,
            "passed": sum(results.values()),
            "failed": len(results) - sum(results.values()),
            "total": len(results)
        }, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    print(f"Results saved to: {results_file}")
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)