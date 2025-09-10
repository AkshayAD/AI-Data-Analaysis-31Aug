#!/usr/bin/env python3
"""
Orchestrator Bridge Module
Provides integration between Streamlit app and LangGraph orchestrator
"""

import asyncio
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Callable
import requests
import websocket
from enum import Enum

# Configuration
ORCHESTRATOR_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
HEALTH_CHECK_INTERVAL = 30  # seconds
RECONNECT_DELAY = 5  # seconds

class ConnectionStatus(Enum):
    """Orchestrator connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class OrchestratorBridge:
    """Bridge between Streamlit and LangGraph orchestrator"""
    
    def __init__(self, client_id: str = None):
        """Initialize orchestrator bridge"""
        self.client_id = client_id or f"streamlit-{datetime.now().timestamp()}"
        self.orchestrator_url = ORCHESTRATOR_URL
        self.ws_url = f"{WS_URL}/{self.client_id}"
        self.status = ConnectionStatus.DISCONNECTED
        self.ws_connection = None
        self.ws_thread = None
        self.callbacks = {}
        self.last_health_check = None
        self.is_running = False
        
    def connect_to_orchestrator(self) -> bool:
        """Establish connection to orchestrator service"""
        try:
            # Check health endpoint
            response = requests.get(f"{self.orchestrator_url}/health", timeout=5)
            
            if response.status_code == 200:
                self.status = ConnectionStatus.CONNECTED
                self.last_health_check = datetime.now()
                
                # Start WebSocket connection in background
                if not self.ws_thread or not self.ws_thread.is_alive():
                    self.start_websocket_connection()
                
                return True
            else:
                self.status = ConnectionStatus.ERROR
                return False
                
        except requests.exceptions.ConnectionError:
            self.status = ConnectionStatus.DISCONNECTED
            return False
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            print(f"Error connecting to orchestrator: {str(e)}")
            return False
    
    def start_websocket_connection(self):
        """Start WebSocket connection in background thread"""
        self.is_running = True
        self.ws_thread = threading.Thread(target=self._websocket_handler, daemon=True)
        self.ws_thread.start()
    
    def _websocket_handler(self):
        """Handle WebSocket connection and messages"""
        while self.is_running:
            try:
                # Create WebSocket connection
                self.ws_connection = websocket.WebSocketApp(
                    self.ws_url,
                    on_open=self._on_ws_open,
                    on_message=self._on_ws_message,
                    on_error=self._on_ws_error,
                    on_close=self._on_ws_close
                )
                
                # Run WebSocket (blocking)
                self.ws_connection.run_forever()
                
            except Exception as e:
                print(f"WebSocket error: {str(e)}")
                self.status = ConnectionStatus.ERROR
                
            # Reconnect after delay
            if self.is_running:
                time.sleep(RECONNECT_DELAY)
    
    def _on_ws_open(self, ws):
        """Handle WebSocket connection open"""
        print(f"WebSocket connected: {self.client_id}")
        self.status = ConnectionStatus.CONNECTED
        
        # Send initial handshake
        ws.send(json.dumps({
            "type": "handshake",
            "client_id": self.client_id,
            "client_type": "streamlit"
        }))
    
    def _on_ws_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            # Handle different message types
            if msg_type == "task_update":
                self._handle_task_update(data)
            elif msg_type == "human_review_request":
                self._handle_review_request(data)
            elif msg_type == "status_update":
                self._handle_status_update(data)
            else:
                print(f"Unknown message type: {msg_type}")
                
        except json.JSONDecodeError:
            print(f"Invalid WebSocket message: {message}")
    
    def _on_ws_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"WebSocket error: {error}")
        self.status = ConnectionStatus.ERROR
    
    def _on_ws_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.status = ConnectionStatus.DISCONNECTED
    
    def _handle_task_update(self, data: Dict[str, Any]):
        """Handle task update messages"""
        task_id = data.get("task_id")
        status = data.get("status")
        
        # Call registered callback
        if "task_update" in self.callbacks:
            self.callbacks["task_update"](task_id, status, data)
    
    def _handle_review_request(self, data: Dict[str, Any]):
        """Handle human review request"""
        review_id = data.get("review_id")
        
        # Call registered callback
        if "review_request" in self.callbacks:
            self.callbacks["review_request"](review_id, data)
    
    def _handle_status_update(self, data: Dict[str, Any]):
        """Handle status update messages"""
        # Call registered callback
        if "status_update" in self.callbacks:
            self.callbacks["status_update"](data)
    
    def submit_task(self, task_type: str, parameters: Dict[str, Any], 
                   priority: int = 2, confidence_threshold: float = 0.7,
                   require_human_review: bool = False) -> Optional[str]:
        """Submit task to orchestrator"""
        try:
            task_data = {
                "task_type": task_type,
                "parameters": parameters,
                "priority": priority,
                "confidence_threshold": confidence_threshold,
                "require_human_review": require_human_review
            }
            
            response = requests.post(
                f"{self.orchestrator_url}/tasks",
                json=task_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("task_id")
            else:
                print(f"Task submission failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error submitting task: {str(e)}")
            return None
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        try:
            response = requests.get(
                f"{self.orchestrator_url}/tasks/{task_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error getting task status: {str(e)}")
            return None
    
    def get_all_tasks(self, limit: int = 10) -> Optional[list]:
        """Get list of all tasks"""
        try:
            response = requests.get(
                f"{self.orchestrator_url}/tasks",
                params={"limit": limit},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json().get("tasks", [])
            else:
                return None
                
        except Exception as e:
            print(f"Error getting tasks: {str(e)}")
            return None
    
    def submit_review_decision(self, review_id: str, decision: str, 
                              feedback: Optional[str] = None) -> bool:
        """Submit human review decision"""
        try:
            review_data = {
                "decision": decision,
                "feedback": feedback,
                "reviewer_id": self.client_id
            }
            
            response = requests.post(
                f"{self.orchestrator_url}/reviews/{review_id}/decision",
                json=review_data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error submitting review: {str(e)}")
            return False
    
    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for specific event type"""
        self.callbacks[event_type] = callback
    
    def handle_websocket_updates(self, update_callback: Callable):
        """Register callback for all WebSocket updates"""
        self.callbacks["status_update"] = update_callback
    
    def disconnect(self):
        """Disconnect from orchestrator"""
        self.is_running = False
        
        if self.ws_connection:
            self.ws_connection.close()
            
        self.status = ConnectionStatus.DISCONNECTED
    
    def is_connected(self) -> bool:
        """Check if connected to orchestrator"""
        return self.status == ConnectionStatus.CONNECTED
    
    def get_status(self) -> str:
        """Get current connection status"""
        return self.status.value

# Global bridge instance (singleton)
_bridge_instance = None

def get_bridge_instance(client_id: str = None) -> OrchestratorBridge:
    """Get or create bridge instance"""
    global _bridge_instance
    
    if _bridge_instance is None:
        _bridge_instance = OrchestratorBridge(client_id)
    
    return _bridge_instance

# Convenience functions for direct import
def connect_to_orchestrator() -> bool:
    """Connect to orchestrator service"""
    bridge = get_bridge_instance()
    return bridge.connect_to_orchestrator()

def submit_task(task_type: str, parameters: Dict[str, Any], **kwargs) -> Optional[str]:
    """Submit task to orchestrator"""
    bridge = get_bridge_instance()
    return bridge.submit_task(task_type, parameters, **kwargs)

def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get task status"""
    bridge = get_bridge_instance()
    return bridge.get_task_status(task_id)

def handle_websocket_updates(callback: Callable):
    """Register WebSocket update handler"""
    bridge = get_bridge_instance()
    bridge.handle_websocket_updates(callback)