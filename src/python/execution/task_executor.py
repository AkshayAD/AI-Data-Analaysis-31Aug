"""
Task Execution Engine - Connects tasks to actual analysis agents
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime
import traceback
import io
import base64
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskExecutor:
    """Executes analysis tasks using appropriate agents"""
    
    def __init__(self):
        self.agents = self._initialize_agents()
        
    def _initialize_agents(self) -> Dict:
        """Initialize available analysis agents"""
        try:
            from agents.data_analysis_agents import (
                DataCleaningAgent, StatisticalAnalysisAgent,
                VisualizationAgent, MLAnalysisAgent
            )
            
            return {
                'data_profiling': DataCleaningAgent(),
                'statistical_analysis': StatisticalAnalysisAgent(),
                'visualization': VisualizationAgent(),
                'predictive_modeling': MLAnalysisAgent(),
                'anomaly_detection': MLAnalysisAgent(),
                'segmentation': MLAnalysisAgent(),
                'correlation_analysis': StatisticalAnalysisAgent(),
                'time_series': StatisticalAnalysisAgent()
            }
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            return {}
    
    def execute_task(self, task: Dict, data: pd.DataFrame = None) -> Dict:
        """
        Execute a single analysis task
        
        Args:
            task: Task dictionary with type, parameters, etc.
            data: DataFrame to analyze
            
        Returns:
            Results dictionary with status, outputs, insights
        """
        start_time = datetime.now()
        
        try:
            task_type = task.get('type', 'unknown')
            logger.info(f"Executing task: {task.get('name')} (type: {task_type})")
            
            # Get appropriate agent
            agent = self.agents.get(task_type)
            
            if not agent:
                logger.warning(f"No agent for task type: {task_type}, using fallback")
                return self._execute_fallback(task, data)
            
            # Execute based on task type
            if task_type == 'data_profiling':
                results = self._profile_data(data)
            elif task_type == 'statistical_analysis':
                results = self._statistical_analysis(data)
            elif task_type == 'correlation_analysis':
                results = self._correlation_analysis(data)
            elif task_type == 'time_series':
                results = self._time_series_analysis(data)
            elif task_type == 'predictive_modeling':
                results = self._predictive_modeling(data)
            elif task_type == 'anomaly_detection':
                results = self._anomaly_detection(data)
            elif task_type == 'segmentation':
                results = self._segmentation(data)
            elif task_type == 'visualization':
                results = self._create_visualizations(data)
            else:
                results = self._execute_fallback(task, data)
            
            # Add metadata
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'status': 'success',
                'task_id': task.get('id'),
                'task_name': task.get('name'),
                'task_type': task_type,
                'execution_time': f"{execution_time:.2f} seconds",
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'confidence': self._calculate_confidence(results),
                'quality_score': self._calculate_quality(results)
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}\n{traceback.format_exc()}")
            return {
                'status': 'failed',
                'task_id': task.get('id'),
                'task_name': task.get('name'),
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _profile_data(self, data: pd.DataFrame) -> Dict:
        """Profile data quality and characteristics"""
        if data is None or data.empty:
            return {'error': 'No data provided'}
        
        profile = {
            'shape': {'rows': len(data), 'columns': len(data.columns)},
            'columns': list(data.columns),
            'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
            'missing_values': data.isnull().sum().to_dict(),
            'missing_percentage': (data.isnull().sum() / len(data) * 100).round(2).to_dict(),
            'duplicates': len(data[data.duplicated()]),
            'memory_usage': f"{data.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            'insights': []
        }
        
        # Numeric columns statistics
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            profile['numeric_stats'] = {}
            for col in numeric_cols:
                profile['numeric_stats'][col] = {
                    'mean': float(data[col].mean()),
                    'median': float(data[col].median()),
                    'std': float(data[col].std()),
                    'min': float(data[col].min()),
                    'max': float(data[col].max()),
                    'q25': float(data[col].quantile(0.25)),
                    'q75': float(data[col].quantile(0.75))
                }
        
        # Generate insights
        total_missing = data.isnull().sum().sum()
        if total_missing > 0:
            profile['insights'].append(f"Found {total_missing} missing values across {data.isnull().any().sum()} columns")
        
        if profile['duplicates'] > 0:
            profile['insights'].append(f"Found {profile['duplicates']} duplicate rows")
        
        # Check for potential issues
        for col in numeric_cols:
            if data[col].std() == 0:
                profile['insights'].append(f"Column '{col}' has no variation (constant values)")
            
            # Check for outliers using IQR
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = len(data[(data[col] < Q1 - 1.5 * IQR) | (data[col] > Q3 + 1.5 * IQR)])
            if outliers > 0:
                profile['insights'].append(f"Column '{col}' has {outliers} potential outliers")
        
        return profile
    
    def _statistical_analysis(self, data: pd.DataFrame) -> Dict:
        """Perform statistical analysis"""
        if data is None or data.empty:
            return {'error': 'No data provided'}
        
        results = {'insights': [], 'statistics': {}}
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) >= 2:
            # Correlation analysis
            corr_matrix = data[numeric_cols].corr()
            high_corr = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        high_corr.append({
                            'var1': corr_matrix.columns[i],
                            'var2': corr_matrix.columns[j],
                            'correlation': round(corr_val, 3)
                        })
            
            results['high_correlations'] = high_corr
            
            if high_corr:
                results['insights'].append(f"Found {len(high_corr)} high correlations (|r| > 0.7)")
        
        # Distribution tests
        for col in numeric_cols[:5]:  # Limit to first 5 columns
            from scipy import stats
            
            # Normality test
            if len(data[col].dropna()) > 3:
                statistic, p_value = stats.normaltest(data[col].dropna())
                results['statistics'][col] = {
                    'normality_test': {
                        'statistic': float(statistic),
                        'p_value': float(p_value),
                        'is_normal': p_value > 0.05
                    }
                }
                
                if p_value < 0.05:
                    results['insights'].append(f"Column '{col}' is not normally distributed (p={p_value:.4f})")
        
        return results
    
    def _correlation_analysis(self, data: pd.DataFrame) -> Dict:
        """Analyze correlations in the data"""
        if data is None or data.empty:
            return {'error': 'No data provided'}
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for correlation analysis'}
        
        corr_matrix = data[numeric_cols].corr()
        
        results = {
            'correlation_matrix': corr_matrix.to_dict(),
            'insights': [],
            'strong_correlations': [],
            'weak_correlations': []
        }
        
        # Find strong and weak correlations
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                pair = {
                    'var1': corr_matrix.columns[i],
                    'var2': corr_matrix.columns[j],
                    'correlation': round(corr_val, 3)
                }
                
                if abs(corr_val) > 0.7:
                    results['strong_correlations'].append(pair)
                elif abs(corr_val) < 0.3:
                    results['weak_correlations'].append(pair)
        
        # Generate insights
        if results['strong_correlations']:
            results['insights'].append(f"Found {len(results['strong_correlations'])} strong correlations")
            
        if results['weak_correlations']:
            results['insights'].append(f"Found {len(results['weak_correlations'])} weak correlations")
        
        # Find the strongest correlation
        if results['strong_correlations']:
            strongest = max(results['strong_correlations'], key=lambda x: abs(x['correlation']))
            results['insights'].append(
                f"Strongest correlation: {strongest['var1']} and {strongest['var2']} (r={strongest['correlation']})"
            )
        
        return results
    
    def _time_series_analysis(self, data: pd.DataFrame) -> Dict:
        """Analyze time series data"""
        if data is None or data.empty:
            return {'error': 'No data provided'}
        
        results = {'insights': [], 'trends': {}}
        
        # Look for date columns
        date_cols = []
        for col in data.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    data[col] = pd.to_datetime(data[col])
                    date_cols.append(col)
                except:
                    pass
        
        if not date_cols:
            # Try to parse the first column as date
            try:
                data.iloc[:, 0] = pd.to_datetime(data.iloc[:, 0])
                date_cols = [data.columns[0]]
            except:
                return {'error': 'No time/date column found for time series analysis'}
        
        # Use first date column
        date_col = date_cols[0]
        data = data.sort_values(by=date_col)
        
        # Analyze numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
            # Calculate trend
            y = data[col].values
            x = np.arange(len(y))
            
            # Simple linear regression for trend
            coeffs = np.polyfit(x, y, 1)
            trend_direction = "increasing" if coeffs[0] > 0 else "decreasing"
            
            results['trends'][col] = {
                'direction': trend_direction,
                'slope': float(coeffs[0]),
                'mean': float(np.mean(y)),
                'std': float(np.std(y))
            }
            
            results['insights'].append(f"{col} shows {trend_direction} trend (slope={coeffs[0]:.4f})")
            
            # Check for seasonality (simple check)
            if len(y) > 12:
                # Compare first half vs second half
                first_half_mean = np.mean(y[:len(y)//2])
                second_half_mean = np.mean(y[len(y)//2:])
                change_pct = ((second_half_mean - first_half_mean) / first_half_mean) * 100
                
                if abs(change_pct) > 10:
                    direction = "increased" if change_pct > 0 else "decreased"
                    results['insights'].append(
                        f"{col} {direction} by {abs(change_pct):.1f}% from first to second half"
                    )
        
        return results
    
    def _predictive_modeling(self, data: pd.DataFrame) -> Dict:
        """Build predictive models"""
        if data is None or data.empty:
            return {'error': 'No data provided'}
        
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import r2_score, mean_squared_error
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) < 2:
                return {'error': 'Need at least 2 numeric columns for predictive modeling'}
            
            # Use last numeric column as target
            target_col = numeric_cols[-1]
            feature_cols = numeric_cols[:-1]
            
            X = data[feature_cols].fillna(0)
            y = data[target_col].fillna(0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=5)
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Feature importance
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
            
            results = {
                'model_type': 'Random Forest Regressor',
                'target_variable': target_col,
                'features': list(feature_cols),
                'metrics': {
                    'r2_score': round(r2, 3),
                    'rmse': round(rmse, 3),
                    'train_size': len(X_train),
                    'test_size': len(X_test)
                },
                'feature_importance': {k: round(v, 3) for k, v in feature_importance.items()},
                'insights': [
                    f"Model R² score: {r2:.3f}",
                    f"Root Mean Squared Error: {rmse:.2f}",
                    f"Most important feature: {top_features[0][0]} ({top_features[0][1]:.3f})"
                ]
            }
            
            if r2 > 0.7:
                results['insights'].append("Model shows good predictive performance (R² > 0.7)")
            elif r2 > 0.5:
                results['insights'].append("Model shows moderate predictive performance")
            else:
                results['insights'].append("Model shows poor predictive performance - consider feature engineering")
            
            return results
            
        except Exception as e:
            return {'error': f'Predictive modeling failed: {str(e)}'}
    
    def _anomaly_detection(self, data: pd.DataFrame) -> Dict:
        """Detect anomalies in the data"""
        if data is None or data.empty:
            return {'error': 'No data provided'}
        
        try:
            from sklearn.ensemble import IsolationForest
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                return {'error': 'No numeric columns for anomaly detection'}
            
            X = data[numeric_cols].fillna(0)
            
            # Isolation Forest for anomaly detection
            clf = IsolationForest(contamination=0.1, random_state=42)
            predictions = clf.fit_predict(X)
            
            # Count anomalies
            n_anomalies = (predictions == -1).sum()
            anomaly_indices = np.where(predictions == -1)[0]
            
            results = {
                'total_anomalies': int(n_anomalies),
                'anomaly_percentage': round(n_anomalies / len(data) * 100, 2),
                'anomaly_indices': anomaly_indices[:10].tolist(),  # First 10 anomalies
                'insights': [
                    f"Detected {n_anomalies} anomalies ({n_anomalies/len(data)*100:.1f}% of data)"
                ]
            }
            
            if n_anomalies > 0:
                # Analyze anomaly characteristics
                anomaly_data = data.iloc[anomaly_indices[:10]]
                normal_data = data[predictions == 1]
                
                for col in numeric_cols[:3]:  # Check first 3 columns
                    anomaly_mean = anomaly_data[col].mean()
                    normal_mean = normal_data[col].mean()
                    
                    if abs(anomaly_mean - normal_mean) > normal_data[col].std():
                        results['insights'].append(
                            f"Anomalies show significant deviation in '{col}'"
                        )
            
            return results
            
        except Exception as e:
            return {'error': f'Anomaly detection failed: {str(e)}'}
    
    def _segmentation(self, data: pd.DataFrame) -> Dict:
        """Perform customer/data segmentation"""
        if data is None or data.empty:
            return {'error': 'No data provided'}
        
        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) < 2:
                return {'error': 'Need at least 2 numeric columns for segmentation'}
            
            X = data[numeric_cols].fillna(0)
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Determine optimal number of clusters (elbow method)
            max_clusters = min(8, len(data) // 10)
            inertias = []
            
            for k in range(2, max_clusters + 1):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(X_scaled)
                inertias.append(kmeans.inertia_)
            
            # Use 3 clusters as default (can be improved with elbow method)
            optimal_k = 3
            
            # Final clustering
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Analyze clusters
            cluster_stats = {}
            for i in range(optimal_k):
                cluster_data = data[clusters == i]
                cluster_stats[f'Cluster_{i}'] = {
                    'size': len(cluster_data),
                    'percentage': round(len(cluster_data) / len(data) * 100, 2),
                    'characteristics': {}
                }
                
                for col in numeric_cols[:3]:  # First 3 columns
                    cluster_stats[f'Cluster_{i}']['characteristics'][col] = {
                        'mean': round(cluster_data[col].mean(), 2),
                        'std': round(cluster_data[col].std(), 2)
                    }
            
            results = {
                'n_clusters': optimal_k,
                'cluster_stats': cluster_stats,
                'insights': [
                    f"Data segmented into {optimal_k} distinct clusters"
                ]
            }
            
            # Find largest and smallest clusters
            sizes = [(k, v['size']) for k, v in cluster_stats.items()]
            largest = max(sizes, key=lambda x: x[1])
            smallest = min(sizes, key=lambda x: x[1])
            
            results['insights'].append(
                f"Largest cluster: {largest[0]} with {largest[1]} items ({cluster_stats[largest[0]]['percentage']}%)"
            )
            results['insights'].append(
                f"Smallest cluster: {smallest[0]} with {smallest[1]} items ({cluster_stats[smallest[0]]['percentage']}%)"
            )
            
            return results
            
        except Exception as e:
            return {'error': f'Segmentation failed: {str(e)}'}
    
    def _create_visualizations(self, data: pd.DataFrame) -> Dict:
        """Create data visualizations"""
        if data is None or data.empty:
            return {'error': 'No data provided'}
        
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            visualizations = []
            insights = []
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            
            # Create correlation heatmap if enough numeric columns
            if len(numeric_cols) >= 2:
                plt.figure(figsize=(10, 8))
                corr_matrix = data[numeric_cols].corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
                plt.title('Correlation Heatmap')
                
                # Save to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.read()).decode()
                plt.close()
                
                visualizations.append({
                    'type': 'correlation_heatmap',
                    'image': img_base64
                })
                insights.append("Created correlation heatmap showing relationships between variables")
            
            # Create distribution plots for first 3 numeric columns
            for col in numeric_cols[:3]:
                plt.figure(figsize=(10, 6))
                
                # Subplot 1: Histogram
                plt.subplot(1, 2, 1)
                plt.hist(data[col].dropna(), bins=30, edgecolor='black', alpha=0.7)
                plt.xlabel(col)
                plt.ylabel('Frequency')
                plt.title(f'Distribution of {col}')
                
                # Subplot 2: Box plot
                plt.subplot(1, 2, 2)
                plt.boxplot(data[col].dropna())
                plt.ylabel(col)
                plt.title(f'Box Plot of {col}')
                
                # Save to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.read()).decode()
                plt.close()
                
                visualizations.append({
                    'type': f'distribution_{col}',
                    'image': img_base64
                })
            
            insights.append(f"Created distribution plots for {min(3, len(numeric_cols))} numeric columns")
            
            return {
                'visualizations': visualizations,
                'insights': insights,
                'n_visualizations': len(visualizations)
            }
            
        except Exception as e:
            return {'error': f'Visualization creation failed: {str(e)}'}
    
    def _execute_fallback(self, task: Dict, data: pd.DataFrame) -> Dict:
        """Fallback execution for unknown task types"""
        return {
            'message': f"Task type '{task.get('type')}' not fully implemented",
            'data_shape': data.shape if data is not None else None,
            'insights': ['Using fallback execution - results may be limited']
        }
    
    def _calculate_confidence(self, results: Dict) -> float:
        """Calculate confidence score for results"""
        if 'error' in results:
            return 0.0
        
        # Base confidence
        confidence = 0.5
        
        # Increase confidence based on completeness
        if 'insights' in results and len(results.get('insights', [])) > 0:
            confidence += 0.2
        
        if 'metrics' in results or 'statistics' in results:
            confidence += 0.2
        
        if 'visualizations' in results or 'correlation_matrix' in results:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_quality(self, results: Dict) -> float:
        """Calculate quality score for results"""
        if 'error' in results:
            return 0.0
        
        quality = 0.0
        
        # Check for key components
        if 'insights' in results:
            quality += min(len(results['insights']) * 0.1, 0.3)
        
        if 'metrics' in results:
            quality += 0.25
        
        if 'statistics' in results:
            quality += 0.25
        
        if 'visualizations' in results:
            quality += 0.2
        
        return min(quality, 1.0)