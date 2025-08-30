"""
Report Generation and Results Aggregation System
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import base64
import io
from pathlib import Path

class ReportGenerator:
    """Generate executive reports from analysis results"""
    
    def __init__(self):
        self.report_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load report templates"""
        return {
            'executive_summary': {
                'sections': ['overview', 'key_findings', 'recommendations', 'next_steps'],
                'format': 'structured'
            },
            'detailed_analysis': {
                'sections': ['methodology', 'data_profile', 'analysis_results', 'visualizations', 'conclusions'],
                'format': 'comprehensive'
            },
            'team_performance': {
                'sections': ['metrics', 'task_completion', 'quality_scores', 'insights'],
                'format': 'metrics_focused'
            }
        }
    
    def aggregate_plan_results(self, plan: Dict, task_results: List[Dict]) -> Dict:
        """
        Aggregate results from multiple tasks in a plan
        
        Args:
            plan: Plan dictionary
            task_results: List of task result dictionaries
            
        Returns:
            Aggregated results dictionary
        """
        aggregated = {
            'plan_id': plan.get('id'),
            'plan_name': plan.get('name'),
            'objectives': plan.get('objectives', []),
            'total_tasks': len(task_results),
            'completed_tasks': len([r for r in task_results if r.get('status') == 'success']),
            'failed_tasks': len([r for r in task_results if r.get('status') == 'failed']),
            'aggregated_insights': [],
            'key_findings': [],
            'metrics_summary': {},
            'recommendations': [],
            'confidence_score': 0.0,
            'quality_score': 0.0,
            'execution_summary': {}
        }
        
        # Aggregate insights
        all_insights = []
        for result in task_results:
            if 'results' in result and isinstance(result['results'], dict):
                insights = result['results'].get('insights', [])
                all_insights.extend(insights)
        
        # Deduplicate and prioritize insights
        aggregated['aggregated_insights'] = self._prioritize_insights(all_insights)
        
        # Extract key findings
        aggregated['key_findings'] = self._extract_key_findings(task_results)
        
        # Aggregate metrics
        aggregated['metrics_summary'] = self._aggregate_metrics(task_results)
        
        # Generate recommendations
        aggregated['recommendations'] = self._generate_recommendations(
            plan['objectives'], 
            aggregated['key_findings'],
            aggregated['metrics_summary']
        )
        
        # Calculate overall scores
        confidence_scores = [r.get('confidence', 0) for r in task_results if 'confidence' in r]
        quality_scores = [r.get('quality_score', 0) for r in task_results if 'quality_score' in r]
        
        aggregated['confidence_score'] = np.mean(confidence_scores) if confidence_scores else 0
        aggregated['quality_score'] = np.mean(quality_scores) if quality_scores else 0
        
        # Execution summary
        total_time = sum([self._parse_execution_time(r.get('execution_time', '0')) 
                         for r in task_results])
        aggregated['execution_summary'] = {
            'total_execution_time': f"{total_time:.2f} seconds",
            'average_task_time': f"{total_time/len(task_results):.2f} seconds" if task_results else "0",
            'completion_rate': f"{aggregated['completed_tasks']/aggregated['total_tasks']*100:.1f}%" if aggregated['total_tasks'] > 0 else "0%"
        }
        
        return aggregated
    
    def generate_executive_report(self, aggregated_results: Dict) -> Dict:
        """
        Generate executive summary report
        
        Args:
            aggregated_results: Aggregated results from plan execution
            
        Returns:
            Executive report dictionary
        """
        report = {
            'title': f"Executive Summary: {aggregated_results.get('plan_name', 'Analysis Plan')}",
            'generated_at': datetime.now().isoformat(),
            'sections': {}
        }
        
        # Overview Section
        report['sections']['overview'] = {
            'title': 'Overview',
            'content': f"""
This report summarizes the analysis conducted for: {aggregated_results.get('plan_name', 'Analysis Plan')}

**Objectives:**
{self._format_list(aggregated_results.get('objectives', []))}

**Execution Summary:**
- Total Tasks: {aggregated_results.get('total_tasks', 0)}
- Completed: {aggregated_results.get('completed_tasks', 0)}
- Success Rate: {aggregated_results['execution_summary'].get('completion_rate', '0%')}
- Total Time: {aggregated_results['execution_summary'].get('total_execution_time', 'N/A')}
- Confidence Score: {aggregated_results.get('confidence_score', 0)*100:.1f}%
- Quality Score: {aggregated_results.get('quality_score', 0)*100:.1f}%
            """
        }
        
        # Key Findings Section
        findings = aggregated_results.get('key_findings', [])
        if findings:
            report['sections']['key_findings'] = {
                'title': 'Key Findings',
                'content': self._format_findings(findings)
            }
        
        # Insights Section
        insights = aggregated_results.get('aggregated_insights', [])
        if insights:
            report['sections']['insights'] = {
                'title': 'Analysis Insights',
                'content': self._format_list(insights[:10])  # Top 10 insights
            }
        
        # Metrics Section
        metrics = aggregated_results.get('metrics_summary', {})
        if metrics:
            report['sections']['metrics'] = {
                'title': 'Key Metrics',
                'content': self._format_metrics(metrics)
            }
        
        # Recommendations Section
        recommendations = aggregated_results.get('recommendations', [])
        if recommendations:
            report['sections']['recommendations'] = {
                'title': 'Recommendations',
                'content': self._format_recommendations(recommendations)
            }
        
        # Next Steps
        report['sections']['next_steps'] = {
            'title': 'Suggested Next Steps',
            'content': self._generate_next_steps(aggregated_results)
        }
        
        return report
    
    def _prioritize_insights(self, insights: List[str]) -> List[str]:
        """Prioritize and deduplicate insights"""
        # Remove duplicates while preserving order
        seen = set()
        unique_insights = []
        for insight in insights:
            if insight not in seen:
                seen.add(insight)
                unique_insights.append(insight)
        
        # Prioritize by keywords
        priority_keywords = ['significant', 'critical', 'important', 'anomaly', 'trend', 'correlation']
        
        prioritized = []
        regular = []
        
        for insight in unique_insights:
            if any(keyword in insight.lower() for keyword in priority_keywords):
                prioritized.append(insight)
            else:
                regular.append(insight)
        
        return prioritized + regular
    
    def _extract_key_findings(self, task_results: List[Dict]) -> List[Dict]:
        """Extract key findings from task results"""
        findings = []
        
        for result in task_results:
            if result.get('status') != 'success':
                continue
            
            task_name = result.get('task_name', 'Unknown Task')
            task_type = result.get('task_type', 'analysis')
            
            if 'results' in result and isinstance(result['results'], dict):
                task_data = result['results']
                
                # Extract findings based on task type
                if 'high_correlations' in task_data or 'strong_correlations' in task_data:
                    corr_data = task_data.get('high_correlations') or task_data.get('strong_correlations', [])
                    if corr_data:
                        findings.append({
                            'type': 'correlation',
                            'title': 'Strong Correlations Detected',
                            'details': f"Found {len(corr_data)} strong correlations in the data",
                            'data': corr_data[:3]  # Top 3
                        })
                
                if 'total_anomalies' in task_data:
                    findings.append({
                        'type': 'anomaly',
                        'title': 'Anomalies Detected',
                        'details': f"Identified {task_data['total_anomalies']} anomalies ({task_data.get('anomaly_percentage', 0)}% of data)",
                        'importance': 'high'
                    })
                
                if 'trends' in task_data:
                    for col, trend in list(task_data['trends'].items())[:2]:
                        findings.append({
                            'type': 'trend',
                            'title': f'{col} Trend Analysis',
                            'details': f"{col} shows {trend['direction']} trend with slope {trend['slope']:.4f}",
                            'data': trend
                        })
                
                if 'n_clusters' in task_data:
                    findings.append({
                        'type': 'segmentation',
                        'title': 'Data Segmentation',
                        'details': f"Data successfully segmented into {task_data['n_clusters']} distinct clusters",
                        'data': task_data.get('cluster_stats')
                    })
                
                if 'metrics' in task_data and 'r2_score' in task_data['metrics']:
                    r2 = task_data['metrics']['r2_score']
                    findings.append({
                        'type': 'model',
                        'title': 'Predictive Model Performance',
                        'details': f"Model achieved R² score of {r2:.3f}",
                        'importance': 'high' if r2 > 0.7 else 'medium'
                    })
        
        return findings
    
    def _aggregate_metrics(self, task_results: List[Dict]) -> Dict:
        """Aggregate metrics from all tasks"""
        metrics = {
            'data_quality': {},
            'model_performance': {},
            'statistical_measures': {},
            'execution_metrics': {}
        }
        
        for result in task_results:
            if result.get('status') != 'success':
                continue
            
            if 'results' in result and isinstance(result['results'], dict):
                task_data = result['results']
                
                # Data quality metrics
                if 'missing_percentage' in task_data:
                    metrics['data_quality']['missing_data'] = task_data['missing_percentage']
                
                if 'duplicates' in task_data:
                    metrics['data_quality']['duplicate_rows'] = task_data['duplicates']
                
                # Model performance metrics
                if 'metrics' in task_data:
                    for key, value in task_data['metrics'].items():
                        metrics['model_performance'][key] = value
                
                # Statistical measures
                if 'statistics' in task_data:
                    metrics['statistical_measures'].update(task_data['statistics'])
        
        # Execution metrics
        metrics['execution_metrics'] = {
            'total_tasks': len(task_results),
            'successful_tasks': len([r for r in task_results if r.get('status') == 'success']),
            'average_confidence': np.mean([r.get('confidence', 0) for r in task_results]),
            'average_quality': np.mean([r.get('quality_score', 0) for r in task_results])
        }
        
        return metrics
    
    def _generate_recommendations(self, objectives: List[str], findings: List[Dict], metrics: Dict) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Check for data quality issues
        if 'data_quality' in metrics and metrics['data_quality']:
            missing_data = metrics['data_quality'].get('missing_data', {})
            if missing_data:
                high_missing = [col for col, pct in missing_data.items() if pct > 10]
                if high_missing:
                    recommendations.append(
                        f"Address data quality: {len(high_missing)} columns have >10% missing values. "
                        "Consider data imputation or collection improvements."
                    )
        
        # Model performance recommendations
        if 'model_performance' in metrics and metrics['model_performance']:
            r2 = metrics['model_performance'].get('r2_score', 0)
            if r2 < 0.5:
                recommendations.append(
                    "Model performance is suboptimal (R² < 0.5). Consider feature engineering, "
                    "collecting more data, or trying different algorithms."
                )
            elif r2 > 0.9:
                recommendations.append(
                    "Model shows very high performance (R² > 0.9). Verify for overfitting "
                    "with cross-validation before deployment."
                )
        
        # Anomaly recommendations
        anomaly_findings = [f for f in findings if f.get('type') == 'anomaly']
        if anomaly_findings:
            recommendations.append(
                "Anomalies detected in the data. Investigate these outliers to determine "
                "if they represent errors, fraud, or valuable edge cases."
            )
        
        # Correlation recommendations
        corr_findings = [f for f in findings if f.get('type') == 'correlation']
        if corr_findings:
            recommendations.append(
                "Strong correlations identified between variables. Consider these relationships "
                "for feature selection and predictive modeling."
            )
        
        # Trend recommendations
        trend_findings = [f for f in findings if f.get('type') == 'trend']
        if trend_findings:
            for trend in trend_findings[:2]:
                if 'increasing' in str(trend.get('details', '')):
                    recommendations.append(
                        f"Increasing trend detected. Plan for capacity/resource scaling if trend continues."
                    )
                elif 'decreasing' in str(trend.get('details', '')):
                    recommendations.append(
                        f"Decreasing trend detected. Investigate root causes and implement corrective actions."
                    )
        
        # Segmentation recommendations
        segment_findings = [f for f in findings if f.get('type') == 'segmentation']
        if segment_findings:
            recommendations.append(
                "Customer/data segments identified. Develop targeted strategies for each segment "
                "to maximize effectiveness."
            )
        
        # Default recommendations if none generated
        if not recommendations:
            recommendations.append("Continue monitoring key metrics and trends")
            recommendations.append("Schedule follow-up analysis in 30 days")
            recommendations.append("Share findings with stakeholders for feedback")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _generate_next_steps(self, results: Dict) -> str:
        """Generate suggested next steps"""
        next_steps = []
        
        # Based on confidence and quality scores
        confidence = results.get('confidence_score', 0)
        quality = results.get('quality_score', 0)
        
        if confidence < 0.7:
            next_steps.append("1. Validate results with additional data sources")
        
        if quality < 0.7:
            next_steps.append("2. Improve data quality and re-run analysis")
        
        # Based on findings
        if results.get('key_findings'):
            next_steps.append("3. Deep-dive analysis on key findings")
            next_steps.append("4. Present results to stakeholders")
        
        # Based on failed tasks
        failed = results.get('failed_tasks', 0)
        if failed > 0:
            next_steps.append(f"5. Investigate and retry {failed} failed tasks")
        
        # Default next steps
        if not next_steps:
            next_steps = [
                "1. Share report with team for review",
                "2. Schedule follow-up analysis",
                "3. Implement recommended actions",
                "4. Monitor key metrics"
            ]
        
        return '\n'.join(next_steps[:5])
    
    def _format_list(self, items: List[str]) -> str:
        """Format list of items as bullet points"""
        if not items:
            return "No items available"
        return '\n'.join([f"• {item}" for item in items])
    
    def _format_findings(self, findings: List[Dict]) -> str:
        """Format findings for report"""
        if not findings:
            return "No significant findings"
        
        formatted = []
        for i, finding in enumerate(findings[:5], 1):
            formatted.append(f"**{i}. {finding.get('title', 'Finding')}**")
            formatted.append(f"   {finding.get('details', '')}")
            if 'importance' in finding:
                formatted.append(f"   *Importance: {finding['importance']}*")
            formatted.append("")
        
        return '\n'.join(formatted)
    
    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics for report"""
        formatted = []
        
        for category, values in metrics.items():
            if values:
                formatted.append(f"**{category.replace('_', ' ').title()}:**")
                if isinstance(values, dict):
                    for key, value in list(values.items())[:5]:
                        if isinstance(value, (int, float)):
                            formatted.append(f"  • {key}: {value:.3f}" if isinstance(value, float) else f"  • {key}: {value}")
                        else:
                            formatted.append(f"  • {key}: {value}")
                formatted.append("")
        
        return '\n'.join(formatted)
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations for report"""
        if not recommendations:
            return "No specific recommendations at this time"
        
        formatted = []
        for i, rec in enumerate(recommendations, 1):
            formatted.append(f"**{i}.** {rec}")
        
        return '\n'.join(formatted)
    
    def _parse_execution_time(self, time_str: str) -> float:
        """Parse execution time string to float seconds"""
        try:
            # Extract number from strings like "2.3 seconds"
            if 'second' in time_str.lower():
                return float(time_str.split()[0])
            return 0.0
        except:
            return 0.0
    
    def export_report_to_html(self, report: Dict) -> str:
        """Export report to HTML format"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.get('title', 'Analysis Report')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #1f77b4; }}
        h2 {{ color: #333; border-bottom: 2px solid #1f77b4; padding-bottom: 5px; }}
        .metric {{ background: #f0f2f6; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .recommendation {{ background: #e8f4f8; padding: 10px; border-left: 4px solid #1f77b4; margin: 10px 0; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; color: #666; }}
    </style>
</head>
<body>
    <h1>{report.get('title', 'Analysis Report')}</h1>
    <p>Generated: {report.get('generated_at', datetime.now().isoformat())}</p>
"""
        
        for section_key, section in report.get('sections', {}).items():
            html += f"""
    <h2>{section.get('title', section_key)}</h2>
    <div>{section.get('content', '').replace('\n', '<br>')}</div>
"""
        
        html += """
    <div class="footer">
        <p>This report was automatically generated by the AI Data Analysis Platform</p>
    </div>
</body>
</html>
"""
        return html