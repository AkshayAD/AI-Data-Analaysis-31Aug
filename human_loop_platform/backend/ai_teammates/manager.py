"""
AI Manager with Real Gemini Integration
Handles actual AI-powered plan generation and analysis
"""

import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import pandas as pd
import numpy as np

class AIManager:
    """Real AI Manager using Gemini API"""
    
    def __init__(self):
        """Initialize AI Manager with API configuration"""
        self.api_key = st.session_state.get('gemini_api_key', '')
        self.model_name = st.session_state.get('gemini_model', 'gemini-2.5-flash')
        self.model = None
        
        if self.api_key:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            return True
        except Exception as e:
            st.error(f"Failed to initialize AI model: {str(e)}")
            return False
    
    def generate_analysis_plan(self, objective: Dict[str, Any], files: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """Generate a real analysis plan using Gemini"""
        if not self.model:
            if not self._initialize_model():
                return self._get_fallback_plan()
        
        try:
            # Construct detailed prompt
            prompt = self._construct_plan_prompt(objective, files, context)
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            plan = self._parse_plan_response(response.text, objective, files)
            
            return plan
            
        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")
            return self._get_fallback_plan()
    
    def _construct_plan_prompt(self, objective: Dict[str, Any], files: Dict[str, Any], context: Optional[str]) -> str:
        """Construct a detailed prompt for plan generation"""
        
        # Extract file information
        file_descriptions = []
        for filename, file_info in files.items():
            desc = f"- {filename}: {file_info.get('type', 'unknown')} with {file_info.get('rows', 0)} rows and {file_info.get('columns', 0)} columns"
            file_descriptions.append(desc)
        
        prompt = f"""
        You are an expert data analyst tasked with creating a comprehensive analysis plan.
        
        OBJECTIVE:
        {objective.get('objective', 'General data analysis')}
        
        ANALYSIS TYPE:
        {objective.get('analysis_type', 'exploratory')}
        
        SUCCESS CRITERIA:
        {objective.get('success_criteria', 'Provide actionable insights')}
        
        AVAILABLE DATA FILES:
        {chr(10).join(file_descriptions)}
        
        ADDITIONAL CONTEXT:
        {context if context else 'No additional context provided'}
        
        Please create a detailed analysis plan that includes:
        
        1. PHASES: Break down the analysis into logical phases
        2. TASKS: Specific tasks for each phase with clear deliverables
        3. METHODOLOGY: Analytical methods and techniques to use
        4. TIMELINE: Estimated time for each phase
        5. RISKS: Potential challenges and mitigation strategies
        6. SUCCESS METRICS: How to measure success
        
        Format your response as a structured JSON plan with the following structure:
        {{
            "title": "Analysis plan title",
            "objective_alignment": 0.0-1.0 score,
            "phases": [
                {{
                    "name": "Phase name",
                    "description": "Phase description",
                    "tasks": [
                        {{
                            "name": "Task name",
                            "description": "Task description",
                            "method": "Method to use",
                            "deliverable": "Expected output",
                            "estimated_hours": number
                        }}
                    ],
                    "dependencies": ["previous phase names"],
                    "estimated_days": number
                }}
            ],
            "methodology": {{
                "approach": "Overall approach",
                "techniques": ["List of techniques"],
                "tools": ["Recommended tools"]
            }},
            "risks": [
                {{
                    "risk": "Risk description",
                    "impact": "high/medium/low",
                    "mitigation": "Mitigation strategy"
                }}
            ],
            "success_metrics": ["List of success metrics"],
            "total_estimated_days": number,
            "confidence": 0.0-1.0 score
        }}
        
        Provide only the JSON response, no additional text.
        """
        
        return prompt
    
    def _parse_plan_response(self, response_text: str, objective: Dict, files: Dict) -> Dict[str, Any]:
        """Parse the Gemini response into a structured plan"""
        try:
            # Try to extract JSON from response
            import re
            
            # Find JSON content in response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group()
                plan = json.loads(json_str)
            else:
                # If no JSON found, create structured plan from text
                plan = self._structure_text_response(response_text, objective, files)
            
            # Add metadata
            plan['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'generator': self.model_name,
                'objective_hash': hash(str(objective)),
                'files_count': len(files)
            }
            
            return plan
            
        except Exception as e:
            st.warning(f"Could not parse AI response: {str(e)}")
            return self._get_fallback_plan()
    
    def _structure_text_response(self, text: str, objective: Dict, files: Dict) -> Dict[str, Any]:
        """Convert unstructured text response to structured plan"""
        lines = text.split('\n')
        
        plan = {
            "title": f"Analysis Plan for: {objective.get('objective', 'Data Analysis')[:50]}",
            "objective_alignment": 0.85,
            "phases": [],
            "methodology": {
                "approach": "Data-driven analysis",
                "techniques": [],
                "tools": ["Python", "Pandas", "Plotly"]
            },
            "risks": [],
            "success_metrics": [],
            "total_estimated_days": 5,
            "confidence": 0.75
        }
        
        # Parse lines to extract structure
        current_phase = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect phases
            if any(keyword in line.lower() for keyword in ['phase', 'step', 'stage']):
                if current_phase:
                    plan['phases'].append(current_phase)
                current_phase = {
                    "name": line,
                    "description": "",
                    "tasks": [],
                    "dependencies": [],
                    "estimated_days": 1
                }
            # Detect tasks
            elif current_phase and any(char in line for char in ['-', '•', '*']):
                task = {
                    "name": line.lstrip('-•* '),
                    "description": "",
                    "method": "Analysis",
                    "deliverable": "Results",
                    "estimated_hours": 2
                }
                current_phase['tasks'].append(task)
        
        # Add last phase
        if current_phase:
            plan['phases'].append(current_phase)
        
        # If no phases found, create default ones
        if not plan['phases']:
            plan['phases'] = self._get_default_phases(objective, files)
        
        return plan
    
    def _get_default_phases(self, objective: Dict, files: Dict) -> List[Dict]:
        """Get default phases based on objective and files"""
        analysis_type = objective.get('analysis_type', 'exploratory')
        
        phases = [
            {
                "name": "Data Understanding & Preparation",
                "description": "Load, explore, and prepare the data for analysis",
                "tasks": [
                    {
                        "name": "Data Loading",
                        "description": "Load all data files into analysis environment",
                        "method": "Pandas/Polars",
                        "deliverable": "Loaded dataframes",
                        "estimated_hours": 1
                    },
                    {
                        "name": "Data Profiling",
                        "description": "Generate statistical profiles of all datasets",
                        "method": "Automated profiling",
                        "deliverable": "Data quality report",
                        "estimated_hours": 2
                    },
                    {
                        "name": "Data Cleaning",
                        "description": "Handle missing values, outliers, and inconsistencies",
                        "method": "Statistical methods",
                        "deliverable": "Clean datasets",
                        "estimated_hours": 3
                    }
                ],
                "dependencies": [],
                "estimated_days": 1
            },
            {
                "name": "Exploratory Data Analysis",
                "description": "Explore patterns, relationships, and insights in the data",
                "tasks": [
                    {
                        "name": "Univariate Analysis",
                        "description": "Analyze individual variables",
                        "method": "Statistical analysis",
                        "deliverable": "Distribution insights",
                        "estimated_hours": 2
                    },
                    {
                        "name": "Bivariate Analysis",
                        "description": "Analyze relationships between variables",
                        "method": "Correlation analysis",
                        "deliverable": "Relationship matrix",
                        "estimated_hours": 3
                    },
                    {
                        "name": "Visualization",
                        "description": "Create insightful visualizations",
                        "method": "Plotly/Matplotlib",
                        "deliverable": "Interactive charts",
                        "estimated_hours": 3
                    }
                ],
                "dependencies": ["Data Understanding & Preparation"],
                "estimated_days": 1
            }
        ]
        
        # Add specific phases based on analysis type
        if analysis_type == 'predictive':
            phases.append({
                "name": "Predictive Modeling",
                "description": "Build and evaluate predictive models",
                "tasks": [
                    {
                        "name": "Feature Engineering",
                        "description": "Create and select features for modeling",
                        "method": "Domain expertise + automation",
                        "deliverable": "Feature set",
                        "estimated_hours": 4
                    },
                    {
                        "name": "Model Training",
                        "description": "Train multiple models and compare performance",
                        "method": "ML algorithms",
                        "deliverable": "Trained models",
                        "estimated_hours": 4
                    },
                    {
                        "name": "Model Evaluation",
                        "description": "Evaluate and select best model",
                        "method": "Cross-validation",
                        "deliverable": "Performance metrics",
                        "estimated_hours": 2
                    }
                ],
                "dependencies": ["Exploratory Data Analysis"],
                "estimated_days": 2
            })
        elif analysis_type == 'diagnostic':
            phases.append({
                "name": "Root Cause Analysis",
                "description": "Identify root causes of observed patterns",
                "tasks": [
                    {
                        "name": "Hypothesis Testing",
                        "description": "Test hypotheses about data patterns",
                        "method": "Statistical tests",
                        "deliverable": "Test results",
                        "estimated_hours": 3
                    },
                    {
                        "name": "Causal Analysis",
                        "description": "Identify causal relationships",
                        "method": "Causal inference",
                        "deliverable": "Causal graph",
                        "estimated_hours": 4
                    }
                ],
                "dependencies": ["Exploratory Data Analysis"],
                "estimated_days": 1
            })
        
        # Add final phase
        phases.append({
            "name": "Insights & Recommendations",
            "description": "Synthesize findings and provide recommendations",
            "tasks": [
                {
                    "name": "Insight Synthesis",
                    "description": "Combine all findings into coherent insights",
                    "method": "Analytical synthesis",
                    "deliverable": "Insight report",
                    "estimated_hours": 3
                },
                {
                    "name": "Recommendations",
                    "description": "Develop actionable recommendations",
                    "method": "Business analysis",
                    "deliverable": "Action plan",
                    "estimated_hours": 2
                },
                {
                    "name": "Report Generation",
                    "description": "Create comprehensive analysis report",
                    "method": "Automated reporting",
                    "deliverable": "Final report",
                    "estimated_hours": 2
                }
            ],
            "dependencies": ["Exploratory Data Analysis"],
            "estimated_days": 1
        })
        
        return phases
    
    def _get_fallback_plan(self) -> Dict[str, Any]:
        """Get a basic fallback plan when API fails"""
        return {
            "title": "Fallback Analysis Plan",
            "objective_alignment": 0.5,
            "phases": self._get_default_phases(
                {"analysis_type": "exploratory"},
                {}
            ),
            "methodology": {
                "approach": "Standard data analysis pipeline",
                "techniques": ["Statistical analysis", "Visualization", "Pattern detection"],
                "tools": ["Python", "Pandas", "Plotly"]
            },
            "risks": [
                {
                    "risk": "API connection issues",
                    "impact": "medium",
                    "mitigation": "Using fallback plan generator"
                }
            ],
            "success_metrics": [
                "Data quality assessment completed",
                "Key insights identified",
                "Actionable recommendations provided"
            ],
            "total_estimated_days": 5,
            "confidence": 0.5,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "Fallback Generator",
                "note": "Generated without AI due to API issues"
            }
        }
    
    def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """Real chat with AI assistant"""
        if not self.model:
            if not self._initialize_model():
                return "I'm currently offline. Please check your API configuration."
        
        try:
            # Build context-aware prompt
            prompt = self._build_chat_prompt(message, context)
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."
    
    def _build_chat_prompt(self, message: str, context: Optional[Dict]) -> str:
        """Build a context-aware chat prompt"""
        prompt = f"""
        You are an AI Data Analysis Manager helping with a data analysis project.
        
        Context:
        - Current Stage: {st.session_state.get('current_stage', 'Planning')}
        - Files Uploaded: {len(st.session_state.get('uploaded_data', {}))}
        - Analysis Type: {context.get('analysis_type', 'Not specified') if context else 'Not specified'}
        
        User Question: {message}
        
        Please provide a helpful, concise response. If the question is about the analysis plan or data, 
        be specific and actionable. Use your expertise in data analysis to guide the user.
        """
        
        return prompt
    
    def analyze_data(self, data: pd.DataFrame, analysis_type: str = "summary") -> Dict[str, Any]:
        """Perform real AI-powered data analysis"""
        if not self.model:
            if not self._initialize_model():
                return self._get_basic_analysis(data)
        
        try:
            # Create data summary for AI
            data_summary = self._create_data_summary(data)
            
            # Build analysis prompt
            prompt = f"""
            Analyze this dataset and provide insights:
            
            Dataset Summary:
            {data_summary}
            
            Analysis Type: {analysis_type}
            
            Please provide:
            1. Key patterns and trends
            2. Anomalies or outliers
            3. Correlations between variables
            4. Business insights
            5. Recommendations for further analysis
            
            Format as a structured analysis report.
            """
            
            # Get AI analysis
            response = self.model.generate_content(prompt)
            
            # Structure the response
            analysis = {
                "summary": response.text,
                "timestamp": datetime.now().isoformat(),
                "data_shape": data.shape,
                "analysis_type": analysis_type
            }
            
            return analysis
            
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return self._get_basic_analysis(data)
    
    def _create_data_summary(self, data: pd.DataFrame) -> str:
        """Create a summary of the dataframe for AI analysis"""
        summary = []
        
        # Basic info
        summary.append(f"Shape: {data.shape[0]} rows × {data.shape[1]} columns")
        summary.append(f"Columns: {', '.join(data.columns.tolist())}")
        
        # Data types
        summary.append("\nData Types:")
        for dtype, count in data.dtypes.value_counts().items():
            summary.append(f"  - {dtype}: {count} columns")
        
        # Numerical summary
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary.append("\nNumerical Columns Summary:")
            desc = data[numeric_cols].describe().to_string()
            summary.append(desc)
        
        # Categorical summary
        cat_cols = data.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            summary.append("\nCategorical Columns:")
            for col in cat_cols[:5]:  # Limit to first 5
                unique_count = data[col].nunique()
                summary.append(f"  - {col}: {unique_count} unique values")
        
        # Missing values
        missing = data.isnull().sum()
        if missing.sum() > 0:
            summary.append("\nMissing Values:")
            for col, count in missing[missing > 0].items():
                summary.append(f"  - {col}: {count} ({count/len(data)*100:.1f}%)")
        
        return "\n".join(summary)
    
    def _get_basic_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get basic analysis without AI"""
        return {
            "summary": "Basic statistical analysis (AI not available)",
            "shape": data.shape,
            "columns": data.columns.tolist(),
            "dtypes": data.dtypes.to_dict(),
            "missing": data.isnull().sum().to_dict(),
            "numeric_summary": data.describe().to_dict() if len(data.select_dtypes(include=[np.number]).columns) > 0 else {},
            "timestamp": datetime.now().isoformat()
        }

# Export the class
__all__ = ['AIManager']