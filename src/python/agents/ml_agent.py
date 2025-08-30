"""
Phase 2: Machine Learning Agent
Performs predictive analysis and model training
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json
import pickle

from .base import BaseAgent, AgentConfig


class MLAgent(BaseAgent):
    """Agent for machine learning tasks"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                name="MLAgent",
                description="Performs machine learning analysis"
            )
        super().__init__(config)
        self.models = {}
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ML task"""
        ml_task = task.get('ml_task', 'train')
        
        if ml_task == 'train':
            return self._train_model(task)
        elif ml_task == 'predict':
            return self._predict(task)
        elif ml_task == 'evaluate':
            return self._evaluate_model(task)
        elif ml_task == 'auto_ml':
            return self._auto_ml(task)
        else:
            return {'error': f'Unknown ML task: {ml_task}'}
    
    def _train_model(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Train a machine learning model"""
        try:
            # Import here to avoid dependency issues if not installed
            from sklearn.model_selection import train_test_split
            from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
            from sklearn.linear_model import LinearRegression, LogisticRegression
            from sklearn.metrics import mean_squared_error, accuracy_score, r2_score
            
            data_path = task.get('data_path')
            target_column = task.get('target_column')
            model_type = task.get('model_type', 'auto')
            task_type = task.get('task_type', 'auto')  # regression or classification
            
            if not data_path or not target_column:
                return {'error': 'data_path and target_column required'}
            
            # Load data
            df = pd.read_csv(data_path)
            
            if target_column not in df.columns:
                return {'error': f'Target column {target_column} not found'}
            
            # Prepare data
            X, y = self._prepare_data(df, target_column)
            
            # Determine task type if auto
            if task_type == 'auto':
                task_type = 'classification' if df[target_column].nunique() < 10 else 'regression'
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Select and train model
            if model_type == 'auto':
                if task_type == 'regression':
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                else:
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif model_type == 'linear':
                if task_type == 'regression':
                    model = LinearRegression()
                else:
                    model = LogisticRegression(max_iter=1000)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Train
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            
            if task_type == 'regression':
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                metrics = {'mse': float(mse), 'r2': float(r2)}
            else:
                accuracy = accuracy_score(y_test, y_pred)
                metrics = {'accuracy': float(accuracy)}
            
            # Store model
            model_id = f"{Path(data_path).stem}_{target_column}_{model_type}"
            self.models[model_id] = {
                'model': model,
                'feature_names': list(X.columns),
                'target_column': target_column,
                'task_type': task_type
            }
            
            # Feature importance for tree-based models
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                feature_importance = {
                    col: float(imp) 
                    for col, imp in zip(X.columns, importance)
                }
                feature_importance = dict(sorted(
                    feature_importance.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10])  # Top 10 features
            
            return {
                'success': True,
                'model_id': model_id,
                'task_type': task_type,
                'model_type': type(model).__name__,
                'metrics': metrics,
                'feature_importance': feature_importance,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except ImportError as e:
            return {'error': f'ML libraries not installed: {e}'}
        except Exception as e:
            self.logger.error(f"Model training failed: {e}")
            return {'error': str(e)}
    
    def _predict(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions using trained model"""
        try:
            model_id = task.get('model_id')
            data_path = task.get('data_path')
            
            if not model_id or model_id not in self.models:
                return {'error': f'Model {model_id} not found'}
            
            if not data_path:
                return {'error': 'data_path required for prediction'}
            
            # Load data
            df = pd.read_csv(data_path)
            model_info = self.models[model_id]
            model = model_info['model']
            feature_names = model_info['feature_names']
            
            # Prepare features
            X = df[feature_names].fillna(0)
            
            # Predict
            predictions = model.predict(X)
            
            # Add predictions to dataframe
            df['prediction'] = predictions
            
            # Save results
            output_path = task.get('output_path', f'/tmp/predictions_{model_id}.csv')
            df.to_csv(output_path, index=False)
            
            return {
                'success': True,
                'predictions_count': len(predictions),
                'output_path': output_path,
                'sample_predictions': predictions[:10].tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return {'error': str(e)}
    
    def _evaluate_model(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate model performance"""
        try:
            from sklearn.metrics import classification_report, confusion_matrix
            
            model_id = task.get('model_id')
            data_path = task.get('data_path')
            
            if not model_id or model_id not in self.models:
                return {'error': f'Model {model_id} not found'}
            
            if not data_path:
                return {'error': 'data_path required for evaluation'}
            
            # Load data
            df = pd.read_csv(data_path)
            model_info = self.models[model_id]
            model = model_info['model']
            feature_names = model_info['feature_names']
            target_column = model_info['target_column']
            task_type = model_info['task_type']
            
            if target_column not in df.columns:
                return {'error': f'Target column {target_column} not found'}
            
            # Prepare data
            X = df[feature_names].fillna(0)
            y = df[target_column]
            
            # Predict
            y_pred = model.predict(X)
            
            # Calculate metrics
            if task_type == 'classification':
                report = classification_report(y, y_pred, output_dict=True)
                cm = confusion_matrix(y, y_pred)
                
                return {
                    'success': True,
                    'task_type': 'classification',
                    'classification_report': report,
                    'confusion_matrix': cm.tolist()
                }
            else:
                from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
                
                mae = mean_absolute_error(y, y_pred)
                mse = mean_squared_error(y, y_pred)
                r2 = r2_score(y, y_pred)
                
                return {
                    'success': True,
                    'task_type': 'regression',
                    'metrics': {
                        'mae': float(mae),
                        'mse': float(mse),
                        'r2': float(r2)
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Model evaluation failed: {e}")
            return {'error': str(e)}
    
    def _auto_ml(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Automated machine learning - try multiple models"""
        try:
            from sklearn.model_selection import cross_val_score
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.linear_model import LinearRegression, Ridge
            
            data_path = task.get('data_path')
            target_column = task.get('target_column')
            
            if not data_path or not target_column:
                return {'error': 'data_path and target_column required'}
            
            # Load and prepare data
            df = pd.read_csv(data_path)
            X, y = self._prepare_data(df, target_column)
            
            # Try multiple models
            models = {
                'LinearRegression': LinearRegression(),
                'Ridge': Ridge(),
                'RandomForest': RandomForestRegressor(n_estimators=50, random_state=42),
                'GradientBoosting': GradientBoostingRegressor(n_estimators=50, random_state=42)
            }
            
            results = {}
            best_score = -float('inf')
            best_model = None
            
            for name, model in models.items():
                try:
                    scores = cross_val_score(model, X, y, cv=5, scoring='r2')
                    mean_score = float(scores.mean())
                    std_score = float(scores.std())
                    
                    results[name] = {
                        'mean_r2': mean_score,
                        'std_r2': std_score
                    }
                    
                    if mean_score > best_score:
                        best_score = mean_score
                        best_model = name
                        
                except Exception as e:
                    results[name] = {'error': str(e)}
            
            return {
                'success': True,
                'models_tested': len(models),
                'results': results,
                'best_model': best_model,
                'best_score': best_score
            }
            
        except ImportError as e:
            return {'error': f'ML libraries not installed: {e}'}
        except Exception as e:
            self.logger.error(f"AutoML failed: {e}")
            return {'error': str(e)}
    
    def _prepare_data(self, df: pd.DataFrame, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for ML"""
        # Select numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove target from features
        if target_column in numeric_cols:
            numeric_cols.remove(target_column)
        
        # Prepare X and y
        X = df[numeric_cols].fillna(0)
        y = df[target_column]
        
        return X, y
    
    def save_model(self, model_id: str, filepath: Path):
        """Save a trained model to file"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.models[model_id], f)
    
    def load_model(self, model_id: str, filepath: Path):
        """Load a model from file"""
        with open(filepath, 'rb') as f:
            self.models[model_id] = pickle.load(f)