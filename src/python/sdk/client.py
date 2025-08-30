#!/usr/bin/env python3
"""
Python SDK Client for AI Data Analysis Platform API
Simplifies integration with the platform
"""

import json
import time
import requests
import pandas as pd
import websocket
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    """REST API client for the platform"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:5000",
        api_key: str = None,
        token: str = None
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.token = token
        self.session = requests.Session()
        
        # Set authentication headers
        if api_key:
            self.session.headers['X-API-Key'] = api_key
        elif token:
            self.session.headers['Authorization'] = f'Bearer {token}'
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        files: Dict = None,
        params: Dict = None
    ) -> requests.Response:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                files=files,
                params=params
            )
            response.raise_for_status()
            return response
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    # === Authentication ===
    
    def register(self, email: str, password: str, name: str = None) -> Dict:
        """Register new user"""
        data = {
            'email': email,
            'password': password,
            'name': name or email.split('@')[0]
        }
        
        response = self._request('POST', '/api/v1/register', data=data)
        result = response.json()
        
        # Update authentication
        self.token = result.get('token')
        self.api_key = result.get('api_key')
        self.session.headers['Authorization'] = f'Bearer {self.token}'
        
        return result
    
    def login(self, email: str, password: str) -> Dict:
        """Login user"""
        data = {'email': email, 'password': password}
        
        response = self._request('POST', '/api/v1/login', data=data)
        result = response.json()
        
        # Update authentication
        self.token = result.get('token')
        self.session.headers['Authorization'] = f'Bearer {self.token}'
        
        return result
    
    # === Data Management ===
    
    def upload_file(self, file_path: Union[str, Path]) -> Dict:
        """Upload data file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f)}
            response = self._request('POST', '/api/v1/upload', files=files)
        
        return response.json()
    
    def upload_dataframe(self, df: pd.DataFrame, filename: str = "data.csv") -> Dict:
        """Upload pandas DataFrame"""
        # Convert to CSV in memory
        csv_buffer = df.to_csv(index=False).encode()
        files = {'file': (filename, csv_buffer)}
        
        response = self._request('POST', '/api/v1/upload', files=files)
        return response.json()
    
    # === Analysis ===
    
    def analyze(
        self,
        session_id: str,
        analysis_type: str = "summary",
        agent: str = "data_analysis",
        parameters: Dict = None
    ) -> Dict:
        """Run data analysis"""
        data = {
            'session_id': session_id,
            'type': analysis_type,
            'agent': agent,
            'parameters': parameters or {}
        }
        
        response = self._request('POST', '/api/v1/analyze', data=data)
        return response.json()
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get analysis job status"""
        response = self._request('GET', f'/api/v1/jobs/{job_id}')
        return response.json()
    
    def wait_for_job(self, job_id: str, timeout: int = 300) -> Dict:
        """Wait for job completion"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.get_job_status(job_id)
            
            if result['status'] in ['completed', 'failed']:
                return result
            
            time.sleep(2)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
    
    # === Model Management ===
    
    def list_models(
        self,
        name: str = None,
        status: str = None,
        model_type: str = None
    ) -> List[Dict]:
        """List available models"""
        params = {}
        if name:
            params['name'] = name
        if status:
            params['status'] = status
        if model_type:
            params['type'] = model_type
        
        response = self._request('GET', '/api/v1/models', params=params)
        return response.json()['models']
    
    def train_model(
        self,
        session_id: str,
        target: str,
        features: List[str],
        model_type: str = "classification",
        algorithm: str = "auto",
        name: str = "model",
        version: str = "1.0",
        test_size: float = 0.2
    ) -> Dict:
        """Train a new model"""
        data = {
            'session_id': session_id,
            'target': target,
            'features': features,
            'model_type': model_type,
            'algorithm': algorithm,
            'name': name,
            'version': version,
            'test_size': test_size
        }
        
        response = self._request('POST', '/api/v1/models/train', data=data)
        return response.json()
    
    def predict(
        self,
        model_id: str,
        data: Union[Dict, List[Dict], pd.DataFrame]
    ) -> Dict:
        """Make predictions using a model"""
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('records')
        
        request_data = {'data': data}
        
        response = self._request('POST', f'/api/v1/models/{model_id}/predict', data=request_data)
        return response.json()
    
    def promote_model(self, model_id: str, status: str) -> Dict:
        """Promote model to new status"""
        data = {'status': status}
        
        response = self._request('POST', f'/api/v1/models/{model_id}/promote', data=data)
        return response.json()
    
    # === Visualization ===
    
    def create_visualization(
        self,
        session_id: str,
        viz_type: str = "auto",
        columns: List[str] = None,
        options: Dict = None
    ) -> Dict:
        """Create data visualization"""
        data = {
            'session_id': session_id,
            'type': viz_type,
            'columns': columns or [],
            'options': options or {}
        }
        
        response = self._request('POST', '/api/v1/visualize', data=data)
        return response.json()
    
    # === Export ===
    
    def export_results(self, job_id: str, format: str = "json") -> Union[Dict, bytes]:
        """Export analysis results"""
        params = {'format': format}
        
        response = self._request('GET', f'/api/v1/export/{job_id}', params=params)
        
        if format == 'json':
            return response.json()
        else:
            return response.content
    
    # === Monitoring ===
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        response = self._request('GET', '/api/v1/stats')
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = requests.get(f"{self.base_url}/api/v1/health")
        return response.json()

class RealtimeClient:
    """WebSocket client for real-time collaboration"""
    
    def __init__(
        self,
        ws_url: str = "ws://localhost:8765",
        user_data: Dict = None
    ):
        self.ws_url = ws_url
        self.user_data = user_data or {'name': 'Anonymous', 'email': 'user@example.com'}
        self.ws = None
        self.user_id = None
        self.workspace_id = None
    
    def connect(self, workspace_id: str = None):
        """Connect to WebSocket server"""
        self.workspace_id = workspace_id
        
        def on_open(ws):
            # Register user
            registration = {
                'type': 'register',
                'user': self.user_data,
                'workspace_id': workspace_id
            }
            ws.send(json.dumps(registration))
            logger.info("Connected to realtime server")
        
        def on_message(ws, message):
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'connected':
                self.user_id = data['user']['id']
                logger.info(f"Registered as user {self.user_id}")
            
            elif msg_type == 'user_joined':
                logger.info(f"User joined: {data['data']['user']['name']}")
            
            elif msg_type == 'data_update':
                logger.info(f"Data update from {data['data']['user']['name']}")
            
            # Override in subclass for custom handling
            self.handle_message(data)
        
        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")
        
        def on_close(ws):
            logger.info("WebSocket connection closed")
        
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Run in thread
        import threading
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Wait for connection
        time.sleep(2)
    
    def handle_message(self, data: Dict):
        """Override to handle messages"""
        pass
    
    def send_data_update(self, update_type: str, data: Dict):
        """Send data update to workspace"""
        if not self.ws:
            raise ConnectionError("Not connected")
        
        message = {
            'type': 'data_update',
            'data': {
                'type': update_type,
                'data': data
            }
        }
        
        self.ws.send(json.dumps(message))
    
    def send_chat(self, message: str):
        """Send chat message"""
        if not self.ws:
            raise ConnectionError("Not connected")
        
        chat_data = {
            'type': 'chat',
            'chat': {'message': message}
        }
        
        self.ws.send(json.dumps(chat_data))
    
    def disconnect(self):
        """Disconnect from server"""
        if self.ws:
            self.ws.close()

class DataAnalysisPlatform:
    """High-level client combining API and realtime features"""
    
    def __init__(
        self,
        api_url: str = "http://localhost:5000",
        ws_url: str = "ws://localhost:8765",
        api_key: str = None
    ):
        self.api = APIClient(api_url, api_key=api_key)
        self.realtime = None
        self.current_session = None
    
    def connect_realtime(self, workspace_id: str = None, user_data: Dict = None):
        """Connect to realtime collaboration"""
        self.realtime = RealtimeClient(ws_url, user_data)
        self.realtime.connect(workspace_id)
    
    def quick_analysis(self, file_path: str) -> Dict:
        """Perform quick analysis on a file"""
        # Upload file
        upload_result = self.api.upload_file(file_path)
        self.current_session = upload_result['session_id']
        
        # Run analysis
        analysis_result = self.api.analyze(
            self.current_session,
            analysis_type="summary"
        )
        
        # Wait for completion if async
        if 'job_id' in analysis_result:
            analysis_result = self.api.wait_for_job(analysis_result['job_id'])
        
        return analysis_result
    
    def train_and_deploy_model(
        self,
        df: pd.DataFrame,
        target: str,
        features: List[str],
        model_name: str = "model"
    ) -> str:
        """Train and deploy a model"""
        # Upload data
        upload_result = self.api.upload_dataframe(df)
        session_id = upload_result['session_id']
        
        # Train model
        train_result = self.api.train_model(
            session_id=session_id,
            target=target,
            features=features,
            name=model_name
        )
        
        model_id = train_result['model_id']
        
        # Promote to production
        self.api.promote_model(model_id, 'production')
        
        logger.info(f"Model {model_id} deployed to production")
        return model_id
    
    def collaborative_analysis(
        self,
        workspace_id: str,
        df: pd.DataFrame
    ):
        """Start collaborative analysis session"""
        # Connect to realtime
        self.connect_realtime(workspace_id)
        
        # Upload data
        upload_result = self.api.upload_dataframe(df)
        session_id = upload_result['session_id']
        
        # Notify workspace
        if self.realtime:
            self.realtime.send_data_update(
                'data',
                {'session_id': session_id, 'shape': df.shape}
            )
        
        return session_id

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = DataAnalysisPlatform()
    
    # Create sample data
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [2, 4, 6, 8, 10],
        'target': [0, 0, 1, 1, 1]
    })
    
    # Quick analysis
    # result = client.quick_analysis("data.csv")
    # print("Analysis result:", result)
    
    # Train model
    # model_id = client.train_and_deploy_model(
    #     df, 'target', ['feature1', 'feature2'], 'my_model'
    # )
    # print(f"Model deployed: {model_id}")
    
    print("SDK client ready")