"""
AI Manager Teammate
Responsible for generating and refining analysis plans
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AIManager:
    """AI Manager for plan generation and coordination"""
    
    def __init__(self, api_key: str = None):
        """Initialize AI Manager"""
        self.api_key = api_key or "AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8"
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.conversation_history = []
        
    def generate_analysis_plan(
        self, 
        objective: Dict[str, Any],
        files: Dict[str, List[Dict]],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive analysis plan based on objective and data"""
        
        # Build prompt with all context
        prompt = self._build_plan_prompt(objective, files, context)
        
        try:
            # Generate plan using Gemini
            response = self.model.generate_content(prompt)
            plan_text = response.text
            
            # Parse the plan into structured format
            plan = self._parse_plan(plan_text, objective, files)
            
            # Add metadata
            plan['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'generator': 'AI Manager',
                'confidence': 0.85,
                'estimated_duration': self._estimate_duration(plan)
            }
            
            # Store in history
            self.conversation_history.append({
                'role': 'manager',
                'content': f"Generated analysis plan for: {objective['objective'][:50]}...",
                'timestamp': datetime.now().isoformat()
            })
            
            return plan
            
        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            return self._generate_fallback_plan(objective, files)
    
    def _build_plan_prompt(
        self, 
        objective: Dict[str, Any],
        files: Dict[str, List[Dict]], 
        context: Optional[Dict]
    ) -> str:
        """Build comprehensive prompt for plan generation"""
        
        # Analyze files to understand data structure
        file_summary = self._summarize_files(files)
        
        prompt = f"""
You are an expert data analysis manager. Generate a comprehensive analysis plan based on the following:

**Business Objective:**
{objective['objective']}

**Analysis Type:** {objective['analysis_type']}

**Success Criteria:**
{objective.get('success_criteria', 'Not specified')}

**Available Data Files:**
{file_summary}

**Additional Context:**
{json.dumps(context, indent=2) if context else 'None provided'}

Please create a detailed analysis plan in YAML format with the following structure:

```yaml
analysis_plan:
  title: <concise title>
  objective_alignment: <score 0-1>
  methodology: <approach name>
  
  phases:
    - name: <phase name>
      description: <what this phase accomplishes>
      owner: <Associate AI|Analyst AI|Manager AI>
      tasks:
        - task_id: <unique id>
          name: <task name>
          type: <data_processing|analysis|visualization|modeling>
          description: <detailed description>
          inputs: [<required inputs>]
          outputs: [<expected outputs>]
          parameters:
            <key>: <value>
          estimated_time: <minutes>
          requires_human_review: <true|false>
    
  quality_gates:
    - after_phase: <phase name>
      criteria:
        - <validation criterion>
      minimum_score: <0-1>
  
  success_metrics:
    - metric: <metric name>
      target: <target value>
      measurement: <how to measure>
  
  risks:
    - risk: <risk description>
      mitigation: <mitigation strategy>
      impact: <low|medium|high>
```

Focus on creating actionable, specific tasks that directly address the business objective.
Consider the data types available and suggest appropriate analytical techniques.
"""
        
        return prompt
    
    def _summarize_files(self, files: Dict[str, List[Dict]]) -> str:
        """Summarize uploaded files for the prompt"""
        summary = []
        
        for category, file_list in files.items():
            if file_list:
                summary.append(f"\n{category.upper()} FILES:")
                for file in file_list:
                    meta = file.get('metadata', {})
                    if 'rows' in meta:
                        summary.append(f"  - {file['name']}: {meta['rows']} rows, {meta['columns']} columns")
                    elif 'pages' in meta:
                        summary.append(f"  - {file['name']}: {meta['pages']} pages document")
                    elif 'statements' in meta:
                        summary.append(f"  - {file['name']}: {meta['statements']} SQL statements")
                    else:
                        summary.append(f"  - {file['name']}")
        
        return '\n'.join(summary) if summary else "No files uploaded"
    
    def _parse_plan(
        self, 
        plan_text: str,
        objective: Dict[str, Any],
        files: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Parse AI-generated plan text into structured format"""
        
        # Try to extract YAML from response
        try:
            # Find YAML block in response
            import re
            yaml_match = re.search(r'```yaml\n(.*?)\n```', plan_text, re.DOTALL)
            
            if yaml_match:
                yaml_content = yaml_match.group(1)
                plan = yaml.safe_load(yaml_content)
                
                # Ensure required structure
                if 'analysis_plan' in plan:
                    return plan['analysis_plan']
                return plan
            else:
                # Try parsing entire response as YAML
                plan = yaml.safe_load(plan_text)
                if isinstance(plan, dict):
                    return plan
        except:
            pass
        
        # If parsing fails, create structured plan from text
        return self._create_structured_plan(plan_text, objective, files)
    
    def _create_structured_plan(
        self,
        plan_text: str,
        objective: Dict[str, Any],
        files: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Create structured plan when parsing fails"""
        
        analysis_type = objective['analysis_type']
        
        # Create default plan based on analysis type
        if analysis_type == 'predictive':
            return self._create_predictive_plan(objective, files)
        elif analysis_type == 'exploratory':
            return self._create_exploratory_plan(objective, files)
        elif analysis_type == 'diagnostic':
            return self._create_diagnostic_plan(objective, files)
        else:
            return self._create_descriptive_plan(objective, files)
    
    def _create_predictive_plan(
        self,
        objective: Dict[str, Any],
        files: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Create predictive analysis plan"""
        
        return {
            'title': 'Predictive Analysis Plan',
            'objective_alignment': 0.9,
            'methodology': 'machine_learning_pipeline',
            'phases': [
                {
                    'name': 'Data Preparation',
                    'description': 'Clean and prepare data for modeling',
                    'owner': 'Associate AI',
                    'tasks': [
                        {
                            'task_id': 'prep_001',
                            'name': 'Data Quality Assessment',
                            'type': 'data_processing',
                            'description': 'Assess data quality and identify issues',
                            'inputs': ['raw_data'],
                            'outputs': ['quality_report'],
                            'parameters': {
                                'check_missing': True,
                                'check_outliers': True,
                                'check_duplicates': True
                            },
                            'estimated_time': 5,
                            'requires_human_review': False
                        },
                        {
                            'task_id': 'prep_002',
                            'name': 'Feature Engineering',
                            'type': 'data_processing',
                            'description': 'Create relevant features for prediction',
                            'inputs': ['cleaned_data'],
                            'outputs': ['feature_matrix'],
                            'parameters': {
                                'encoding_method': 'target_encoding',
                                'scaling_method': 'standard'
                            },
                            'estimated_time': 10,
                            'requires_human_review': True
                        }
                    ]
                },
                {
                    'name': 'Model Development',
                    'description': 'Build and train predictive models',
                    'owner': 'Analyst AI',
                    'tasks': [
                        {
                            'task_id': 'model_001',
                            'name': 'Train Baseline Models',
                            'type': 'modeling',
                            'description': 'Train multiple baseline models',
                            'inputs': ['feature_matrix'],
                            'outputs': ['baseline_models', 'performance_metrics'],
                            'parameters': {
                                'algorithms': ['random_forest', 'xgboost', 'logistic_regression'],
                                'cross_validation': 5,
                                'metrics': ['accuracy', 'precision', 'recall', 'f1']
                            },
                            'estimated_time': 20,
                            'requires_human_review': False
                        },
                        {
                            'task_id': 'model_002',
                            'name': 'Hyperparameter Optimization',
                            'type': 'modeling',
                            'description': 'Optimize best model hyperparameters',
                            'inputs': ['best_baseline_model'],
                            'outputs': ['optimized_model'],
                            'parameters': {
                                'method': 'bayesian_optimization',
                                'n_iterations': 50
                            },
                            'estimated_time': 30,
                            'requires_human_review': True
                        }
                    ]
                },
                {
                    'name': 'Validation & Insights',
                    'description': 'Validate model and generate insights',
                    'owner': 'Analyst AI',
                    'tasks': [
                        {
                            'task_id': 'val_001',
                            'name': 'Model Validation',
                            'type': 'analysis',
                            'description': 'Validate model on test data',
                            'inputs': ['optimized_model', 'test_data'],
                            'outputs': ['validation_report'],
                            'parameters': {
                                'validation_methods': ['holdout', 'time_series_split']
                            },
                            'estimated_time': 15,
                            'requires_human_review': True
                        }
                    ]
                }
            ],
            'quality_gates': [
                {
                    'after_phase': 'Data Preparation',
                    'criteria': ['Data quality score > 0.8', 'No critical data issues'],
                    'minimum_score': 0.8
                },
                {
                    'after_phase': 'Model Development',
                    'criteria': ['Model performance meets targets', 'No overfitting detected'],
                    'minimum_score': 0.85
                }
            ],
            'success_metrics': [
                {
                    'metric': 'Model Accuracy',
                    'target': 0.85,
                    'measurement': 'Cross-validation score'
                },
                {
                    'metric': 'Business Impact',
                    'target': 'Reduce churn by 20%',
                    'measurement': 'Predicted vs actual outcomes'
                }
            ],
            'risks': [
                {
                    'risk': 'Insufficient data for training',
                    'mitigation': 'Use data augmentation techniques',
                    'impact': 'medium'
                },
                {
                    'risk': 'Model overfitting',
                    'mitigation': 'Apply regularization and cross-validation',
                    'impact': 'high'
                }
            ]
        }
    
    def _create_exploratory_plan(
        self,
        objective: Dict[str, Any],
        files: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Create exploratory analysis plan"""
        
        return {
            'title': 'Exploratory Data Analysis Plan',
            'objective_alignment': 0.85,
            'methodology': 'comprehensive_eda',
            'phases': [
                {
                    'name': 'Initial Data Exploration',
                    'description': 'Understand data structure and content',
                    'owner': 'Associate AI',
                    'tasks': [
                        {
                            'task_id': 'explore_001',
                            'name': 'Data Profiling',
                            'type': 'analysis',
                            'description': 'Profile all data attributes',
                            'inputs': ['raw_data'],
                            'outputs': ['data_profile'],
                            'parameters': {
                                'profile_depth': 'comprehensive'
                            },
                            'estimated_time': 10,
                            'requires_human_review': False
                        }
                    ]
                },
                {
                    'name': 'Pattern Discovery',
                    'description': 'Discover patterns and relationships',
                    'owner': 'Analyst AI',
                    'tasks': [
                        {
                            'task_id': 'pattern_001',
                            'name': 'Correlation Analysis',
                            'type': 'analysis',
                            'description': 'Analyze correlations between variables',
                            'inputs': ['cleaned_data'],
                            'outputs': ['correlation_matrix', 'insights'],
                            'parameters': {
                                'methods': ['pearson', 'spearman'],
                                'threshold': 0.3
                            },
                            'estimated_time': 15,
                            'requires_human_review': True
                        }
                    ]
                }
            ],
            'quality_gates': [],
            'success_metrics': [],
            'risks': []
        }
    
    def _create_diagnostic_plan(
        self,
        objective: Dict[str, Any],
        files: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Create diagnostic analysis plan"""
        
        return {
            'title': 'Diagnostic Analysis Plan',
            'objective_alignment': 0.88,
            'methodology': 'root_cause_analysis',
            'phases': [
                {
                    'name': 'Problem Definition',
                    'description': 'Define and scope the problem',
                    'owner': 'Manager AI',
                    'tasks': []
                }
            ],
            'quality_gates': [],
            'success_metrics': [],
            'risks': []
        }
    
    def _create_descriptive_plan(
        self,
        objective: Dict[str, Any],
        files: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Create descriptive analysis plan"""
        
        return {
            'title': 'Descriptive Analysis Plan',
            'objective_alignment': 0.82,
            'methodology': 'statistical_summary',
            'phases': [
                {
                    'name': 'Data Summarization',
                    'description': 'Summarize key metrics and statistics',
                    'owner': 'Associate AI',
                    'tasks': []
                }
            ],
            'quality_gates': [],
            'success_metrics': [],
            'risks': []
        }
    
    def _estimate_duration(self, plan: Dict[str, Any]) -> int:
        """Estimate total duration for the analysis plan"""
        
        total_minutes = 0
        for phase in plan.get('phases', []):
            for task in phase.get('tasks', []):
                total_minutes += task.get('estimated_time', 5)
        
        return total_minutes
    
    def _generate_fallback_plan(
        self,
        objective: Dict[str, Any],
        files: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Generate fallback plan if AI generation fails"""
        
        return {
            'title': 'Standard Analysis Plan',
            'objective_alignment': 0.7,
            'methodology': 'standard_pipeline',
            'phases': [
                {
                    'name': 'Data Understanding',
                    'description': 'Initial data exploration',
                    'owner': 'Associate AI',
                    'tasks': []
                },
                {
                    'name': 'Analysis',
                    'description': 'Core analysis tasks',
                    'owner': 'Analyst AI',
                    'tasks': []
                }
            ],
            'quality_gates': [],
            'success_metrics': [],
            'risks': [],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'Fallback Generator',
                'confidence': 0.5
            }
        }
    
    def refine_plan(self, plan: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Refine existing plan based on user feedback"""
        
        prompt = f"""
Refine the following analysis plan based on user feedback:

Current Plan:
{yaml.dump(plan, default_flow_style=False)}

User Feedback:
{feedback}

Please provide an updated plan that addresses the feedback while maintaining the same structure.
"""
        
        try:
            response = self.model.generate_content(prompt)
            refined_plan = self._parse_plan(response.text, plan, {})
            
            # Update metadata
            refined_plan['metadata']['refined_at'] = datetime.now().isoformat()
            refined_plan['metadata']['refinement_count'] = plan.get('metadata', {}).get('refinement_count', 0) + 1
            
            return refined_plan
            
        except Exception as e:
            logger.error(f"Error refining plan: {e}")
            return plan
    
    def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """Chat with the AI Manager about the analysis plan"""
        
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Build chat prompt with context
        prompt = f"""
You are the AI Manager helping with data analysis planning. 

Conversation history:
{self._format_conversation_history()}

Current context:
{json.dumps(context, indent=2) if context else 'No specific context'}

User message: {message}

Please provide a helpful, concise response. If asked about the plan, explain your reasoning.
If asked for changes, suggest specific modifications. Stay focused on data analysis planning.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Add response to history
            self.conversation_history.append({
                'role': 'manager',
                'content': response_text,
                'timestamp': datetime.now().isoformat()
            })
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "I apologize, but I'm having trouble processing your request. Could you please rephrase or try again?"
    
    def _format_conversation_history(self) -> str:
        """Format conversation history for prompt"""
        
        # Keep last 10 messages for context
        recent_history = self.conversation_history[-10:]
        
        formatted = []
        for msg in recent_history:
            role = msg['role'].upper()
            content = msg['content'][:200] + '...' if len(msg['content']) > 200 else msg['content']
            formatted.append(f"{role}: {content}")
        
        return '\n'.join(formatted)