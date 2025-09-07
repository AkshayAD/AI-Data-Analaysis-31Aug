#!/usr/bin/env python3
"""
🤖 Automated Test Harness - AI Analysis Platform
Continuous validation and tracking system for recursive development
"""

import asyncio
import json
import os
import sys
import subprocess
import time
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_harness.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestHarness:
    """Automated test execution and result tracking system"""
    
    def __init__(self):
        self.root_path = Path("/root/repo")
        self.project_state_file = self.root_path / "PROJECT_STATE.yaml"
        self.test_results_file = self.root_path / "TEST_RESULTS.json"
        self.todo_tracker_file = self.root_path / "TODO_TRACKER.md"
        self.metrics_dashboard_file = self.root_path / "METRICS_DASHBOARD.md"
        
        # Test configuration
        self.test_file = self.root_path / "test_working_app_fixed.py"
        self.app_file = self.root_path / "human_loop_platform" / "app_working.py"
        self.screenshot_dir = self.root_path / "screenshots_working_app"
        self.app_url = "http://localhost:8503"
        self.app_port = 8503
        
    def load_project_state(self) -> Dict[str, Any]:
        """Load current project state from YAML"""
        try:
            with open(self.project_state_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading project state: {e}")
            return {}
    
    def save_project_state(self, state: Dict[str, Any]):
        """Save updated project state to YAML"""
        try:
            state['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            with open(self.project_state_file, 'w') as f:
                yaml.dump(state, f, default_flow_style=False, sort_keys=False)
            logger.info("Project state updated successfully")
        except Exception as e:
            logger.error(f"Error saving project state: {e}")
    
    def load_test_results(self) -> Dict[str, Any]:
        """Load test results history"""
        try:
            with open(self.test_results_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading test results: {e}")
            return {}
    
    def save_test_results(self, results: Dict[str, Any]):
        """Save updated test results"""
        try:
            results['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            with open(self.test_results_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info("Test results updated successfully")
        except Exception as e:
            logger.error(f"Error saving test results: {e}")
    
    def check_app_running(self) -> bool:
        """Check if Streamlit app is running"""
        try:
            import requests
            response = requests.get(self.app_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_app(self) -> Optional[subprocess.Popen]:
        """Start Streamlit application if not running"""
        if self.check_app_running():
            logger.info("App already running")
            return None
        
        logger.info("Starting Streamlit application...")
        try:
            os.chdir(self.root_path / "human_loop_platform")
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", 
                "app_working.py", "--server.port", str(self.app_port),
                "--server.headless", "true"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for app to start
            time.sleep(10)
            
            if self.check_app_running():
                logger.info("App started successfully")
                return process
            else:
                logger.error("App failed to start")
                return None
        except Exception as e:
            logger.error(f"Error starting app: {e}")
            return None
    
    def run_tests(self) -> Dict[str, Any]:
        """Execute the test suite and capture results"""
        logger.info("Running test suite...")
        
        # Ensure app is running
        app_process = self.start_app()
        
        try:
            # Change to repo root for test execution
            os.chdir(self.root_path)
            
            # Run the test
            start_time = time.time()
            result = subprocess.run([
                sys.executable, str(self.test_file)
            ], capture_output=True, text=True, timeout=120)
            execution_time = time.time() - start_time
            
            # Parse results
            test_results = {
                "execution_id": f"run-{int(time.time())}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "test_file": str(self.test_file),
                "execution_time": f"{execution_time:.1f}s",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            # Analyze output for specific test results
            output = result.stdout + result.stderr
            test_results.update(self.parse_test_output(output))
            
            logger.info(f"Test execution completed in {execution_time:.1f}s")
            return test_results
            
        except subprocess.TimeoutExpired:
            logger.error("Test execution timed out")
            return {"error": "timeout", "timestamp": datetime.now(timezone.utc).isoformat()}
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
        finally:
            # Clean up app process if we started it
            if app_process:
                try:
                    app_process.terminate()
                    app_process.wait(timeout=5)
                except:
                    app_process.kill()
    
    def parse_test_output(self, output: str) -> Dict[str, Any]:
        """Parse test output to extract specific test results"""
        results = {
            "detailed_results": {},
            "issues_discovered": [],
            "performance_metrics": {},
            "screenshots_captured": []
        }
        
        # Analyze output for test patterns
        lines = output.split('\n')
        current_test = None
        
        for line in lines:
            line = line.strip()
            
            # Detect test execution patterns
            if "Testing:" in line or "TESTING:" in line:
                current_test = line.replace("Testing:", "").replace("TESTING:", "").strip()
                
            # Detect success patterns
            elif "✅" in line or "PASS" in line or "SUCCESS" in line:
                if current_test:
                    results["detailed_results"][current_test] = {
                        "status": "pass",
                        "message": line
                    }
                    
            # Detect failure patterns
            elif "❌" in line or "FAIL" in line or "ERROR" in line:
                if current_test:
                    results["detailed_results"][current_test] = {
                        "status": "fail", 
                        "message": line
                    }
                    results["issues_discovered"].append({
                        "test": current_test,
                        "error": line,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
            # Detect screenshot captures
            elif "Screenshot saved" in line or ".png" in line:
                results["screenshots_captured"].append(line)
            
            # Detect performance metrics
            elif "took" in line and "seconds" in line:
                try:
                    # Extract timing information
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "seconds" in part and i > 0:
                            duration = parts[i-1].replace("s", "").replace(":", "")
                            if current_test and duration.replace(".", "").isdigit():
                                results["performance_metrics"][current_test] = f"{duration}s"
                except:
                    pass
        
        return results
    
    def count_screenshots(self) -> Dict[str, int]:
        """Count available screenshots"""
        screenshot_count = {"total": 0, "by_stage": {}}
        
        if self.screenshot_dir.exists():
            for screenshot in self.screenshot_dir.glob("*.png"):
                screenshot_count["total"] += 1
                # Extract stage from filename if possible
                name = screenshot.name.lower()
                if "stage0" in name:
                    screenshot_count["by_stage"]["stage0"] = screenshot_count["by_stage"].get("stage0", 0) + 1
                elif "stage1" in name:
                    screenshot_count["by_stage"]["stage1"] = screenshot_count["by_stage"].get("stage1", 0) + 1
                elif "stage2" in name:
                    screenshot_count["by_stage"]["stage2"] = screenshot_count["by_stage"].get("stage2", 0) + 1
        
        return screenshot_count
    
    def calculate_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance and quality metrics"""
        metrics = {
            "test_execution": {
                "duration": test_results.get("execution_time", "0s"),
                "success": test_results.get("success", False),
                "timestamp": test_results.get("timestamp")
            },
            "screenshots": self.count_screenshots(),
            "app_status": {
                "running": self.check_app_running(),
                "url": self.app_url,
                "port": self.app_port
            }
        }
        
        # Calculate pass/fail rates from detailed results
        detailed = test_results.get("detailed_results", {})
        if detailed:
            total_tests = len(detailed)
            passed_tests = sum(1 for result in detailed.values() if result.get("status") == "pass")
            failed_tests = total_tests - passed_tests
            
            metrics["test_summary"] = {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            }
        
        return metrics
    
    def update_tracking_files(self, test_results: Dict[str, Any], metrics: Dict[str, Any]):
        """Update all tracking files with new test results"""
        
        # Update PROJECT_STATE.yaml
        try:
            state = self.load_project_state()
            
            # Update test results section
            if "test_results" not in state:
                state["test_results"] = {}
            
            state["test_results"].update({
                "last_run": datetime.now(timezone.utc).date().isoformat(),
                "overall_coverage": metrics.get("test_summary", {}).get("pass_rate", 0),
                "passed": metrics.get("test_summary", {}).get("passed", 0),
                "failed": metrics.get("test_summary", {}).get("failed", 0),
                "total": metrics.get("test_summary", {}).get("total", 0)
            })
            
            # Update issues based on test failures
            issues_discovered = test_results.get("issues_discovered", [])
            if "issues" not in state:
                state["issues"] = {"critical": [], "medium": []}
            
            # Add new issues from test failures
            for issue in issues_discovered:
                new_issue = {
                    "description": f"Test failure: {issue.get('test', 'Unknown')}",
                    "details": issue.get("error", ""),
                    "impact": "Test failure detected",
                    "priority": 1 if "critical" in issue.get("error", "").lower() else 3,
                    "discovered": issue.get("timestamp")
                }
                
                # Check if issue already exists
                existing = any(
                    existing_issue.get("description") == new_issue["description"]
                    for existing_issue in state["issues"]["critical"] + state["issues"]["medium"]
                )
                
                if not existing:
                    if new_issue["priority"] <= 2:
                        state["issues"]["critical"].append(new_issue)
                    else:
                        state["issues"]["medium"].append(new_issue)
            
            self.save_project_state(state)
            
        except Exception as e:
            logger.error(f"Error updating project state: {e}")
        
        # Update TEST_RESULTS.json
        try:
            results_data = self.load_test_results()
            
            # Add new execution to history
            if "execution_history" not in results_data:
                results_data["execution_history"] = []
            
            execution_entry = {
                "execution_id": test_results.get("execution_id"),
                "timestamp": test_results.get("timestamp"),
                "test_file": str(self.test_file),
                "overall_result": {
                    "status": "pass" if test_results.get("success") else "fail",
                    "execution_time": test_results.get("execution_time"),
                    "return_code": test_results.get("return_code")
                },
                "detailed_results": test_results.get("detailed_results", {}),
                "issues_discovered": test_results.get("issues_discovered", []),
                "screenshots_captured": test_results.get("screenshots_captured", []),
                "metrics": metrics
            }
            
            results_data["execution_history"].append(execution_entry)
            
            # Keep only last 10 executions to prevent file bloat
            if len(results_data["execution_history"]) > 10:
                results_data["execution_history"] = results_data["execution_history"][-10:]
            
            # Update current status
            results_data["current_status"] = {
                "last_execution": test_results.get("execution_id"),
                "status": "pass" if test_results.get("success") else "fail",
                "timestamp": test_results.get("timestamp"),
                "ready_for_next_iteration": test_results.get("success", False)
            }
            
            self.save_test_results(results_data)
            
        except Exception as e:
            logger.error(f"Error updating test results: {e}")
    
    def generate_summary_report(self, test_results: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Generate a summary report of test execution"""
        
        summary = f"""
🤖 TEST HARNESS EXECUTION REPORT
{'='*50}

Timestamp: {test_results.get('timestamp', 'Unknown')}
Execution ID: {test_results.get('execution_id', 'Unknown')}
Duration: {test_results.get('execution_time', 'Unknown')}

OVERALL RESULT: {'✅ PASS' if test_results.get('success') else '❌ FAIL'}

TEST SUMMARY:
"""
        
        test_summary = metrics.get("test_summary", {})
        if test_summary:
            summary += f"""
- Total Tests: {test_summary.get('total', 0)}
- Passed: {test_summary.get('passed', 0)} ✅
- Failed: {test_summary.get('failed', 0)} ❌  
- Pass Rate: {test_summary.get('pass_rate', 0):.1f}%
"""
        
        detailed_results = test_results.get("detailed_results", {})
        if detailed_results:
            summary += "\nDETAILED RESULTS:\n"
            for test_name, result in detailed_results.items():
                status_icon = "✅" if result.get("status") == "pass" else "❌"
                summary += f"- {test_name}: {status_icon} {result.get('status', 'unknown').upper()}\n"
        
        issues = test_results.get("issues_discovered", [])
        if issues:
            summary += f"\nISSUES DISCOVERED ({len(issues)}):\n"
            for issue in issues:
                summary += f"- {issue.get('test', 'Unknown')}: {issue.get('error', 'No details')}\n"
        
        screenshots = test_results.get("screenshots_captured", [])
        if screenshots:
            summary += f"\nSCREENSHOTS CAPTURED ({len(screenshots)}):\n"
            for screenshot in screenshots:
                summary += f"- {screenshot}\n"
        
        app_status = metrics.get("app_status", {})
        summary += f"""
APP STATUS:
- Running: {'✅ Yes' if app_status.get('running') else '❌ No'}
- URL: {app_status.get('url', 'Unknown')}

NEXT ACTIONS:
"""
        
        if test_results.get("success"):
            summary += "- ✅ All tests passing - ready for next development iteration\n"
            summary += "- 📋 Check TODO_TRACKER.md for next priority task\n"
            summary += "- 🚀 Execute AUTOMATION_PROMPT.md to continue development\n"
        else:
            summary += "- 🔧 Fix failing tests before proceeding\n"
            summary += "- 📊 Review detailed error messages above\n"
            summary += "- 🔄 Re-run test harness after fixes\n"
        
        summary += f"""
FILES UPDATED:
- PROJECT_STATE.yaml ✅
- TEST_RESULTS.json ✅  
- METRICS_DASHBOARD.md (manual update recommended)

{'='*50}
"""
        
        return summary
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation cycle"""
        logger.info("Starting full validation cycle...")
        
        try:
            # Execute tests
            test_results = self.run_tests()
            
            # Calculate metrics
            metrics = self.calculate_metrics(test_results)
            
            # Update tracking files
            self.update_tracking_files(test_results, metrics)
            
            # Generate summary
            summary = self.generate_summary_report(test_results, metrics)
            
            logger.info("Validation cycle completed")
            print(summary)
            
            return {
                "success": True,
                "test_results": test_results,
                "metrics": metrics,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error in validation cycle: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

def main():
    """Main execution function"""
    harness = TestHarness()
    
    print("🤖 AI Analysis Platform - Automated Test Harness")
    print("="*60)
    print()
    
    # Check if required files exist
    required_files = [
        harness.project_state_file,
        harness.test_results_file,
        harness.test_file
    ]
    
    missing_files = [f for f in required_files if not f.exists()]
    if missing_files:
        print("❌ Missing required files:")
        for f in missing_files:
            print(f"   - {f}")
        return 1
    
    # Run validation
    try:
        result = asyncio.run(harness.run_full_validation())
        return 0 if result.get("success") else 1
    except KeyboardInterrupt:
        print("\n⚡ Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())