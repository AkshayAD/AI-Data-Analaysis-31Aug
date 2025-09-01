"""
AI Personas for Data Analysis Team
Simulates a collaborative AI analysis team with Manager, Analyst, and Associate personas
"""

import os
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from dataclasses import dataclass
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    
try:
    import pandas as pd
except ImportError:
    pd = None

@dataclass
class PersonaResponse:
    """Structure for persona responses"""
    persona: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

class AIPersona:
    """Base class for AI personas"""
    
    def __init__(self, name: str, role: str, model_name: str = "gemini-2.0-flash-exp"):
        self.name = name
        self.role = role
        self.model_name = model_name
        self.conversation_history = []
        
    def configure_api(self, api_key: str):
        """Configure Gemini API"""
        if HAS_GENAI:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
        
    def get_response(self, prompt: str, **kwargs) -> str:
        """Get response from Gemini model"""
        try:
            if self.model and HAS_GENAI:
                response = self.model.generate_content(prompt)
                return response.text
            else:
                # Return mock response for testing
                return f"[Mock {self.name} Response]: Analysis plan generated for prompt: {prompt[:100]}..."
        except Exception as e:
            return f"Error: {str(e)}"
            
    def add_to_history(self, content: str):
        """Add content to conversation history"""
        self.conversation_history.append({
            "persona": self.name,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

class ManagerPersona(AIPersona):
    """AI Manager - Creates analysis plans and strategies"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        super().__init__("Manager", "Strategic Planning & Oversight", model_name)
        
    def create_analysis_plan(self, project_name: str, problem_statement: str, 
                            data_context: str, file_info: str) -> str:
        """Create structured analysis plan"""
        prompt = f"""
        You are an AI Manager creating a comprehensive analysis plan.
        
        **Project Details:**
        - Project Name: {project_name}
        - Problem Statement: {problem_statement}
        - Data Context: {data_context}
        - Available Files: {file_info}
        
        **Your Task:**
        Create a structured, step-by-step analysis plan that includes:
        1. Executive Summary of objectives
        2. Data Assessment Strategy
        3. Analysis Methodology (specific techniques to apply)
        4. Expected Deliverables
        5. Risk Factors & Mitigation
        6. Success Metrics
        
        Format your response in clear sections with bullet points.
        Focus on actionable, specific steps the team can execute.
        """
        
        response = self.get_response(prompt)
        self.add_to_history(f"Created analysis plan: {response[:200]}...")
        return response
        
    def create_final_report(self, analysis_results: List[Dict], problem_statement: str) -> str:
        """Create final synthesis report"""
        prompt = f"""
        You are an AI Manager creating a final executive report.
        
        **Original Problem Statement:**
        {problem_statement}
        
        **Completed Analysis Results:**
        {json.dumps(analysis_results, indent=2)[:5000]}  # Limit size
        
        **Your Task:**
        Create a professional executive report that includes:
        1. Executive Summary
        2. Key Findings & Insights
        3. Data-Driven Recommendations
        4. Implementation Roadmap
        5. Expected Impact & ROI
        6. Next Steps
        
        Make it concise, actionable, and focused on business value.
        """
        
        response = self.get_response(prompt)
        self.add_to_history(f"Created final report: {response[:200]}...")
        return response

class AnalystPersona(AIPersona):
    """AI Analyst - Performs data analysis and technical execution"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        super().__init__("Analyst", "Data Analysis & Technical Execution", model_name)
        
    def analyze_data_profile(self, data_profiles: Dict, manager_plan: str) -> str:
        """Analyze data and provide technical summary"""
        prompt = f"""
        You are an AI Data Analyst examining the uploaded data.
        
        **Manager's Plan:**
        {manager_plan}
        
        **Data Profiles:**
        {json.dumps(data_profiles, indent=2)[:3000]}  # Limit size
        
        **Your Task:**
        Provide a technical data assessment including:
        1. Data Quality Assessment
        2. Key Statistics & Distributions
        3. Data Relationships & Patterns
        4. Potential Analysis Approaches
        5. Data Preparation Requirements
        6. Technical Recommendations
        
        Be specific and technical in your analysis.
        """
        
        response = self.get_response(prompt)
        self.add_to_history(f"Data profile analysis: {response[:200]}...")
        return response
        
    def execute_analysis_task(self, task: str, data_context: str) -> Dict:
        """Execute a specific analysis task"""
        prompt = f"""
        You are an AI Data Analyst executing a specific task.
        
        **Task Description:**
        {task}
        
        **Data Context:**
        {data_context}
        
        **Your Task:**
        1. Describe the analytical approach
        2. Generate Python code to execute this analysis
        3. Explain expected outputs
        4. Identify potential insights
        
        Format your response as:
        APPROACH: [methodology]
        CODE:
        ```python
        [your code here]
        ```
        EXPECTED_OUTPUT: [description]
        INSIGHTS: [potential findings]
        """
        
        response = self.get_response(prompt)
        self.add_to_history(f"Executed task: {task[:100]}...")
        
        # Parse response to extract code and other components
        result = {
            "task": task,
            "response": response,
            "code": self._extract_code(response),
            "timestamp": datetime.now().isoformat()
        }
        return result
        
    def _extract_code(self, response: str) -> str:
        """Extract Python code from response"""
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        return ""

class AssociatePersona(AIPersona):
    """AI Associate - Provides guidance and generates specific tasks"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        super().__init__("Associate", "Analysis Guidance & Task Generation", model_name)
        
    def generate_analysis_tasks(self, problem_statement: str, manager_plan: str, 
                               analyst_summary: str) -> List[str]:
        """Generate specific, executable analysis tasks"""
        prompt = f"""
        You are an AI Associate generating specific analysis tasks.
        
        **Problem Statement:**
        {problem_statement}
        
        **Manager's Strategic Plan:**
        {manager_plan}
        
        **Analyst's Data Assessment:**
        {analyst_summary}
        
        **Your Task:**
        Generate 5-8 specific, executable analysis tasks that:
        1. Directly address the problem statement
        2. Align with the manager's strategic plan
        3. Leverage the available data effectively
        4. Can be executed with Python/pandas/scikit-learn
        5. Will produce actionable insights
        
        Format each task as:
        TASK [number]: [Clear, specific task description]
        - Objective: [What this achieves]
        - Method: [Technical approach]
        - Output: [Expected deliverable]
        
        Make tasks specific and technical, not generic.
        """
        
        response = self.get_response(prompt)
        self.add_to_history(f"Generated analysis tasks: {response[:200]}...")
        
        # Parse tasks from response
        tasks = self._parse_tasks(response)
        return tasks
        
    def review_analysis(self, task_results: List[Dict]) -> str:
        """Review completed analysis tasks"""
        prompt = f"""
        You are an AI Associate reviewing completed analysis tasks.
        
        **Completed Tasks and Results:**
        {json.dumps(task_results, indent=2)[:4000]}  # Limit size
        
        **Your Task:**
        Provide a comprehensive review including:
        1. Quality Assessment of each analysis
        2. Key Insights Discovered
        3. Gaps or Missing Analyses
        4. Recommendations for Improvement
        5. Suggested Follow-up Analyses
        6. Integration Opportunities
        
        Be constructive and specific in your feedback.
        """
        
        response = self.get_response(prompt)
        self.add_to_history(f"Review of analysis: {response[:200]}...")
        return response
        
    def _parse_tasks(self, response: str) -> List[str]:
        """Parse individual tasks from response"""
        tasks = []
        lines = response.split('\n')
        current_task = []
        
        for line in lines:
            if line.strip().startswith('TASK'):
                if current_task:
                    tasks.append('\n'.join(current_task).strip())
                current_task = [line]
            elif current_task:
                current_task.append(line)
                
        if current_task:
            tasks.append('\n'.join(current_task).strip())
            
        return tasks

class AITeamOrchestrator:
    """Orchestrates the AI team collaboration"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        self.manager = ManagerPersona(model_name)
        self.analyst = AnalystPersona(model_name)
        self.associate = AssociatePersona(model_name)
        
        # Configure API for all personas
        self.manager.configure_api(api_key)
        self.analyst.configure_api(api_key)
        self.associate.configure_api(api_key)
        
        self.conversation_history = []
        
    def add_to_conversation(self, persona: str, content: str):
        """Add to conversation history"""
        self.conversation_history.append({
            "persona": persona,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_conversation_history(self) -> List[Dict]:
        """Get complete conversation history"""
        history = []
        for persona in [self.manager, self.analyst, self.associate]:
            history.extend(persona.conversation_history)
        history.extend(self.conversation_history)
        # Sort by timestamp
        history.sort(key=lambda x: x.get('timestamp', ''))
        return history
        
    def run_complete_analysis(self, project_name: str, problem_statement: str,
                            data_context: str, data_files: Dict) -> Dict:
        """Run complete analysis workflow"""
        results = {
            "project_name": project_name,
            "problem_statement": problem_statement,
            "stages": {}
        }
        
        # Stage 1: Manager creates plan
        file_info = self._format_file_info(data_files)
        manager_plan = self.manager.create_analysis_plan(
            project_name, problem_statement, data_context, file_info
        )
        results["stages"]["manager_plan"] = manager_plan
        
        # Stage 2: Analyst examines data
        data_profiles = self._create_data_profiles(data_files)
        analyst_summary = self.analyst.analyze_data_profile(
            data_profiles, manager_plan
        )
        results["stages"]["analyst_summary"] = analyst_summary
        
        # Stage 3: Associate generates tasks
        tasks = self.associate.generate_analysis_tasks(
            problem_statement, manager_plan, analyst_summary
        )
        results["stages"]["tasks"] = tasks
        
        # Stage 4: Analyst executes tasks (would integrate with marimo here)
        task_results = []
        for task in tasks[:3]:  # Limit to first 3 tasks for demo
            result = self.analyst.execute_analysis_task(
                task, data_context
            )
            task_results.append(result)
        results["stages"]["task_results"] = task_results
        
        # Stage 5: Associate reviews
        review = self.associate.review_analysis(task_results)
        results["stages"]["review"] = review
        
        # Stage 6: Manager creates final report
        final_report = self.manager.create_final_report(
            task_results, problem_statement
        )
        results["stages"]["final_report"] = final_report
        
        return results
        
    def _format_file_info(self, data_files: Dict) -> str:
        """Format file information for prompts"""
        info = []
        if pd is None:
            # Return mock info if pandas not available
            for name in data_files.keys():
                info.append(f"- {name}: 100 rows, 10 columns")
                info.append(f"  Columns: col1, col2, col3...")
        else:
            for name, df in data_files.items():
                if pd and isinstance(df, pd.DataFrame):
                    info.append(f"- {name}: {df.shape[0]} rows, {df.shape[1]} columns")
                    info.append(f"  Columns: {', '.join(df.columns[:10])}")
        return '\n'.join(info)
        
    def _create_data_profiles(self, data_files: Dict) -> Dict:
        """Create data profiles for analysis"""
        profiles = {}
        if pd is None:
            # Return mock profiles if pandas not available
            for name in data_files.keys():
                profiles[name] = {
                    "shape": (100, 10),
                    "columns": ["col1", "col2", "col3"],
                    "dtypes": {},
                    "missing": {},
                    "summary": {}
                }
        else:
            for name, df in data_files.items():
                if pd and isinstance(df, pd.DataFrame):
                    profiles[name] = {
                        "shape": df.shape,
                        "columns": list(df.columns),
                        "dtypes": df.dtypes.to_dict(),
                        "missing": df.isnull().sum().to_dict(),
                        "summary": df.describe().to_dict() if not df.empty else {}
                    }
        return profiles