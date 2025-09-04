"""
Objective Input Component
Captures business objectives, success criteria, and analysis context
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime

class ObjectiveInput:
    """Component for capturing analysis objectives and context"""
    
    ANALYSIS_TYPES = {
        'exploratory': {
            'name': '🔍 Exploratory Analysis',
            'description': 'Discover patterns, relationships, and insights in your data',
            'typical_questions': [
                'What patterns exist in the data?',
                'Are there any anomalies or outliers?',
                'What relationships exist between variables?'
            ]
        },
        'predictive': {
            'name': '🔮 Predictive Analysis',
            'description': 'Build models to forecast future outcomes',
            'typical_questions': [
                'What will happen next?',
                'Can we predict customer behavior?',
                'What factors drive the outcome?'
            ]
        },
        'diagnostic': {
            'name': '🏥 Diagnostic Analysis',
            'description': 'Understand why something happened',
            'typical_questions': [
                'What caused this issue?',
                'Why did performance drop?',
                'What are the root causes?'
            ]
        },
        'descriptive': {
            'name': '📊 Descriptive Analysis',
            'description': 'Summarize and describe historical data',
            'typical_questions': [
                'What happened?',
                'How many, how much, how often?',
                'What are the key metrics?'
            ]
        }
    }
    
    def __init__(self):
        """Initialize objective input component"""
        if 'objective_data' not in st.session_state:
            st.session_state.objective_data = {}
    
    def render(self) -> Dict[str, Any]:
        """Render objective input interface"""
        st.header("🎯 Define Your Analysis Objective")
        
        # Main objective input
        col1, col2 = st.columns([2, 1])
        
        with col1:
            objective = st.text_area(
                "Business Objective *",
                placeholder="Example: Identify factors driving customer churn and develop strategies to reduce churn rate by 25% in Q1 2024",
                height=100,
                help="Clearly describe what you want to achieve with this analysis"
            )
            
            # Success criteria
            success_criteria = st.text_area(
                "Success Criteria",
                placeholder="Example:\n- Identify top 3 churn factors with >80% confidence\n- Develop actionable retention strategies\n- Create early warning system for at-risk customers",
                height=80,
                help="Define measurable criteria for successful analysis"
            )
        
        with col2:
            # Analysis type selection
            analysis_type = st.selectbox(
                "Analysis Type *",
                options=list(self.ANALYSIS_TYPES.keys()),
                format_func=lambda x: self.ANALYSIS_TYPES[x]['name'],
                help="Select the type of analysis that best fits your objective"
            )
            
            # Show type description
            if analysis_type:
                st.info(self.ANALYSIS_TYPES[analysis_type]['description'])
                
                # Show typical questions
                with st.expander("Typical Questions"):
                    for question in self.ANALYSIS_TYPES[analysis_type]['typical_questions']:
                        st.write(f"• {question}")
        
        # Additional context (expandable)
        with st.expander("📝 Additional Context (Optional)", expanded=False):
            context_data = self._render_context_inputs()
        
        # Validate inputs
        is_valid = self._validate_inputs(objective, analysis_type)
        
        if is_valid:
            # Compile objective data
            objective_data = {
                'objective': objective,
                'analysis_type': analysis_type,
                'success_criteria': success_criteria if success_criteria else None,
                'context': context_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in session state
            st.session_state.objective_data = objective_data
            
            # Show summary
            self._show_objective_summary(objective_data)
            
            return objective_data
        
        return {}
    
    def _render_context_inputs(self) -> Dict[str, Any]:
        """Render additional context input fields"""
        context = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Data source information
            context['data_source'] = st.text_input(
                "Data Source",
                placeholder="e.g., CRM system, Sales database, Survey responses"
            )
            
            # Time period
            context['time_period'] = st.text_input(
                "Time Period",
                placeholder="e.g., Jan 2023 - Dec 2023, Last 6 months"
            )
            
            # Industry/Domain
            context['domain'] = st.selectbox(
                "Industry/Domain",
                options=['', 'E-commerce', 'Healthcare', 'Finance', 'Manufacturing', 
                        'Retail', 'Technology', 'Education', 'Other'],
                help="Select your industry or domain"
            )
        
        with col2:
            # Known issues
            context['known_issues'] = st.text_area(
                "Known Data Issues",
                placeholder="e.g., Missing values in email field, Duplicate records possible",
                height=68
            )
            
            # Expected challenges
            context['challenges'] = st.text_area(
                "Expected Challenges",
                placeholder="e.g., Imbalanced dataset, Seasonal variations",
                height=68
            )
        
        # Stakeholders
        context['stakeholders'] = st.text_input(
            "Key Stakeholders",
            placeholder="e.g., Marketing Team, C-Suite, Product Managers"
        )
        
        # Additional notes
        context['notes'] = st.text_area(
            "Additional Notes",
            placeholder="Any other relevant information about the analysis...",
            height=60
        )
        
        # Remove empty values
        context = {k: v for k, v in context.items() if v}
        
        return context
    
    def _validate_inputs(self, objective: str, analysis_type: str) -> bool:
        """Validate required inputs"""
        errors = []
        
        if not objective or len(objective.strip()) < 10:
            errors.append("Please provide a clear business objective (at least 10 characters)")
        
        if not analysis_type:
            errors.append("Please select an analysis type")
        
        if errors:
            for error in errors:
                st.error(error)
            return False
        
        return True
    
    def _show_objective_summary(self, objective_data: Dict[str, Any]):
        """Display summary of captured objectives"""
        st.success("✅ Objective captured successfully!")
        
        with st.expander("📋 Objective Summary", expanded=True):
            # Main objective
            st.markdown("**Business Objective:**")
            st.info(objective_data['objective'])
            
            # Analysis type
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Analysis Type:**")
                st.write(self.ANALYSIS_TYPES[objective_data['analysis_type']]['name'])
            
            with col2:
                if objective_data.get('success_criteria'):
                    st.markdown("**Success Criteria:**")
                    st.write(objective_data['success_criteria'])
            
            # Context if provided
            if objective_data.get('context'):
                st.markdown("**Additional Context:**")
                for key, value in objective_data['context'].items():
                    if value:
                        st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
    
    def get_objective_data(self) -> Dict[str, Any]:
        """Get stored objective data"""
        return st.session_state.get('objective_data', {})
    
    def clear_objective_data(self):
        """Clear stored objective data"""
        if 'objective_data' in st.session_state:
            del st.session_state.objective_data