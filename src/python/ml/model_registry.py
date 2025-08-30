#!/usr/bin/env python3
"""
Model Registry and Version Control System
Manages ML model lifecycle, versioning, and deployment
"""

import json
import pickle
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelMetadata:
    """Model metadata and versioning information"""
    model_id: str
    name: str
    version: str
    model_type: str  # regression, classification, clustering
    algorithm: str
    created_at: datetime
    updated_at: datetime
    author: str
    description: str
    tags: List[str]
    metrics: Dict[str, float]
    parameters: Dict[str, Any]
    feature_names: List[str]
    target_name: str
    training_data_hash: str
    file_path: str
    status: str  # draft, staging, production, archived
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModelMetadata':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class ModelRegistry:
    """Central registry for ML models"""
    
    def __init__(self, registry_path: str = "./model_registry"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        self.models_dir = self.registry_path / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.registry_path / "registry.json"
        self.models: Dict[str, ModelMetadata] = self._load_registry()
    
    def _load_registry(self) -> Dict[str, ModelMetadata]:
        """Load model registry from disk"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                return {
                    model_id: ModelMetadata.from_dict(meta)
                    for model_id, meta in data.items()
                }
        return {}
    
    def _save_registry(self):
        """Save registry to disk"""
        data = {
            model_id: meta.to_dict()
            for model_id, meta in self.models.items()
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_model_id(self, name: str, version: str) -> str:
        """Generate unique model ID"""
        base = f"{name}_{version}".lower().replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base}_{timestamp}"
    
    def _calculate_data_hash(self, X: Union[pd.DataFrame, np.ndarray]) -> str:
        """Calculate hash of training data for versioning"""
        if isinstance(X, pd.DataFrame):
            data_str = X.to_json()
        else:
            data_str = str(X.tolist())
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def register_model(
        self,
        model: BaseEstimator,
        name: str,
        version: str,
        X_train: Union[pd.DataFrame, np.ndarray],
        y_train: Union[pd.Series, np.ndarray],
        X_test: Optional[Union[pd.DataFrame, np.ndarray]] = None,
        y_test: Optional[Union[pd.Series, np.ndarray]] = None,
        model_type: str = "classification",
        author: str = "unknown",
        description: str = "",
        tags: List[str] = None,
        auto_evaluate: bool = True
    ) -> str:
        """Register a new model in the registry"""
        
        model_id = self._generate_model_id(name, version)
        
        # Get feature names
        if isinstance(X_train, pd.DataFrame):
            feature_names = X_train.columns.tolist()
        else:
            feature_names = [f"feature_{i}" for i in range(X_train.shape[1])]
        
        # Get target name
        if isinstance(y_train, pd.Series):
            target_name = y_train.name or "target"
        else:
            target_name = "target"
        
        # Calculate metrics if test data provided
        metrics = {}
        if auto_evaluate and X_test is not None and y_test is not None:
            metrics = self.evaluate_model(model, X_test, y_test, model_type)
        
        # Save model
        model_path = self.models_dir / f"{model_id}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Create metadata
        metadata = ModelMetadata(
            model_id=model_id,
            name=name,
            version=version,
            model_type=model_type,
            algorithm=type(model).__name__,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            author=author,
            description=description,
            tags=tags or [],
            metrics=metrics,
            parameters=model.get_params(),
            feature_names=feature_names,
            target_name=target_name,
            training_data_hash=self._calculate_data_hash(X_train),
            file_path=str(model_path),
            status="draft"
        )
        
        # Register model
        self.models[model_id] = metadata
        self._save_registry()
        
        logger.info(f"Model registered: {model_id}")
        return model_id
    
    def evaluate_model(
        self,
        model: BaseEstimator,
        X_test: Union[pd.DataFrame, np.ndarray],
        y_test: Union[pd.Series, np.ndarray],
        model_type: str = "classification"
    ) -> Dict[str, float]:
        """Evaluate model performance"""
        
        y_pred = model.predict(X_test)
        metrics = {}
        
        if model_type == "classification":
            metrics['accuracy'] = accuracy_score(y_test, y_pred)
            
            # Handle multiclass
            avg_method = 'weighted' if len(np.unique(y_test)) > 2 else 'binary'
            metrics['precision'] = precision_score(y_test, y_pred, average=avg_method)
            metrics['recall'] = recall_score(y_test, y_pred, average=avg_method)
            metrics['f1_score'] = f1_score(y_test, y_pred, average=avg_method)
            
        elif model_type == "regression":
            metrics['mse'] = mean_squared_error(y_test, y_pred)
            metrics['mae'] = mean_absolute_error(y_test, y_pred)
            metrics['rmse'] = np.sqrt(metrics['mse'])
            metrics['r2_score'] = r2_score(y_test, y_pred)
        
        return metrics
    
    def load_model(self, model_id: str) -> BaseEstimator:
        """Load model from registry"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found in registry")
        
        metadata = self.models[model_id]
        with open(metadata.file_path, 'rb') as f:
            return pickle.load(f)
    
    def get_model_metadata(self, model_id: str) -> ModelMetadata:
        """Get model metadata"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        return self.models[model_id]
    
    def list_models(
        self,
        name: Optional[str] = None,
        status: Optional[str] = None,
        model_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[ModelMetadata]:
        """List models with optional filtering"""
        
        models = list(self.models.values())
        
        if name:
            models = [m for m in models if name.lower() in m.name.lower()]
        
        if status:
            models = [m for m in models if m.status == status]
        
        if model_type:
            models = [m for m in models if m.model_type == model_type]
        
        if tags:
            models = [m for m in models if any(tag in m.tags for tag in tags)]
        
        # Sort by creation date (newest first)
        models.sort(key=lambda x: x.created_at, reverse=True)
        
        return models
    
    def promote_model(self, model_id: str, new_status: str) -> bool:
        """Promote model to new status (staging, production)"""
        if model_id not in self.models:
            return False
        
        valid_statuses = ['draft', 'staging', 'production', 'archived']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
        
        # If promoting to production, demote current production model
        if new_status == 'production':
            model_name = self.models[model_id].name
            for mid, meta in self.models.items():
                if meta.name == model_name and meta.status == 'production' and mid != model_id:
                    meta.status = 'archived'
                    meta.updated_at = datetime.now()
        
        self.models[model_id].status = new_status
        self.models[model_id].updated_at = datetime.now()
        self._save_registry()
        
        logger.info(f"Model {model_id} promoted to {new_status}")
        return True
    
    def get_production_model(self, name: str) -> Optional[BaseEstimator]:
        """Get current production model by name"""
        for model_id, meta in self.models.items():
            if meta.name == name and meta.status == 'production':
                return self.load_model(model_id)
        return None
    
    def compare_models(
        self,
        model_ids: List[str],
        X_test: Union[pd.DataFrame, np.ndarray],
        y_test: Union[pd.Series, np.ndarray]
    ) -> pd.DataFrame:
        """Compare multiple models on same test data"""
        
        results = []
        
        for model_id in model_ids:
            if model_id not in self.models:
                continue
            
            metadata = self.models[model_id]
            model = self.load_model(model_id)
            
            # Evaluate
            metrics = self.evaluate_model(
                model, X_test, y_test, 
                metadata.model_type
            )
            
            results.append({
                'model_id': model_id,
                'name': metadata.name,
                'version': metadata.version,
                'algorithm': metadata.algorithm,
                'status': metadata.status,
                **metrics
            })
        
        return pd.DataFrame(results)
    
    def delete_model(self, model_id: str) -> bool:
        """Delete model from registry"""
        if model_id not in self.models:
            return False
        
        # Delete model file
        model_path = Path(self.models[model_id].file_path)
        if model_path.exists():
            model_path.unlink()
        
        # Remove from registry
        del self.models[model_id]
        self._save_registry()
        
        logger.info(f"Model {model_id} deleted")
        return True
    
    def export_model(
        self,
        model_id: str,
        export_path: str,
        include_metadata: bool = True
    ) -> str:
        """Export model with metadata"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        export_dir = Path(export_path) / model_id
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy model file
        metadata = self.models[model_id]
        model_src = Path(metadata.file_path)
        model_dst = export_dir / "model.pkl"
        shutil.copy2(model_src, model_dst)
        
        # Export metadata
        if include_metadata:
            meta_path = export_dir / "metadata.json"
            with open(meta_path, 'w') as f:
                json.dump(metadata.to_dict(), f, indent=2)
        
        # Create requirements file
        req_path = export_dir / "requirements.txt"
        with open(req_path, 'w') as f:
            f.write("scikit-learn>=1.0.0\n")
            f.write("pandas>=1.3.0\n")
            f.write("numpy>=1.21.0\n")
        
        # Create usage example
        usage_path = export_dir / "usage.py"
        with open(usage_path, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
\"\"\"
Usage example for model {model_id}
\"\"\"

import pickle
import pandas as pd

# Load model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Example prediction
# Replace with your actual data
X = pd.DataFrame({{
    # Add your features here
    {', '.join([f'"{feat}": [value]' for feat in metadata.feature_names[:3]])}
}})

predictions = model.predict(X)
print(f"Predictions: {{predictions}}")
""")
        
        logger.info(f"Model exported to {export_dir}")
        return str(export_dir)

class ModelTrainer:
    """Advanced model training with hyperparameter tuning"""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
    
    def train_model(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        model_type: str = "classification",
        algorithm: str = "auto",
        name: str = "model",
        version: str = "1.0",
        test_size: float = 0.2,
        cv_folds: int = 5,
        auto_tune: bool = True,
        **kwargs
    ) -> str:
        """Train and register a model with automatic tuning"""
        
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.linear_model import LogisticRegression, LinearRegression
        from sklearn.svm import SVC, SVR
        from sklearn.model_selection import GridSearchCV
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Select algorithm
        if algorithm == "auto":
            if model_type == "classification":
                models = {
                    'rf': RandomForestClassifier(random_state=42),
                    'lr': LogisticRegression(random_state=42, max_iter=1000),
                    'svm': SVC(random_state=42)
                }
            else:
                models = {
                    'rf': RandomForestRegressor(random_state=42),
                    'lr': LinearRegression(),
                    'svr': SVR()
                }
            
            # Train all models and select best
            best_score = -float('inf')
            best_model = None
            best_algo = None
            
            for algo, model in models.items():
                try:
                    model.fit(X_train, y_train)
                    score = model.score(X_test, y_test)
                    
                    if score > best_score:
                        best_score = score
                        best_model = model
                        best_algo = algo
                    
                    logger.info(f"{algo}: score = {score:.4f}")
                except Exception as e:
                    logger.warning(f"Failed to train {algo}: {e}")
            
            model = best_model
            algorithm = best_algo
        else:
            # Use specified algorithm
            if model_type == "classification":
                if algorithm == "rf":
                    model = RandomForestClassifier(random_state=42)
                elif algorithm == "lr":
                    model = LogisticRegression(random_state=42, max_iter=1000)
                else:
                    model = SVC(random_state=42)
            else:
                if algorithm == "rf":
                    model = RandomForestRegressor(random_state=42)
                elif algorithm == "lr":
                    model = LinearRegression()
                else:
                    model = SVR()
            
            # Hyperparameter tuning
            if auto_tune and algorithm == "rf":
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20],
                    'min_samples_split': [2, 5]
                }
                
                grid_search = GridSearchCV(
                    model, param_grid, cv=cv_folds,
                    scoring='accuracy' if model_type == 'classification' else 'r2',
                    n_jobs=-1
                )
                
                grid_search.fit(X_train, y_train)
                model = grid_search.best_estimator_
                logger.info(f"Best params: {grid_search.best_params_}")
            else:
                model.fit(X_train, y_train)
        
        # Register model
        model_id = self.registry.register_model(
            model=model,
            name=name,
            version=version,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            model_type=model_type,
            author=kwargs.get('author', 'auto-trainer'),
            description=kwargs.get('description', f'Auto-trained {algorithm} model'),
            tags=kwargs.get('tags', ['auto-trained', algorithm])
        )
        
        return model_id