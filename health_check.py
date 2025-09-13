#!/usr/bin/env python3
"""
Health Check System - Pre-flight validation and system monitoring
Part of RECURSIVE_ENGINE v2.0
"""

import os
import sys
import json
import yaml
import time
import psutil
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

class HealthCheck:
    """System health validation and monitoring"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'health_score': 0,
            'status': 'unknown',
            'issues': [],
            'recommendations': []
        }
        
    def log(self, message: str, level: str = 'info'):
        """Log messages with color coding"""
        if not self.verbose and level == 'debug':
            return
            
        colors = {
            'success': GREEN,
            'warning': YELLOW,
            'error': RED,
            'info': BLUE,
            'debug': ''
        }
        
        color = colors.get(level, '')
        print(f"{color}{message}{RESET}")
    
    def check_python_version(self) -> bool:
        """Verify Python version compatibility"""
        self.log("Checking Python version...", 'info')
        
        required = (3, 8)
        current = sys.version_info[:2]
        
        if current >= required:
            self.log(f"  ✅ Python {current[0]}.{current[1]} (required: {required[0]}.{required[1]}+)", 'success')
            self.results['checks']['python_version'] = True
            return True
        else:
            self.log(f"  ❌ Python {current[0]}.{current[1]} (required: {required[0]}.{required[1]}+)", 'error')
            self.results['checks']['python_version'] = False
            self.results['issues'].append(f"Python version {current} < {required}")
            return False
    
    def check_required_files(self) -> bool:
        """Verify all required files exist"""
        self.log("Checking required files...", 'info')
        
        required_files = [
            'SYSTEM_STATE.yaml',
            'ERROR_PATTERNS.yaml',
            'TASK_PIPELINE.md',
            'TEST_MATRIX.json',
            'human_loop_platform/app_working.py',
            'orchestrator.py'
        ]
        
        all_exist = True
        for file in required_files:
            path = Path(file)
            if path.exists():
                self.log(f"  ✅ {file}", 'success')
            else:
                self.log(f"  ❌ {file} missing", 'error')
                self.results['issues'].append(f"Missing file: {file}")
                all_exist = False
        
        self.results['checks']['required_files'] = all_exist
        return all_exist
    
    def check_services(self) -> bool:
        """Check if required services are running"""
        self.log("Checking services...", 'info')
        
        services = {
            'streamlit': {
                'url': 'http://localhost:8503',
                'process': 'streamlit',
                'critical': True
            },
            'orchestrator': {
                'url': 'http://localhost:8000/health',
                'process': 'orchestrator',
                'critical': False
            }
        }
        
        all_running = True
        for name, config in services.items():
            try:
                response = requests.get(config['url'], timeout=2)
                if response.status_code < 500:
                    self.log(f"  ✅ {name} service running", 'success')
                    self.results['checks'][f'service_{name}'] = True
                else:
                    raise Exception(f"Status code: {response.status_code}")
            except:
                if config['critical']:
                    self.log(f"  ❌ {name} service not responding", 'error')
                    self.results['issues'].append(f"{name} service not running")
                    all_running = False
                else:
                    self.log(f"  ⚠️  {name} service not responding (non-critical)", 'warning')
                self.results['checks'][f'service_{name}'] = False
        
        return all_running
    
    def check_environment(self) -> bool:
        """Check environment variables and configuration"""
        self.log("Checking environment...", 'info')
        
        env_vars = ['GEMINI_API_KEY', 'GOOGLE_API_KEY', 'AI_API_KEY']
        api_key_found = False
        
        # Check for .env file
        env_file = Path('.env')
        if env_file.exists():
            self.log("  ✅ .env file found", 'success')
            # Load and check for API keys
            with open(env_file) as f:
                content = f.read()
                for var in env_vars:
                    if f"{var}=" in content:
                        api_key_found = True
                        break
        
        # Check environment variables
        for var in env_vars:
            if os.getenv(var):
                api_key_found = True
                self.log(f"  ✅ {var} configured", 'success')
                break
        
        if not api_key_found:
            self.log("  ⚠️  No API key configured", 'warning')
            self.results['recommendations'].append("Configure API key in .env or environment")
        
        self.results['checks']['environment'] = api_key_found
        return True  # Non-critical
    
    def check_dependencies(self) -> bool:
        """Check Python package dependencies"""
        self.log("Checking dependencies...", 'info')
        
        required_packages = [
            'streamlit',
            'pandas',
            'playwright',
            'langgraph',
            'fastapi',
            'google-generativeai'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.log(f"  ✅ {package}", 'success')
            except ImportError:
                self.log(f"  ❌ {package} missing", 'error')
                missing.append(package)
        
        if missing:
            self.results['issues'].append(f"Missing packages: {', '.join(missing)}")
            self.results['recommendations'].append(f"Run: pip install {' '.join(missing)}")
        
        self.results['checks']['dependencies'] = len(missing) == 0
        return len(missing) == 0
    
    def check_system_resources(self) -> bool:
        """Check system resource availability"""
        self.log("Checking system resources...", 'info')
        
        # Memory check
        memory = psutil.virtual_memory()
        memory_gb = memory.available / (1024**3)
        
        if memory_gb > 2:
            self.log(f"  ✅ Memory: {memory_gb:.1f}GB available", 'success')
        else:
            self.log(f"  ⚠️  Memory: {memory_gb:.1f}GB (low)", 'warning')
            self.results['recommendations'].append("Close unnecessary applications")
        
        # Disk check
        disk = psutil.disk_usage('/')
        disk_gb = disk.free / (1024**3)
        
        if disk_gb > 5:
            self.log(f"  ✅ Disk: {disk_gb:.1f}GB free", 'success')
        else:
            self.log(f"  ⚠️  Disk: {disk_gb:.1f}GB (low)", 'warning')
            self.results['recommendations'].append("Free up disk space")
        
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent < 80:
            self.log(f"  ✅ CPU: {cpu_percent}% usage", 'success')
        else:
            self.log(f"  ⚠️  CPU: {cpu_percent}% (high)", 'warning')
        
        self.results['checks']['resources'] = memory_gb > 1 and disk_gb > 1
        return True  # Non-critical
    
    def check_test_status(self) -> bool:
        """Check recent test results"""
        self.log("Checking test status...", 'info')
        
        try:
            with open('TEST_MATRIX.json') as f:
                test_data = json.load(f)
            
            pass_rate = test_data['summary']['pass_rate']
            if pass_rate > 90:
                self.log(f"  ✅ Test pass rate: {pass_rate}%", 'success')
            elif pass_rate > 70:
                self.log(f"  ⚠️  Test pass rate: {pass_rate}%", 'warning')
            else:
                self.log(f"  ❌ Test pass rate: {pass_rate}%", 'error')
                self.results['issues'].append(f"Low test pass rate: {pass_rate}%")
            
            self.results['checks']['tests'] = pass_rate > 70
            return pass_rate > 70
        except:
            self.log("  ⚠️  Could not read test results", 'warning')
            return True  # Non-critical
    
    def check_git_status(self) -> bool:
        """Check git repository status"""
        self.log("Checking git status...", 'info')
        
        try:
            # Check for uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.stdout:
                changes = len(result.stdout.strip().split('\n'))
                self.log(f"  ⚠️  {changes} uncommitted changes", 'warning')
                self.results['recommendations'].append("Commit or stash changes")
            else:
                self.log("  ✅ Working directory clean", 'success')
            
            self.results['checks']['git'] = True
            return True
        except:
            self.log("  ⚠️  Could not check git status", 'warning')
            return True  # Non-critical
    
    def calculate_health_score(self) -> float:
        """Calculate overall health score"""
        checks = self.results['checks']
        
        # Weighted scoring
        weights = {
            'python_version': 10,
            'required_files': 20,
            'service_streamlit': 15,
            'service_orchestrator': 10,
            'environment': 10,
            'dependencies': 15,
            'resources': 5,
            'tests': 10,
            'git': 5
        }
        
        total_weight = sum(weights.values())
        score = 0
        
        for check, weight in weights.items():
            if check in checks and checks[check]:
                score += weight
        
        health_score = (score / total_weight) * 100
        self.results['health_score'] = round(health_score, 1)
        
        return health_score
    
    def run_all_checks(self) -> Tuple[bool, Dict]:
        """Run all health checks"""
        self.log("\n" + "="*50, 'info')
        self.log("🏥 SYSTEM HEALTH CHECK", 'info')
        self.log("="*50 + "\n", 'info')
        
        # Run checks
        checks = [
            self.check_python_version(),
            self.check_required_files(),
            self.check_services(),
            self.check_environment(),
            self.check_dependencies(),
            self.check_system_resources(),
            self.check_test_status(),
            self.check_git_status()
        ]
        
        # Calculate health score
        health_score = self.calculate_health_score()
        
        # Determine status
        critical_checks = [checks[0], checks[1], checks[4]]  # Python, files, dependencies
        
        if all(critical_checks) and health_score > 80:
            self.results['status'] = 'healthy'
            status_icon = "✅"
            status_color = 'success'
        elif all(critical_checks) and health_score > 60:
            self.results['status'] = 'degraded'
            status_icon = "⚠️"
            status_color = 'warning'
        else:
            self.results['status'] = 'unhealthy'
            status_icon = "❌"
            status_color = 'error'
        
        # Print summary
        self.log("\n" + "="*50, 'info')
        self.log(f"{status_icon} HEALTH SCORE: {health_score}% - {self.results['status'].upper()}", status_color)
        self.log("="*50, 'info')
        
        if self.results['issues']:
            self.log("\n🔴 Issues Found:", 'error')
            for issue in self.results['issues']:
                self.log(f"  • {issue}", 'error')
        
        if self.results['recommendations']:
            self.log("\n💡 Recommendations:", 'warning')
            for rec in self.results['recommendations']:
                self.log(f"  • {rec}", 'warning')
        
        # Save results
        with open('health_check_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"\n📊 Results saved to health_check_results.json", 'info')
        
        return health_score > 60, self.results
    
    def quick_check(self) -> bool:
        """Quick health check for critical systems only"""
        self.verbose = False
        
        critical = [
            self.check_required_files(),
            self.check_services(),
            self.check_dependencies()
        ]
        
        return all(critical)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='System Health Check')
    parser.add_argument('--quick', action='store_true', help='Quick check only')
    parser.add_argument('--init', action='store_true', help='Initialize system')
    parser.add_argument('--retry', action='store_true', help='Retry after recovery')
    parser.add_argument('--json', action='store_true', help='Output JSON only')
    
    args = parser.parse_args()
    
    health = HealthCheck(verbose=not args.json)
    
    if args.init:
        # Initialize system
        health.log("Initializing system...", 'info')
        os.system('bash recovery_mode.sh --setup')
        
    if args.quick:
        success = health.quick_check()
        sys.exit(0 if success else 1)
    
    success, results = health.run_all_checks()
    
    if args.json:
        print(json.dumps(results))
    
    if args.retry and not success:
        health.log("\n🔄 Running recovery mode...", 'warning')
        os.system('bash recovery_mode.sh')
        health.log("\n🔄 Retrying health check...", 'info')
        success, results = health.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()