import pandas as pd
import numpy as np
from typing import Any, Dict, Optional, List
from pathlib import Path

from .base import BaseAgent, AgentConfig


class DataAnalysisAgent(BaseAgent):
    """Simple agent for basic data analysis tasks"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                name="DataAnalysisAgent",
                description="Agent for basic data analysis"
            )
        super().__init__(config)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data analysis task"""
        task_type = task.get('type', 'analyze')
        
        if task_type == 'analyze':
            return self._analyze_data(task)
        elif task_type == 'summary':
            return self._summarize_data(task)
        elif task_type == 'clean':
            return self._clean_data(task)
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    def _analyze_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic data analysis"""
        data_path = task.get('data_path')
        if not data_path:
            return {'error': 'No data_path provided'}
        
        try:
            # Load data
            df = self._load_data(data_path)
            
            # Basic analysis
            analysis = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'missing_values': df.isnull().sum().to_dict(),
                'summary': {}
            }
            
            # Numeric columns summary
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis['summary'] = df[numeric_cols].describe().to_dict()
            
            return {'success': True, 'analysis': analysis}
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {'error': str(e)}
    
    def _summarize_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data summary"""
        data_path = task.get('data_path')
        if not data_path:
            return {'error': 'No data_path provided'}
        
        try:
            df = self._load_data(data_path)
            
            summary = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': float(df.memory_usage(deep=True).sum() / 1024**2),  # MB
                'column_types': {str(k): v for k, v in df.dtypes.value_counts().to_dict().items()}
            }
            
            return {'success': True, 'summary': summary}
            
        except Exception as e:
            self.logger.error(f"Summary failed: {e}")
            return {'error': str(e)}
    
    def _clean_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Basic data cleaning"""
        data_path = task.get('data_path')
        output_path = task.get('output_path')
        
        if not data_path:
            return {'error': 'No data_path provided'}
        
        try:
            df = self._load_data(data_path)
            original_shape = df.shape
            
            # Basic cleaning
            df = df.drop_duplicates()
            df = df.dropna(how='all')  # Remove completely empty rows
            
            cleaned_shape = df.shape
            
            # Save if output path provided
            if output_path:
                self._save_data(df, output_path)
            
            return {
                'success': True,
                'original_shape': original_shape,
                'cleaned_shape': cleaned_shape,
                'rows_removed': original_shape[0] - cleaned_shape[0]
            }
            
        except Exception as e:
            self.logger.error(f"Cleaning failed: {e}")
            return {'error': str(e)}
    
    def _load_data(self, path: str) -> pd.DataFrame:
        """Load data from various formats"""
        path = Path(path)
        
        if path.suffix == '.csv':
            return pd.read_csv(path)
        elif path.suffix in ['.xlsx', '.xls']:
            return pd.read_excel(path)
        elif path.suffix == '.json':
            return pd.read_json(path)
        elif path.suffix == '.parquet':
            return pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def _save_data(self, df: pd.DataFrame, path: str) -> None:
        """Save data to file"""
        path = Path(path)
        
        if path.suffix == '.csv':
            df.to_csv(path, index=False)
        elif path.suffix in ['.xlsx', '.xls']:
            df.to_excel(path, index=False)
        elif path.suffix == '.json':
            df.to_json(path, orient='records')
        elif path.suffix == '.parquet':
            df.to_parquet(path)
        else:
            # Default to CSV
            df.to_csv(path.with_suffix('.csv'), index=False)