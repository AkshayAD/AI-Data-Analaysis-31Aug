#!/usr/bin/env python3
"""
REST API Server for AI Data Analysis Platform
Provides endpoints for external integrations
"""

import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import wraps
import hashlib
import jwt
import pandas as pd
import io
import base64

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from agents import DataAnalysisAgent, VisualizationAgent, MLAgent
from agents.orchestrator import OrchestrationAgent
from agents.intelligent_agent import IntelligentAgent
from llm import GeminiClient
from ml.model_registry import ModelRegistry, ModelTrainer

# Configuration
SECRET_KEY = os.getenv('API_SECRET_KEY', 'your-secret-key-change-in-production')
UPLOAD_FOLDER = './uploads'
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json', 'parquet'}

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create upload directory
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# Initialize components
agents = {
    'data_analysis': DataAnalysisAgent(),
    'visualization': VisualizationAgent(),
    'ml': MLAgent(),
    'orchestrator': OrchestrationAgent()
}

model_registry = ModelRegistry()
model_trainer = ModelTrainer(model_registry)

# Initialize Gemini if API key available
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    try:
        llm_client = GeminiClient(api_key=gemini_key)
        agents['intelligent'] = IntelligentAgent(llm_client=llm_client)
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini: {e}")

# In-memory storage (replace with database in production)
users = {}
api_keys = {}
sessions = {}
analysis_jobs = {}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_api_key():
    """Generate a unique API key"""
    return hashlib.sha256(f"{uuid.uuid4()}{datetime.now()}".encode()).hexdigest()

def verify_token(f):
    """Decorator to verify JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            # Check for API key
            api_key = request.headers.get('X-API-Key')
            if api_key and api_key in api_keys:
                request.user = api_keys[api_key]
                return f(*args, **kwargs)
            return jsonify({'error': 'No token or API key provided'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# === Authentication Endpoints ===

@app.route('/api/v1/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    
    if email in users:
        return jsonify({'error': 'User already exists'}), 409
    
    # Create user
    user_id = str(uuid.uuid4())
    users[email] = {
        'id': user_id,
        'email': email,
        'password': generate_password_hash(data['password']),
        'name': data.get('name', email.split('@')[0]),
        'created_at': datetime.now().isoformat(),
        'api_keys': []
    }
    
    # Generate API key
    api_key = generate_api_key()
    api_keys[api_key] = {'user_id': user_id, 'email': email}
    users[email]['api_keys'].append(api_key)
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'user_id': user_id,
        'email': email,
        'token': token,
        'api_key': api_key
    }), 201

@app.route('/api/v1/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    
    if email not in users:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    user = users[email]
    
    if not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'user_id': user['id'],
        'email': email,
        'token': token,
        'api_keys': user.get('api_keys', [])
    }), 200

# === Data Upload Endpoints ===

@app.route('/api/v1/upload', methods=['POST'])
@verify_token
def upload_file():
    """Upload data file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    file_id = f"{uuid.uuid4()}_{filename}"
    file_path = Path(UPLOAD_FOLDER) / file_id
    file.save(str(file_path))
    
    # Process file
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif filename.endswith('.json'):
            df = pd.read_json(file_path)
        elif filename.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Store in session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'file_id': file_id,
            'file_path': str(file_path),
            'filename': filename,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'uploaded_at': datetime.now().isoformat(),
            'user_id': request.user.get('user_id')
        }
        
        return jsonify({
            'session_id': session_id,
            'file_id': file_id,
            'filename': filename,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'preview': df.head(5).to_dict('records')
        }), 201
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

# === Analysis Endpoints ===

@app.route('/api/v1/analyze', methods=['POST'])
@verify_token
def analyze_data():
    """Run data analysis"""
    data = request.json
    
    if not data or not data.get('session_id'):
        return jsonify({'error': 'Session ID required'}), 400
    
    session_id = data['session_id']
    
    if session_id not in sessions:
        return jsonify({'error': 'Invalid session'}), 404
    
    session = sessions[session_id]
    
    # Load data
    try:
        df = pd.read_csv(session['file_path']) if session['filename'].endswith('.csv') else \
             pd.read_excel(session['file_path']) if session['filename'].endswith('.xlsx') else \
             pd.read_json(session['file_path'])
    except Exception as e:
        return jsonify({'error': f'Failed to load data: {str(e)}'}), 500
    
    # Create analysis job
    job_id = str(uuid.uuid4())
    analysis_jobs[job_id] = {
        'id': job_id,
        'status': 'running',
        'created_at': datetime.now().isoformat(),
        'user_id': request.user.get('user_id')
    }
    
    # Run analysis
    try:
        analysis_type = data.get('type', 'summary')
        agent_name = data.get('agent', 'data_analysis')
        
        if agent_name not in agents:
            return jsonify({'error': f'Agent {agent_name} not available'}), 400
        
        agent = agents[agent_name]
        
        task = {
            'type': analysis_type,
            'data': df.to_dict() if len(df) < 10000 else df.head(10000).to_dict()
        }
        
        # Add custom parameters
        if 'parameters' in data:
            task.update(data['parameters'])
        
        result = agent.execute(task)
        
        # Update job
        analysis_jobs[job_id]['status'] = 'completed'
        analysis_jobs[job_id]['result'] = result
        analysis_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        analysis_jobs[job_id]['status'] = 'failed'
        analysis_jobs[job_id]['error'] = str(e)
        
        return jsonify({
            'job_id': job_id,
            'status': 'failed',
            'error': str(e)
        }), 500

@app.route('/api/v1/jobs/<job_id>', methods=['GET'])
@verify_token
def get_job_status(job_id):
    """Get analysis job status"""
    if job_id not in analysis_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = analysis_jobs[job_id]
    
    # Check ownership
    if job.get('user_id') != request.user.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(job), 200

# === Model Management Endpoints ===

@app.route('/api/v1/models', methods=['GET'])
@verify_token
def list_models():
    """List available models"""
    name = request.args.get('name')
    status = request.args.get('status')
    model_type = request.args.get('type')
    
    models = model_registry.list_models(
        name=name,
        status=status,
        model_type=model_type
    )
    
    return jsonify({
        'models': [m.to_dict() for m in models],
        'count': len(models)
    }), 200

@app.route('/api/v1/models/train', methods=['POST'])
@verify_token
def train_model():
    """Train a new model"""
    data = request.json
    
    if not data or not data.get('session_id'):
        return jsonify({'error': 'Session ID required'}), 400
    
    session_id = data['session_id']
    
    if session_id not in sessions:
        return jsonify({'error': 'Invalid session'}), 404
    
    # Load data
    session = sessions[session_id]
    df = pd.read_csv(session['file_path'])
    
    # Get training parameters
    target_column = data.get('target')
    feature_columns = data.get('features')
    
    if not target_column or not feature_columns:
        return jsonify({'error': 'Target and features required'}), 400
    
    try:
        X = df[feature_columns]
        y = df[target_column]
        
        # Train model
        model_id = model_trainer.train_model(
            X=X,
            y=y,
            model_type=data.get('model_type', 'classification'),
            algorithm=data.get('algorithm', 'auto'),
            name=data.get('name', 'api_model'),
            version=data.get('version', '1.0'),
            test_size=data.get('test_size', 0.2),
            author=request.user.get('email', 'unknown')
        )
        
        # Get model metadata
        metadata = model_registry.get_model_metadata(model_id)
        
        return jsonify({
            'model_id': model_id,
            'metadata': metadata.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        return jsonify({'error': f'Training failed: {str(e)}'}), 500

@app.route('/api/v1/models/<model_id>/predict', methods=['POST'])
@verify_token
def predict(model_id):
    """Make predictions using a model"""
    data = request.json
    
    if not data or 'data' not in data:
        return jsonify({'error': 'Data required for prediction'}), 400
    
    try:
        # Load model
        model = model_registry.load_model(model_id)
        metadata = model_registry.get_model_metadata(model_id)
        
        # Prepare data
        if isinstance(data['data'], list):
            X = pd.DataFrame(data['data'])
        else:
            X = pd.DataFrame([data['data']])
        
        # Ensure correct columns
        if set(X.columns) != set(metadata.feature_names):
            return jsonify({
                'error': f'Expected features: {metadata.feature_names}'
            }), 400
        
        # Make predictions
        predictions = model.predict(X[metadata.feature_names])
        
        # Get probabilities for classification
        probabilities = None
        if metadata.model_type == 'classification' and hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X[metadata.feature_names]).tolist()
        
        return jsonify({
            'predictions': predictions.tolist(),
            'probabilities': probabilities,
            'model_id': model_id,
            'model_name': metadata.name,
            'model_version': metadata.version
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/api/v1/models/<model_id>/promote', methods=['POST'])
@verify_token
def promote_model(model_id):
    """Promote model to new status"""
    data = request.json
    
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'New status required'}), 400
    
    try:
        success = model_registry.promote_model(model_id, new_status)
        if success:
            return jsonify({
                'message': f'Model promoted to {new_status}',
                'model_id': model_id
            }), 200
        else:
            return jsonify({'error': 'Model not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

# === Visualization Endpoints ===

@app.route('/api/v1/visualize', methods=['POST'])
@verify_token
def create_visualization():
    """Create data visualization"""
    data = request.json
    
    if not data or not data.get('session_id'):
        return jsonify({'error': 'Session ID required'}), 400
    
    session_id = data['session_id']
    
    if session_id not in sessions:
        return jsonify({'error': 'Invalid session'}), 404
    
    # Load data
    session = sessions[session_id]
    df = pd.read_csv(session['file_path'])
    
    # Create visualization
    viz_type = data.get('type', 'auto')
    columns = data.get('columns', [])
    
    try:
        task = {
            'type': viz_type,
            'data': df[columns].to_dict() if columns else df.to_dict(),
            'options': data.get('options', {})
        }
        
        result = agents['visualization'].execute(task)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Visualization failed: {e}")
        return jsonify({'error': f'Visualization failed: {str(e)}'}), 500

# === Export Endpoints ===

@app.route('/api/v1/export/<job_id>', methods=['GET'])
@verify_token
def export_results(job_id):
    """Export analysis results"""
    if job_id not in analysis_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = analysis_jobs[job_id]
    
    # Check ownership
    if job.get('user_id') != request.user.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify(job['result']), 200
    
    elif format_type == 'csv':
        # Convert to CSV if possible
        if 'data' in job['result'] and isinstance(job['result']['data'], dict):
            df = pd.DataFrame(job['result']['data'])
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            return send_file(
                io.BytesIO(csv_buffer.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'analysis_{job_id}.csv'
            )
        else:
            return jsonify({'error': 'Cannot export to CSV'}), 400
    
    else:
        return jsonify({'error': 'Unsupported format'}), 400

# === Health & Monitoring ===

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agents': list(agents.keys()),
        'models_count': len(model_registry.models)
    }), 200

@app.route('/api/v1/stats', methods=['GET'])
@verify_token
def get_stats():
    """Get usage statistics"""
    user_id = request.user.get('user_id')
    
    user_jobs = [j for j in analysis_jobs.values() if j.get('user_id') == user_id]
    
    return jsonify({
        'total_jobs': len(user_jobs),
        'completed_jobs': len([j for j in user_jobs if j['status'] == 'completed']),
        'failed_jobs': len([j for j in user_jobs if j['status'] == 'failed']),
        'active_sessions': len([s for s in sessions.values() if s.get('user_id') == user_id])
    }), 200

# === Error Handlers ===

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large'}), 413

def main():
    """Run the API server"""
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main()