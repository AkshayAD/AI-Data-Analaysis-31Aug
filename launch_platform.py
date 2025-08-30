#!/usr/bin/env python3
"""
Launch script for AI Data Analysis Platform
Starts all services with one command
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class PlatformLauncher:
    """Manages platform services"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
    
    def start_service(self, name: str, command: list, env: dict = None):
        """Start a service subprocess"""
        try:
            logger.info(f"Starting {name}...")
            
            process = subprocess.Popen(
                command,
                env={**os.environ, **(env or {})},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[name] = process
            logger.info(f"✅ {name} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            return False
    
    def start_all(self, services: list = None):
        """Start all platform services"""
        self.running = True
        
        # Default services
        if not services:
            services = ['streamlit', 'api', 'websocket', 'monitoring']
        
        # Service configurations
        service_configs = {
            'streamlit': {
                'command': ['streamlit', 'run', 'streamlit_app_v2.py', 
                          '--server.port', '8501', '--server.headless', 'true'],
                'env': {}
            },
            'api': {
                'command': [sys.executable, 'src/python/api/api_server.py'],
                'env': {'API_PORT': '5000'}
            },
            'websocket': {
                'command': [sys.executable, 'src/python/collaboration/realtime_server.py'],
                'env': {}
            },
            'monitoring': {
                'command': [sys.executable, '-c', 
                          'from src.python.monitoring.monitor import monitoring; monitoring.start(); import time; time.sleep(86400)'],
                'env': {}
            }
        }
        
        # Start selected services
        for service in services:
            if service in service_configs:
                config = service_configs[service]
                self.start_service(service, config['command'], config['env'])
                time.sleep(2)  # Give service time to start
        
        logger.info("=" * 50)
        logger.info("🚀 Platform services started!")
        logger.info("=" * 50)
        logger.info("Access points:")
        logger.info("  📊 Streamlit UI: http://localhost:8501")
        logger.info("  🔌 REST API: http://localhost:5000")
        logger.info("  🔄 WebSocket: ws://localhost:8765")
        logger.info("  📈 API Health: http://localhost:5000/api/v1/health")
        logger.info("=" * 50)
        logger.info("Press Ctrl+C to stop all services")
    
    def stop_all(self):
        """Stop all running services"""
        logger.info("\nStopping services...")
        
        for name, process in self.processes.items():
            try:
                logger.info(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        self.processes.clear()
        self.running = False
        logger.info("All services stopped")
    
    def monitor_services(self):
        """Monitor running services"""
        while self.running:
            try:
                time.sleep(5)
                
                # Check if services are still running
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        logger.warning(f"Service {name} has stopped (exit code: {process.returncode})")
                        
                        # Try to restart
                        logger.info(f"Attempting to restart {name}...")
                        # Restart logic here if needed
                        
            except KeyboardInterrupt:
                break
    
    def run(self, services: list = None):
        """Main run loop"""
        # Set up signal handler
        def signal_handler(sig, frame):
            logger.info("\nReceived interrupt signal")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start services
        self.start_all(services)
        
        # Monitor services
        try:
            self.monitor_services()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()

def check_requirements():
    """Check if required packages are installed"""
    required = ['streamlit', 'flask', 'websockets', 'pandas', 'sklearn']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.warning(f"Missing packages: {', '.join(missing)}")
        logger.info("Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
        return False
    
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Launch AI Data Analysis Platform')
    parser.add_argument(
        '--services',
        nargs='+',
        choices=['streamlit', 'api', 'websocket', 'monitoring'],
        help='Services to start (default: all)'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check requirements'
    )
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Run in development mode'
    )
    
    args = parser.parse_args()
    
    # Check requirements
    logger.info("Checking requirements...")
    if not check_requirements():
        if args.check_only:
            sys.exit(1)
        logger.info("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    if args.check_only:
        logger.info("✅ All requirements satisfied")
        sys.exit(0)
    
    # Set development mode
    if args.dev:
        os.environ['API_DEBUG'] = 'true'
        os.environ['STREAMLIT_THEME_BASE'] = 'light'
    
    # Launch platform
    launcher = PlatformLauncher()
    launcher.run(args.services)

if __name__ == "__main__":
    main()