"""
Intelligent Agent with LLM capabilities
Uses Gemini for enhanced analysis while minimizing API costs
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
import json

from .base import BaseAgent, AgentConfig
from llm import GeminiClient, LLMConfig


class IntelligentAgent(BaseAgent):
    """
    Agent that uses LLM for intelligent analysis
    Designed to minimize API calls through caching and smart fallbacks
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, api_key: Optional[str] = None):
        if config is None:
            config = AgentConfig(
                name="IntelligentAgent",
                description="LLM-enhanced analysis agent"
            )
        super().__init__(config)
        
        # Initialize LLM client
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key
            llm_config = LLMConfig(api_key=api_key)
        else:
            # Will try to use environment variable
            llm_config = None
        
        self.llm = GeminiClient(llm_config)
        self.llm_enabled = self.llm.enabled
        
        if self.llm_enabled:
            self.logger.info("LLM capabilities enabled (Gemini 2.5 Flash)")
        else:
            self.logger.info("Running without LLM - using rule-based analysis")
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intelligent analysis task"""
        task_type = task.get('type', 'smart_analysis')
        
        if task_type == 'smart_analysis':
            return self._smart_analysis(task)
        elif task_type == 'explain_results':
            return self._explain_results(task)
        elif task_type == 'suggest_next_steps':
            return self._suggest_next_steps(task)
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    def _smart_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform intelligent analysis using LLM when beneficial
        Falls back to rule-based analysis to save API costs
        """
        data_path = task.get('data_path')
        if not data_path:
            return {'error': 'No data_path provided'}
        
        try:
            # Load data
            df = pd.read_csv(data_path)
            
            # Basic analysis (no API calls)
            basic_stats = {
                'rows': len(df),
                'columns': len(df.columns),
                'numeric_columns': len(df.select_dtypes(include=['number']).columns),
                'missing_values': df.isnull().sum().sum()
            }
            
            # Determine if LLM analysis would be valuable
            use_llm = (
                self.llm_enabled and 
                len(df) > 10 and  # Enough data to analyze
                len(df.columns) < 20  # Not too complex
            )
            
            insights = []
            recommendations = []
            
            if use_llm:
                # Create concise data description
                data_desc = self._create_data_description(df)
                
                # Get LLM analysis (cached)
                llm_result = self.llm.analyze_data(
                    data_desc,
                    analysis_type="exploratory"
                )
                
                if 'error' not in llm_result:
                    # Extract insights
                    if isinstance(llm_result, dict):
                        insights = llm_result.get('insights', [])
                        recommendations = llm_result.get('recommendations', [])
                    
                    # Generate additional insights
                    metrics = {
                        'mean_values': df.select_dtypes(include=['number']).mean().to_dict(),
                        'correlations': self._get_top_correlations(df)
                    }
                    
                    llm_insights = self.llm.generate_insights(metrics)
                    insights.extend(llm_insights)
            
            # Always add rule-based insights
            rule_insights = self._generate_rule_based_insights(df)
            insights.extend(rule_insights)
            
            # Get visualization suggestions
            viz_suggestions = []
            if use_llm:
                viz_suggestions = self.llm.suggest_visualizations(
                    list(df.columns),
                    {col: str(dtype) for col, dtype in df.dtypes.items()}
                )
            
            if not viz_suggestions:
                viz_suggestions = self._suggest_visualizations_fallback(df)
            
            return {
                'success': True,
                'basic_stats': basic_stats,
                'insights': insights[:5],  # Limit to top 5
                'recommendations': recommendations[:3],  # Limit to top 3
                'visualization_suggestions': viz_suggestions[:3],
                'llm_used': use_llm,
                'usage_stats': self.llm.get_usage_stats() if use_llm else None
            }
            
        except Exception as e:
            self.logger.error(f"Smart analysis failed: {e}")
            return {'error': str(e)}
    
    def _explain_results(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain analysis results in plain language
        Uses LLM only for complex results
        """
        results = task.get('results', {})
        
        if not results:
            return {'error': 'No results provided to explain'}
        
        # Simple explanation for basic results
        if len(str(results)) < 500:
            explanation = self._generate_simple_explanation(results)
            return {
                'success': True,
                'explanation': explanation,
                'llm_used': False
            }
        
        # Use LLM for complex results (if enabled)
        if self.llm_enabled:
            # Truncate results to save tokens
            results_str = json.dumps(results, indent=2)[:500]
            
            explanation = self.llm.analyze_data(
                f"Explain these results simply: {results_str}",
                analysis_type="explanation"
            )
            
            return {
                'success': True,
                'explanation': explanation.get('analysis', 'Results processed successfully'),
                'llm_used': True,
                'usage_stats': self.llm.get_usage_stats()
            }
        
        return {
            'success': True,
            'explanation': self._generate_simple_explanation(results),
            'llm_used': False
        }
    
    def _suggest_next_steps(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest next steps based on current analysis
        Minimizes LLM usage through smart caching
        """
        current_state = task.get('current_state', {})
        
        # Generate suggestions based on state
        suggestions = []
        
        # Rule-based suggestions (no API calls)
        if 'data_analyzed' in current_state:
            suggestions.append("Consider creating visualizations to explore patterns")
        
        if 'model_trained' in current_state:
            model_metrics = current_state.get('model_metrics', {})
            if model_metrics.get('r2', 0) < 0.7:
                suggestions.append("Try feature engineering to improve model performance")
            else:
                suggestions.append("Model performs well - consider deployment")
        
        # Add LLM suggestions if valuable
        if self.llm_enabled and len(current_state) > 3:
            # Only call LLM for complex scenarios
            state_summary = json.dumps(current_state, indent=2)[:300]
            
            llm_suggestions = self.llm.generate_insights({
                'context': 'next_steps',
                'state': state_summary
            })
            
            suggestions.extend(llm_suggestions[:2])  # Limit LLM suggestions
        
        return {
            'success': True,
            'next_steps': suggestions[:5],
            'llm_used': self.llm_enabled and len(current_state) > 3,
            'usage_stats': self.llm.get_usage_stats() if self.llm_enabled else None
        }
    
    def _create_data_description(self, df: pd.DataFrame) -> str:
        """Create concise data description for LLM"""
        desc_parts = [
            f"Dataset with {len(df)} rows and {len(df.columns)} columns.",
            f"Columns: {', '.join(df.columns[:10])}",
            f"Data types: {df.dtypes.value_counts().to_dict()}",
            f"Missing values: {df.isnull().sum().sum()}"
        ]
        
        # Add sample statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns[:5]
        if len(numeric_cols) > 0:
            stats = df[numeric_cols].describe().loc[['mean', 'std']].to_dict()
            desc_parts.append(f"Key stats: {stats}")
        
        return " ".join(desc_parts)[:500]  # Limit length
    
    def _get_top_correlations(self, df: pd.DataFrame) -> Dict[str, float]:
        """Get top correlations from dataframe"""
        numeric_df = df.select_dtypes(include=['number'])
        if len(numeric_df.columns) < 2:
            return {}
        
        corr_matrix = numeric_df.corr()
        
        # Get top correlations (excluding diagonal)
        correlations = {}
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:  # Only strong correlations
                    correlations[f"{col1}-{col2}"] = round(corr_value, 3)
        
        # Return top 5
        return dict(sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)[:5])
    
    def _generate_rule_based_insights(self, df: pd.DataFrame) -> list:
        """Generate insights without using LLM"""
        insights = []
        
        # Check for missing data
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_pct > 10:
            insights.append(f"High missing data rate ({missing_pct:.1f}%) may affect analysis quality")
        
        # Check for outliers in numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols[:3]:  # Check first 3 columns
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > len(df) * 0.05:
                insights.append(f"Column '{col}' has {outliers} potential outliers")
        
        # Check data balance
        if len(df.columns) > len(df) * 0.5:
            insights.append("More features than samples - consider dimensionality reduction")
        
        return insights
    
    def _suggest_visualizations_fallback(self, df: pd.DataFrame) -> list:
        """Suggest visualizations without LLM"""
        suggestions = []
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        if len(numeric_cols) >= 2:
            suggestions.append({
                "type": "correlation_heatmap",
                "reason": "Visualize relationships between numeric variables"
            })
        
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            suggestions.append({
                "type": "box_plot",
                "reason": "Compare distributions across categories"
            })
        
        if len(numeric_cols) > 0:
            suggestions.append({
                "type": "histogram",
                "reason": "Understand data distribution"
            })
        
        return suggestions
    
    def _generate_simple_explanation(self, results: Dict) -> str:
        """Generate simple explanation without LLM"""
        parts = []
        
        if 'shape' in results:
            parts.append(f"Data has {results['shape'][0]} rows and {results['shape'][1]} columns.")
        
        if 'metrics' in results:
            metrics = results['metrics']
            if 'accuracy' in metrics:
                parts.append(f"Model accuracy: {metrics['accuracy']*100:.1f}%")
            if 'r2' in metrics:
                parts.append(f"Model R² score: {metrics['r2']:.3f}")
        
        if 'insights' in results:
            parts.append(f"Found {len(results['insights'])} key insights.")
        
        return " ".join(parts) if parts else "Analysis completed successfully."