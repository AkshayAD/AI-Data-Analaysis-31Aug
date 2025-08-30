#!/usr/bin/env python3
"""
Tests for Phase 4 Features:
- Real-time collaboration
- Model registry
- API endpoints
- Monitoring system
"""

import pytest
import json
import time
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src" / "python"))

# Import components
from ml.model_registry import ModelRegistry, ModelTrainer, ModelMetadata
from monitoring.monitor import (
    MonitoringSystem, MetricsCollector, EventLogger,
    PerformanceTracker, Metric, Event
)
from collaboration.realtime_server import (
    CollaborationServer, User, Workspace, Message
)
from sdk.client import APIClient, RealtimeClient, DataAnalysisPlatform

class TestModelRegistry:
    """Test model registry functionality"""
    
    @pytest.fixture
    def registry(self):
        """Create test registry"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ModelRegistry(registry_path=tmpdir)
    
    @pytest.fixture
    def sample_model(self):
        """Create sample model"""
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data"""
        X = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100)
        })
        y = pd.Series(np.random.randint(0, 2, 100), name='target')
        return X, y
    
    def test_register_model(self, registry, sample_model, sample_data):
        """Test model registration"""
        X, y = sample_data
        X_train, X_test = X[:80], X[80:]
        y_train, y_test = y[:80], y[80:]
        
        # Train model
        sample_model.fit(X_train, y_train)
        
        # Register model
        model_id = registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0",
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            model_type="classification",
            author="test_user",
            description="Test model",
            tags=["test", "sample"]
        )
        
        assert model_id in registry.models
        assert registry.models[model_id].name == "test_model"
        assert registry.models[model_id].version == "1.0"
        assert registry.models[model_id].model_type == "classification"
        assert "test" in registry.models[model_id].tags
    
    def test_load_model(self, registry, sample_model, sample_data):
        """Test model loading"""
        X, y = sample_data
        sample_model.fit(X, y)
        
        # Register model
        model_id = registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0",
            X_train=X,
            y_train=y
        )
        
        # Load model
        loaded_model = registry.load_model(model_id)
        
        assert loaded_model is not None
        assert hasattr(loaded_model, 'predict')
        
        # Test prediction
        predictions = loaded_model.predict(X[:5])
        assert len(predictions) == 5
    
    def test_list_models(self, registry, sample_model, sample_data):
        """Test listing models with filters"""
        X, y = sample_data
        sample_model.fit(X, y)
        
        # Register multiple models
        model_id1 = registry.register_model(
            model=sample_model,
            name="model_a",
            version="1.0",
            X_train=X,
            y_train=y,
            model_type="classification"
        )
        
        model_id2 = registry.register_model(
            model=sample_model,
            name="model_b",
            version="2.0",
            X_train=X,
            y_train=y,
            model_type="regression"
        )
        
        # List all models
        all_models = registry.list_models()
        assert len(all_models) == 2
        
        # Filter by name
        models_a = registry.list_models(name="model_a")
        assert len(models_a) == 1
        assert models_a[0].name == "model_a"
        
        # Filter by type
        classification_models = registry.list_models(model_type="classification")
        assert len(classification_models) == 1
    
    def test_promote_model(self, registry, sample_model, sample_data):
        """Test model promotion"""
        X, y = sample_data
        sample_model.fit(X, y)
        
        model_id = registry.register_model(
            model=sample_model,
            name="test_model",
            version="1.0",
            X_train=X,
            y_train=y
        )
        
        # Initial status should be draft
        assert registry.models[model_id].status == "draft"
        
        # Promote to staging
        success = registry.promote_model(model_id, "staging")
        assert success
        assert registry.models[model_id].status == "staging"
        
        # Promote to production
        success = registry.promote_model(model_id, "production")
        assert success
        assert registry.models[model_id].status == "production"
    
    def test_model_comparison(self, registry, sample_data):
        """Test comparing multiple models"""
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier
        
        X, y = sample_data
        X_train, X_test = X[:80], X[80:]
        y_train, y_test = y[:80], y[80:]
        
        # Train and register multiple models
        models = [
            LogisticRegression(),
            RandomForestClassifier(n_estimators=10)
        ]
        
        model_ids = []
        for i, model in enumerate(models):
            model.fit(X_train, y_train)
            model_id = registry.register_model(
                model=model,
                name=f"model_{i}",
                version="1.0",
                X_train=X_train,
                y_train=y_train
            )
            model_ids.append(model_id)
        
        # Compare models
        comparison = registry.compare_models(model_ids, X_test, y_test)
        
        assert len(comparison) == 2
        assert 'accuracy' in comparison.columns or 'r2_score' in comparison.columns

class TestMonitoringSystem:
    """Test monitoring system"""
    
    @pytest.fixture
    def monitoring(self):
        """Create monitoring system"""
        return MonitoringSystem()
    
    def test_metrics_collection(self, monitoring):
        """Test metrics collection"""
        collector = monitoring.metrics_collector
        
        # Collect metrics
        metrics = collector.collect_system_metrics()
        
        assert len(metrics) > 0
        assert any(m.name == "system.cpu.usage" for m in metrics)
        assert any(m.name == "system.memory.usage" for m in metrics)
        
        # Check metric structure
        cpu_metric = next(m for m in metrics if m.name == "system.cpu.usage")
        assert cpu_metric.value >= 0
        assert cpu_metric.value <= 100
        assert cpu_metric.unit == "percent"
    
    def test_event_logging(self, monitoring):
        """Test event logging"""
        logger = monitoring.event_logger
        
        # Log events
        logger.log_event("test_event", "Test message", level="info")
        logger.log_event("error_event", "Error occurred", level="error")
        
        # Get recent events
        events = logger.get_recent_events(10)
        assert len(events) >= 2
        
        # Filter by level
        error_events = logger.get_recent_events(10, level="error")
        assert len(error_events) >= 1
        assert all(e['level'] == 'error' for e in error_events)
        
        # Check statistics
        stats = logger.get_event_statistics()
        assert stats['test_event'] >= 1
        assert stats['error_event'] >= 1
    
    def test_performance_tracking(self, monitoring):
        """Test performance tracking"""
        tracker = monitoring.performance_tracker
        
        @tracker.track_operation("test_operation")
        def slow_operation():
            time.sleep(0.1)
            return "result"
        
        # Run operation multiple times
        for _ in range(3):
            result = slow_operation()
            assert result == "result"
        
        # Get performance stats
        stats = tracker.get_performance_stats("test_operation")
        
        assert stats['count'] == 3
        assert stats['avg_time'] >= 0.1
        assert stats['min_time'] >= 0.1
        assert stats['max_time'] >= 0.1
    
    def test_alert_checking(self, monitoring):
        """Test alert generation"""
        # Mock high CPU metrics
        with patch.object(monitoring.metrics_collector, 'get_recent_metrics') as mock_metrics:
            mock_metrics.return_value = [
                {'name': 'system.cpu.usage', 'value': 85} for _ in range(10)
            ]
            
            alerts = monitoring.check_alerts()
            
            assert len(alerts) > 0
            assert any(a['type'] == 'high_cpu' for a in alerts)
    
    def test_dashboard_data(self, monitoring):
        """Test dashboard data generation"""
        # Log some events
        monitoring.event_logger.log_event("test", "Test event")
        
        # Get dashboard data
        dashboard = monitoring.get_dashboard_data()
        
        assert 'system_metrics' in dashboard
        assert 'recent_events' in dashboard
        assert 'event_stats' in dashboard
        assert 'performance_stats' in dashboard
        assert 'alerts' in dashboard
        assert 'timestamp' in dashboard

class TestCollaborationServer:
    """Test real-time collaboration server"""
    
    @pytest.fixture
    def server(self):
        """Create collaboration server"""
        return CollaborationServer()
    
    def test_user_registration(self, server):
        """Test user registration"""
        user = User(
            id="test_id",
            name="Test User",
            email="test@example.com",
            role="editor"
        )
        
        assert user.id == "test_id"
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == "editor"
        assert user.avatar is not None
    
    def test_workspace_creation(self, server):
        """Test workspace creation"""
        workspace = Workspace(
            id="workspace_1",
            name="Test Workspace",
            owner_id="user_1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            data={},
            active_users=set(),
            settings={}
        )
        
        assert workspace.id == "workspace_1"
        assert workspace.name == "Test Workspace"
        assert workspace.owner_id == "user_1"
        assert len(workspace.active_users) == 0
    
    def test_message_creation(self):
        """Test message creation"""
        message = Message(
            type="data_update",
            user_id="user_1",
            workspace_id="workspace_1",
            data={"test": "data"}
        )
        
        assert message.type == "data_update"
        assert message.user_id == "user_1"
        assert message.workspace_id == "workspace_1"
        assert message.data["test"] == "data"
        
        # Test JSON serialization
        json_str = message.to_json()
        data = json.loads(json_str)
        assert data['type'] == "data_update"

class TestAPIClient:
    """Test API client SDK"""
    
    @pytest.fixture
    def client(self):
        """Create API client"""
        return APIClient(base_url="http://localhost:5000")
    
    @patch('sdk.client.requests.Session')
    def test_authentication(self, mock_session):
        """Test authentication methods"""
        client = APIClient()
        mock_response = Mock()
        mock_response.json.return_value = {
            'token': 'test_token',
            'api_key': 'test_key',
            'user_id': 'user_123'
        }
        mock_response.raise_for_status = Mock()
        
        client.session.request = Mock(return_value=mock_response)
        
        # Test registration
        result = client.register('test@example.com', 'password123')
        
        assert result['token'] == 'test_token'
        assert client.token == 'test_token'
        assert client.session.headers['Authorization'] == 'Bearer test_token'
    
    @patch('sdk.client.requests.Session')
    def test_file_upload(self, mock_session):
        """Test file upload"""
        client = APIClient(api_key="test_key")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\n1,2\n3,4")
            temp_file = f.name
        
        try:
            mock_response = Mock()
            mock_response.json.return_value = {
                'session_id': 'session_123',
                'file_id': 'file_456'
            }
            mock_response.raise_for_status = Mock()
            
            client.session.request = Mock(return_value=mock_response)
            
            # Upload file
            result = client.upload_file(temp_file)
            
            assert result['session_id'] == 'session_123'
            assert result['file_id'] == 'file_456'
        
        finally:
            Path(temp_file).unlink()
    
    @patch('sdk.client.requests.Session')
    def test_dataframe_upload(self, mock_session):
        """Test DataFrame upload"""
        client = APIClient(api_key="test_key")
        
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'session_id': 'session_123'
        }
        mock_response.raise_for_status = Mock()
        
        client.session.request = Mock(return_value=mock_response)
        
        # Upload DataFrame
        result = client.upload_dataframe(df, "test.csv")
        
        assert result['session_id'] == 'session_123'
    
    @patch('sdk.client.requests.Session')
    def test_model_operations(self, mock_session):
        """Test model-related operations"""
        client = APIClient(api_key="test_key")
        
        # Mock list models
        mock_response = Mock()
        mock_response.json.return_value = {
            'models': [
                {'model_id': 'model_1', 'name': 'test_model'}
            ]
        }
        mock_response.raise_for_status = Mock()
        
        client.session.request = Mock(return_value=mock_response)
        
        # List models
        models = client.list_models()
        assert len(models) == 1
        assert models[0]['name'] == 'test_model'

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_model_training_workflow(self):
        """Test complete model training workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create registry and trainer
            registry = ModelRegistry(registry_path=tmpdir)
            trainer = ModelTrainer(registry)
            
            # Create sample data
            X = pd.DataFrame({
                'feature1': np.random.randn(100),
                'feature2': np.random.randn(100)
            })
            y = pd.Series(np.random.randint(0, 2, 100))
            
            # Train model
            model_id = trainer.train_model(
                X=X,
                y=y,
                model_type="classification",
                algorithm="auto",
                name="integration_test",
                version="1.0"
            )
            
            # Verify model was registered
            assert model_id in registry.models
            
            # Load and test model
            model = registry.load_model(model_id)
            predictions = model.predict(X[:10])
            assert len(predictions) == 10
            
            # Promote model
            registry.promote_model(model_id, "production")
            assert registry.models[model_id].status == "production"
            
            # Get production model
            prod_model = registry.get_production_model("integration_test")
            assert prod_model is not None
    
    def test_monitoring_workflow(self):
        """Test monitoring workflow"""
        monitoring = MonitoringSystem()
        
        # Start monitoring
        monitoring.start()
        
        try:
            # Log some events
            for i in range(5):
                monitoring.event_logger.log_event(
                    "analysis",
                    f"Analysis {i} completed",
                    metadata={'analysis_id': i}
                )
            
            # Track performance
            @monitoring.performance_tracker.track_operation("test_op")
            def operation():
                time.sleep(0.01)
                return "done"
            
            for _ in range(3):
                operation()
            
            # Get dashboard data
            dashboard = monitoring.get_dashboard_data()
            
            # Verify data
            assert len(dashboard['recent_events']) >= 5
            assert 'test_op' in dashboard['performance_stats']
            assert dashboard['performance_stats']['test_op']['count'] == 3
        
        finally:
            monitoring.stop()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])