#!/usr/bin/env python3
"""
🤖 Simplified Test Harness - AI Analysis Platform
Validates recursive development system without external dependencies
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleTestHarness:
    """Simplified test harness using only built-in libraries"""
    
    def __init__(self):
        self.root_path = Path("/root/repo")
        self.test_file = self.root_path / "test_working_app_fixed.py"
        self.screenshot_dir = self.root_path / "screenshots_working_app"
        self.app_url = "http://localhost:8503"
        
    def check_required_files(self) -> dict:
        """Check if all automation files exist"""
        files = {
            "PROJECT_STATE.yaml": self.root_path / "PROJECT_STATE.yaml",
            "AUTOMATION_PROMPT.md": self.root_path / "AUTOMATION_PROMPT.md", 
            "TODO_TRACKER.md": self.root_path / "TODO_TRACKER.md",
            "TEST_RESULTS.json": self.root_path / "TEST_RESULTS.json",
            "METRICS_DASHBOARD.md": self.root_path / "METRICS_DASHBOARD.md",
            "CLAUDE.md": self.root_path / "CLAUDE.md",
            "test_harness.py": self.root_path / "test_harness.py"
        }
        
        status = {}
        for name, path in files.items():
            status[name] = {
                "exists": path.exists(),
                "size": path.stat().st_size if path.exists() else 0,
                "path": str(path)
            }
        
        return status
    
    def check_app_status(self) -> dict:
        """Check if Streamlit app is accessible"""
        try:
            # Try to connect without external requests library
            import socket
            import urllib.request
            
            # Quick socket check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 8503))
            sock.close()
            
            return {
                "port_open": result == 0,
                "url": self.app_url,
                "status": "running" if result == 0 else "not_running"
            }
        except Exception as e:
            return {
                "port_open": False,
                "url": self.app_url,
                "status": "error",
                "error": str(e)
            }
    
    def count_screenshots(self) -> dict:
        """Count available screenshots"""
        count = {"total": 0, "files": []}
        
        if self.screenshot_dir.exists():
            for screenshot in self.screenshot_dir.glob("*.png"):
                count["total"] += 1
                count["files"].append(screenshot.name)
        
        return count
    
    def run_basic_test(self) -> dict:
        """Run basic test validation"""
        logger.info("Running basic test validation...")
        
        try:
            os.chdir(self.root_path)
            start_time = time.time()
            
            # Check if test file exists
            if not self.test_file.exists():
                return {
                    "status": "error",
                    "message": f"Test file not found: {self.test_file}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Try to run the test
            result = subprocess.run([
                sys.executable, str(self.test_file)
            ], capture_output=True, text=True, timeout=60)
            
            execution_time = time.time() - start_time
            
            return {
                "status": "completed",
                "success": result.returncode == 0,
                "execution_time": f"{execution_time:.1f}s",
                "return_code": result.returncode,
                "stdout_lines": len(result.stdout.split('\n')),
                "stderr_lines": len(result.stderr.split('\n')),
                "has_screenshots": "screenshot" in result.stdout.lower(),
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "message": "Test execution timed out after 60 seconds",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_automation_system(self) -> dict:
        """Validate the complete automation system"""
        logger.info("Validating automation system...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "healthy",
            "issues": []
        }
        
        # Check required files
        file_status = self.check_required_files()
        report["files"] = file_status
        
        missing_files = [name for name, status in file_status.items() if not status["exists"]]
        if missing_files:
            report["issues"].append(f"Missing files: {', '.join(missing_files)}")
            report["system_status"] = "degraded"
        
        # Check app status
        app_status = self.check_app_status()
        report["app"] = app_status
        
        if not app_status["port_open"]:
            report["issues"].append("Streamlit app not running on port 8503")
        
        # Count screenshots
        screenshots = self.count_screenshots()
        report["screenshots"] = screenshots
        
        # Run basic test
        test_result = self.run_basic_test()
        report["test"] = test_result
        
        if test_result.get("status") == "error":
            report["issues"].append(f"Test execution failed: {test_result.get('message', 'Unknown error')}")
            report["system_status"] = "error"
        elif not test_result.get("success", False):
            report["issues"].append("Tests are failing - system needs attention")
            report["system_status"] = "degraded"
        
        # Overall health assessment
        if not report["issues"]:
            report["system_status"] = "healthy"
            report["ready_for_automation"] = True
        else:
            report["ready_for_automation"] = False
        
        return report
    
    def generate_status_report(self, validation_result: dict) -> str:
        """Generate human-readable status report"""
        
        status = validation_result["system_status"]
        timestamp = validation_result["timestamp"]
        
        if status == "healthy":
            status_icon = "✅"
        elif status == "degraded": 
            status_icon = "⚠️"
        else:
            status_icon = "❌"
        
        report = f"""
🤖 RECURSIVE DEVELOPMENT SYSTEM - VALIDATION REPORT
{'='*60}

Timestamp: {timestamp}
Overall Status: {status_icon} {status.upper()}
Ready for Automation: {'✅ YES' if validation_result.get('ready_for_automation') else '❌ NO'}

FILE SYSTEM STATUS:
"""
        
        files = validation_result.get("files", {})
        for name, info in files.items():
            icon = "✅" if info["exists"] else "❌"
            size = f" ({info['size']} bytes)" if info["exists"] else ""
            report += f"  {icon} {name}{size}\n"
        
        app = validation_result.get("app", {})
        report += f"""
APPLICATION STATUS:
  Port 8503: {'✅ Open' if app.get('port_open') else '❌ Closed'}
  Status: {app.get('status', 'unknown')}
  URL: {app.get('url', 'unknown')}
"""
        
        screenshots = validation_result.get("screenshots", {})
        report += f"""
SCREENSHOTS:
  Total: {screenshots.get('total', 0)} files
  Directory: screenshots_working_app/
"""
        
        test = validation_result.get("test", {})
        test_icon = "✅" if test.get("success") else "❌"
        report += f"""
TEST EXECUTION:
  Status: {test_icon} {test.get('status', 'unknown').upper()}
  Duration: {test.get('execution_time', 'unknown')}
  Return Code: {test.get('return_code', 'unknown')}
"""
        
        issues = validation_result.get("issues", [])
        if issues:
            report += f"""
ISSUES FOUND ({len(issues)}):
"""
            for issue in issues:
                report += f"  ⚠️  {issue}\n"
        
        report += f"""
NEXT STEPS:
"""
        
        if validation_result.get("ready_for_automation"):
            report += """  🚀 System is ready for recursive development!
  📋 Copy contents of AUTOMATION_PROMPT.md
  🤖 Send to Claude Code to begin autonomous development
  📈 Monitor progress via METRICS_DASHBOARD.md
"""
        else:
            report += """  🔧 Fix the issues listed above before proceeding
  📝 Check individual files and resolve problems
  🔄 Re-run this validation after fixes
"""
        
        report += f"""
AUTOMATION FILES:
  📊 PROJECT_STATE.yaml - Development state tracking
  🔄 AUTOMATION_PROMPT.md - Recursive prompt template  
  📋 TODO_TRACKER.md - Task management (24 tasks)
  🧪 TEST_RESULTS.json - Test execution history
  📈 METRICS_DASHBOARD.md - Progress visualization
  🤖 test_harness.py - Full automation system

{'='*60}
"""
        
        return report

def main():
    """Main execution function"""
    harness = SimpleTestHarness()
    
    print("🤖 RECURSIVE DEVELOPMENT SYSTEM VALIDATION")
    print("="*50)
    
    try:
        # Run validation
        result = harness.validate_automation_system()
        
        # Generate and display report
        report = harness.generate_status_report(result)
        print(report)
        
        # Save result to file for future reference
        result_file = harness.root_path / "validation_result.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"📄 Full results saved to: {result_file}")
        
        # Return appropriate exit code
        return 0 if result.get("ready_for_automation") else 1
        
    except Exception as e:
        print(f"❌ Fatal error during validation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())