"""
Stage 1: Plan Generation with AI Manager
Generate, edit, and refine analysis plans with AI assistance
"""

import streamlit as st
import sys
from pathlib import Path
import json
import yaml
from typing import Dict, Any

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from components.PlanEditor import PlanEditor
from components.ChatInterface import ChatInterface
from backend.ai_teammates.manager import AIManager

class PlanGenerationPage:
    """Main page for Stage 1: Plan Generation"""
    
    def __init__(self):
        """Initialize the page"""
        self.plan_editor = PlanEditor()
        self.chat_interface = ChatInterface()
        
        # Initialize AI Manager
        self.manager = AIManager()
        
        # Initialize session state
        if 'generated_plan' not in st.session_state:
            st.session_state.generated_plan = None
        if 'plan_approved' not in st.session_state:
            st.session_state.plan_approved = False
        
        # Load context from Stage 0
        self._load_context()
    
    def _load_context(self):
        """Load analysis context from previous stage"""
        context_file = Path("/root/repo/human_loop_platform/data/analysis_context.json")
        
        if context_file.exists():
            with open(context_file, 'r') as f:
                st.session_state.analysis_context = json.load(f)
        elif 'analysis_context' not in st.session_state:
            st.session_state.analysis_context = {}
    
    def render(self):
        """Render the main page"""
        # Header
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>🎯 AI-Powered Plan Generation</h1>
            <p style='font-size: 1.1rem; color: #666;'>Generate and refine your analysis plan with AI assistance</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress indicator
        self._render_progress_indicator()
        
        # Check if context exists
        if not st.session_state.get('analysis_context'):
            st.warning("⚠️ No analysis context found. Please complete Stage 0 first.")
            if st.button("← Go to Input & Objectives"):
                st.session_state.current_stage = 0
                st.rerun()
            return
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Plan generation and editing area
            self._render_plan_area()
        
        with col2:
            # Chat interface in sidebar column
            self._render_chat_column()
        
        # Action buttons at bottom
        self._render_action_buttons()
    
    def _render_progress_indicator(self):
        """Render stage progress indicator"""
        stages = [
            ("Input & Objectives", False),
            ("Plan Generation", True),  # Current stage
            ("Data Understanding", False),
            ("Task Configuration", False),
            ("Execution", False),
            ("Review & Export", False)
        ]
        
        st.markdown("### 📍 Analysis Workflow Progress")
        
        cols = st.columns(len(stages))
        for idx, (stage_name, is_active) in enumerate(stages):
            with cols[idx]:
                if is_active:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.8rem;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; border-radius: 10px; font-size: 0.85rem;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                        <strong>Step {idx + 1}</strong><br/>
                        <span style='font-size: 0.75rem;'>{stage_name}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.8rem;
                                background: #f8f9fa; color: #6c757d; border-radius: 10px;
                                border: 1px solid #dee2e6; font-size: 0.85rem;'>
                        Step {idx + 1}<br/>
                        <span style='font-size: 0.75rem;'>{stage_name}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    def _render_plan_area(self):
        """Render plan generation and editing area"""
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["🚀 Generate", "✏️ Edit", "📋 Summary"])
        
        with tab1:
            self._render_generation_tab()
        
        with tab2:
            self._render_edit_tab()
        
        with tab3:
            self._render_summary_tab()
    
    def _render_generation_tab(self):
        """Render plan generation tab"""
        
        st.header("Generate Analysis Plan")
        
        # Show current context
        with st.expander("📌 Analysis Context", expanded=True):
            context = st.session_state.analysis_context
            
            if 'objective' in context:
                obj = context['objective']
                st.markdown(f"**Objective:** {obj['objective']}")
                st.markdown(f"**Type:** {obj['analysis_type'].title()}")
                if obj.get('success_criteria'):
                    st.markdown(f"**Success Criteria:** {obj['success_criteria']}")
            
            if 'files' in context:
                file_count = sum(len(v) for v in context['files'].values())
                st.markdown(f"**Files:** {file_count} files uploaded")
        
        # Generation options
        col1, col2 = st.columns(2)
        
        with col1:
            generation_mode = st.radio(
                "Generation Mode",
                ["Automatic", "Guided", "Template"],
                help="Choose how to generate the plan"
            )
        
        with col2:
            if generation_mode == "Template":
                template = st.selectbox(
                    "Select Template",
                    ["Predictive Analysis", "Exploratory Analysis", 
                     "Diagnostic Analysis", "Descriptive Analysis"]
                )
        
        # Generate button
        if st.button("🎯 Generate Plan", type="primary", use_container_width=True):
            with st.spinner("AI Manager is generating your analysis plan..."):
                # Generate plan using AI Manager
                plan = self.manager.generate_analysis_plan(
                    objective=context.get('objective', {}),
                    files=context.get('files', {}),
                    context=context.get('objective', {}).get('context')
                )
                
                st.session_state.generated_plan = plan
                st.success("✅ Plan generated successfully!")
                
                # Show plan preview
                with st.expander("Plan Preview", expanded=True):
                    st.code(yaml.dump(plan, default_flow_style=False), language='yaml')
        
        # Regenerate option
        if st.session_state.generated_plan:
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Regenerate Plan"):
                    with st.spinner("Regenerating..."):
                        plan = self.manager.generate_analysis_plan(
                            objective=context.get('objective', {}),
                            files=context.get('files', {}),
                            context=context.get('objective', {}).get('context')
                        )
                        st.session_state.generated_plan = plan
                        st.rerun()
            
            with col2:
                feedback = st.text_input("Refinement feedback (optional)")
                if st.button("🔧 Refine Plan") and feedback:
                    with st.spinner("Refining plan based on your feedback..."):
                        refined_plan = self.manager.refine_plan(
                            st.session_state.generated_plan,
                            feedback
                        )
                        st.session_state.generated_plan = refined_plan
                        st.success("✅ Plan refined!")
                        st.rerun()
    
    def _render_edit_tab(self):
        """Render plan editing tab"""
        
        st.header("Edit Analysis Plan")
        
        if not st.session_state.generated_plan:
            st.info("💡 Generate a plan first to edit it")
            return
        
        # Plan editor
        edited_plan = self.plan_editor.render(st.session_state.generated_plan)
        
        # Update plan if edited
        if edited_plan != st.session_state.generated_plan:
            st.session_state.generated_plan = edited_plan
            st.success("✅ Plan updated")
    
    def _render_summary_tab(self):
        """Render plan summary tab"""
        
        st.header("Plan Summary")
        
        if not st.session_state.generated_plan:
            st.info("💡 Generate a plan first to see the summary")
            return
        
        # Plan summary
        self.plan_editor.render_plan_summary(st.session_state.generated_plan)
    
    def _render_chat_column(self):
        """Render chat interface column"""
        
        st.header("💬 AI Assistant")
        
        # Quick actions
        with st.expander("Quick Actions", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📋 Send to Reviewer", use_container_width=True):
                    self._send_to_reviewer()
                
                if st.button("📊 Send to Associate", use_container_width=True):
                    self._send_to_associate()
            
            with col2:
                if st.button("🧮 Send to Analyst", use_container_width=True):
                    self._send_to_analyst()
                
                if st.button("👔 Regenerate", use_container_width=True):
                    self._regenerate_with_manager()
        
        # Chat interface
        context = {
            'plan': st.session_state.generated_plan,
            'objective': st.session_state.analysis_context.get('objective')
        }
        
        # Render chat for active teammate
        teammate = st.selectbox(
            "Chat with:",
            ["manager", "reviewer", "associate", "analyst"],
            format_func=lambda x: self.chat_interface.AI_TEAMMATES[x]['name']
        )
        
        # Show chat history
        chat_container = st.container()
        with chat_container:
            self.chat_interface._display_chat_history(teammate, height=300)
        
        # Input area
        message = st.text_input(
            "Message:",
            key=f"plan_chat_input_{teammate}",
            placeholder="Ask a question..."
        )
        
        if st.button("Send", key=f"plan_send_{teammate}") and message:
            self.chat_interface._add_message(teammate, 'user', message)
            response = self.chat_interface._get_ai_response(teammate, message, context)
            self.chat_interface._add_message(teammate, teammate, response)
            st.rerun()
    
    def _render_action_buttons(self):
        """Render action buttons at bottom"""
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("← Previous", help="Go back to Input & Objectives"):
                st.session_state.current_stage = 0
                st.rerun()
        
        with col2:
            if st.button("💾 Save Plan", help="Save current plan"):
                self._save_plan()
        
        with col3:
            if st.button("📥 Export", help="Export plan to file"):
                self._export_plan()
        
        with col4:
            if st.session_state.generated_plan:
                if st.button("✅ Approve & Continue →", type="primary", 
                           help="Approve plan and continue to next stage"):
                    st.session_state.plan_approved = True
                    st.session_state.current_stage = 2
                    self._save_plan()
                    st.success("✅ Plan approved! Moving to Data Understanding...")
                    st.balloons()
                    # Would navigate to Stage 2
    
    def _send_to_reviewer(self):
        """Send plan to Reviewer AI"""
        if st.session_state.generated_plan:
            self.chat_interface._add_message('reviewer', 'user', 
                "Please review this plan and provide feedback")
            response = "I'll review your plan for completeness and best practices..."
            self.chat_interface._add_message('reviewer', 'reviewer', response)
            st.info("📋 Plan sent to Reviewer AI")
    
    def _send_to_associate(self):
        """Send plan to Associate AI"""
        if st.session_state.generated_plan:
            self.chat_interface._add_message('associate', 'user',
                "Please review the data preparation tasks in this plan")
            response = "I'll check the data preparation steps..."
            self.chat_interface._add_message('associate', 'associate', response)
            st.info("📊 Plan sent to Associate AI")
    
    def _send_to_analyst(self):
        """Send plan to Analyst AI"""
        if st.session_state.generated_plan:
            self.chat_interface._add_message('analyst', 'user',
                "Please review the analysis tasks in this plan")
            response = "I'll review the analysis methodology..."
            self.chat_interface._add_message('analyst', 'analyst', response)
            st.info("🧮 Plan sent to Analyst AI")
    
    def _regenerate_with_manager(self):
        """Regenerate plan with Manager AI"""
        with st.spinner("Regenerating plan..."):
            context = st.session_state.analysis_context
            plan = self.manager.generate_analysis_plan(
                objective=context.get('objective', {}),
                files=context.get('files', {}),
                context=context.get('objective', {}).get('context')
            )
            st.session_state.generated_plan = plan
            st.success("✅ Plan regenerated!")
            st.rerun()
    
    def _save_plan(self):
        """Save current plan to file"""
        if st.session_state.generated_plan:
            plan_file = Path("/root/repo/human_loop_platform/data/analysis_plan.json")
            with open(plan_file, 'w') as f:
                json.dump({
                    'plan': st.session_state.generated_plan,
                    'approved': st.session_state.plan_approved,
                    'context': st.session_state.analysis_context
                }, f, indent=2, default=str)
            st.success("✅ Plan saved!")
    
    def _export_plan(self):
        """Export plan for download"""
        if st.session_state.generated_plan:
            # Convert to YAML for export
            yaml_content = yaml.dump(
                st.session_state.generated_plan,
                default_flow_style=False,
                sort_keys=False
            )
            
            st.download_button(
                label="📥 Download Plan (YAML)",
                data=yaml_content,
                file_name="analysis_plan.yaml",
                mime="text/yaml"
            )

# Main execution
def main():
    page = PlanGenerationPage()
    page.render()

if __name__ == "__main__":
    main()