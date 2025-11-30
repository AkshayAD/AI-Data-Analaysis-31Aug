import subprocess
import socket
import time
import os
import signal
import sys
from typing import Optional

class MarimoServerManager:
    """Manages marimo server processes for Streamlit integration"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.port: Optional[int] = None
        self.current_notebook: Optional[str] = None
        self.mode: str = 'edit'

    def find_available_port(self, start_port: int = 3000, max_port: int = 4000) -> int:
        """Find an available port starting from start_port"""
        for port in range(start_port, max_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('127.0.0.1', port))
                    return port
                except OSError:
                    continue
        raise RuntimeError("No available ports found")

    def start_server(self, notebook_path: str, mode: str = 'edit') -> str:
        """
        Start marimo server for the given notebook
        mode: 'edit' or 'run'
        """
        # If already running for this notebook and mode, return current URL
        if (self.process and self.process.poll() is None and
            self.current_notebook == notebook_path and self.mode == mode):
            return self.get_url()

        # Stop existing server
        self.stop_server()

        # Verify file exists
        if not os.path.exists(notebook_path):
            raise FileNotFoundError(f"Notebook not found: {notebook_path}")

        self.port = self.find_available_port()
        self.current_notebook = notebook_path
        self.mode = mode

        cmd = [
            "marimo",
            mode,
            "--no-token",
            "--port", str(self.port),
            "--headless",
            notebook_path
        ]

        # Start process
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for server to start
        max_retries = 50
        for _ in range(max_retries):
            try:
                # Check if process is still alive
                if self.process.poll() is not None:
                    _, stderr = self.process.communicate()
                    raise RuntimeError(f"Marimo failed to start: {stderr}")

                # Check connection
                import urllib.request
                with urllib.request.urlopen(f"http://localhost:{self.port}/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(0.2)

        return self.get_url()

    def stop_server(self):
        """Stop the running marimo server"""
        if self.process:
            try:
                # terminate() is gentler than kill()
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            except Exception as e:
                print(f"Error stopping marimo server: {e}")
            finally:
                self.process = None
                self.port = None
                self.current_notebook = None

    def get_url(self) -> str:
        """Get the URL for the current server"""
        if self.port:
            return f"http://localhost:{self.port}"
        return ""

    def __del__(self):
        """Cleanup on deletion"""
        self.stop_server()
