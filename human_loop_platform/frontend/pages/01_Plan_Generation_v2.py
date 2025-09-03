"""
Stage 1: Plan Generation with Real AI Integration
Uses actual Gemini API for plan generation and chat
"""

import streamlit as st
from pathlib import Path
import sys
import json
from typing import Dict, Any
import yaml
from datetime import datetime

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from components.PlanEditor import PlanEditor
from components.ChatInterface import ChatInterface
from backend.ai_teammates.manager import AIManager

class PlanGenerationPage:
    """Plan Generation page with real AI integration"""
    
    def __init__(self):
        """Initialize with real AI manager"""
        # Initialize components
        self.plan_editor = PlanEditor()
        self.chat_interface = ChatInterface()
        
        # Initialize AI Manager with real API
        self.manager = AIManager()
        
        # Initialize session state
        if 'generated_plan' not in st.session_state:
            st.session_state.generated_plan = None
            
        if 'plan_approved' not in st.session_state:
            st.session_state.plan_approved = False
            
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def render(self):
        """Render the main page"""
        # Check API configuration
        if not st.session_state.get('api_configured', False):
            st.error("⚠️ API not configured. Please return to Stage 0 and configure your Gemini API key.")
            if st.button("← Back to Input & Objectives"):
                st.session_state.current_stage = 0
                st.rerun()
            return
        
        # Check for context from Stage 0
        if not st.session_state.get('analysis_context'):
            st.warning("⚠️ No analysis context found. Please complete Stage 0 first.")
            if st.button("← Back to Input & Objectives"):
                st.session_state.current_stage = 0
                st.rerun()
            return
        
        # Header
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>🎯 AI-Powered Plan Generation</h1>
            <p style='font-size: 1.1rem; color: #666;'>Generate and refine your analysis plan with AI assistance</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress indicator
        self._render_progress_indicator()
        
        # Main content
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Main plan area with tabs
            tab1, tab2, tab3, tab4 = st.tabs(["🎯 Generate", "✏️ Edit", "📊 Summary", "🔍 Status"])
            
            with tab1:
                self._render_generation_tab()
            
            with tab2:
                self._render_edit_tab()
            
            with tab3:
                self._render_summary_tab()
                
            with tab4:
                self._render_status_tab()
        
        with col2:
            # AI Assistant sidebar
            self._render_ai_assistant()
        
        # Action buttons
        self._render_action_buttons()
    
    def _render_generation_tab(self):
        """Render plan generation tab"""
        st.header("Generate Analysis Plan")
        
        # Show current context
        with st.expander("📌 Analysis Context", expanded=True):
            context = st.session_state.analysis_context
            
            if 'objective' in context:
                obj = context['objective']
                st.write(f"**Objective:** {obj.get('objective', 'Not set')}")
                st.write(f"**Type:** {obj.get('analysis_type', 'Not set').title()}")
                if obj.get('success_criteria'):
                    st.write(f"**Success Criteria:** {obj['success_criteria']}")
            
            if 'files' in context:
                st.write(f"**Files:** {len(context['files'])} files uploaded")
                for filename in context['files']:
                    st.caption(f"• {filename}")
        
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
            else:
                template = None
        
        # Additional instructions
        additional_instructions = st.text_area(
            "Additional Instructions (Optional)",
            placeholder="Any specific requirements or focus areas for the analysis plan...",
            height=100
        )
        
        # Generate button
        if st.button("🎯 Generate Plan", type="primary", use_container_width=True):
            with st.spinner("AI Manager is generating your analysis plan..."):
                # Use real AI to generate plan
                plan = self.manager.generate_analysis_plan(
                    objective=context.get('objective', {}),
                    files=context.get('files', {}),
                    context=additional_instructions if additional_instructions else None
                )
                
                if plan:
                    st.session_state.generated_plan = plan
                    st.success("✅ Plan generated successfully!")
                    
                    # Show plan preview
                    with st.expander("📋 Plan Preview", expanded=True):
                        # Display key metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Phases", len(plan.get('phases', [])))
                        with col2:
                            total_tasks = sum(len(p.get('tasks', [])) for p in plan.get('phases', []))
                            st.metric("Tasks", total_tasks)
                        with col3:
                            st.metric("Est. Days", plan.get('total_estimated_days', 0))
                        with col4:
                            confidence = plan.get('confidence', 0.5)
                            st.metric("Confidence", f"{confidence:.1%}")
                        
                        # Show plan structure
                        st.json(plan)
                else:
                    st.error("❌ Failed to generate plan. Please check your API configuration.")
    
    def _render_edit_tab(self):
        """Render plan editing tab"""
        st.header("Edit Analysis Plan")
        
        if not st.session_state.generated_plan:
            st.info("📝 No plan generated yet. Generate a plan first to edit it.")
            return
        
        # Format selector
        format_option = st.radio("Format", ["YAML", "JSON"], horizontal=True)
        
        # Convert plan to selected format
        plan = st.session_state.generated_plan
        if format_option == "YAML":
            plan_text = yaml.dump(plan, default_flow_style=False, sort_keys=False)
        else:
            plan_text = json.dumps(plan, indent=2)
        
        # Edit area
        edited_text = st.text_area(
            "✏️ Edit Plan",
            value=plan_text,
            height=400,
            help="Edit the plan structure. Be careful to maintain valid YAML/JSON format."
        )
        
        # Validation and save buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Validate"):
                try:
                    if format_option == "YAML":
                        validated = yaml.safe_load(edited_text)
                    else:
                        validated = json.loads(edited_text)
                    st.success("✅ Valid format!")
                except Exception as e:
                    st.error(f"❌ Invalid format: {str(e)}")
        
        with col2:
            if st.button("💾 Save Changes"):
                try:
                    if format_option == "YAML":
                        updated_plan = yaml.safe_load(edited_text)
                    else:
                        updated_plan = json.loads(edited_text)
                    st.session_state.generated_plan = updated_plan
                    st.success("✅ Changes saved!")
                except Exception as e:
                    st.error(f"❌ Cannot save: {str(e)}")
        
        with col3:
            if st.button("↩️ Reset"):
                st.session_state.generated_plan = st.session_state.get('original_plan', {})
                st.rerun()
        
        with col4:
            if st.button("⬇️ Download"):
                if format_option == "YAML":
                    st.download_button(
                        "Download YAML",
                        data=edited_text,
                        file_name="analysis_plan.yaml",
                        mime="text/yaml"
                    )
                else:
                    st.download_button(
                        "Download JSON",
                        data=edited_text,
                        file_name="analysis_plan.json",
                        mime="application/json"
                    )
    
    def _render_summary_tab(self):
        """Render plan summary tab"""
        st.header("Plan Summary")
        
        if not st.session_state.generated_plan:
            st.info("📊 No plan to summarize. Generate a plan first.")
            return
        
        plan = st.session_state.generated_plan
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Phases", len(plan.get('phases', [])))
        
        with col2:
            total_tasks = sum(len(p.get('tasks', [])) for p in plan.get('phases', []))
            st.metric("Total Tasks", total_tasks)
        
        with col3:
            st.metric("Est. Duration", f"{plan.get('total_estimated_days', 0)} days")
        
        with col4:
            confidence = plan.get('confidence', 0.5)
            st.metric("Confidence", f"{confidence:.1%}")
        
        # Phases breakdown
        st.subheader("📋 Analysis Phases")
        
        for i, phase in enumerate(plan.get('phases', []), 1):
            with st.expander(f"Phase {i}: {phase.get('name', 'Unnamed')}"):
                st.write(f"**Description:** {phase.get('description', 'No description')}")
                st.write(f"**Estimated Days:** {phase.get('estimated_days', 1)}")
                
                # Tasks
                st.write("**Tasks:**")
                for j, task in enumerate(phase.get('tasks', []), 1):
                    st.write(f"{j}. {task.get('name', 'Unnamed task')}")
                    if task.get('description'):
                        st.caption(f"   {task['description']}")
                    if task.get('estimated_hours'):
                        st.caption(f"   ⏱️ {task['estimated_hours']} hours")
                
                # Dependencies
                if phase.get('dependencies'):
                    st.write(f"**Dependencies:** {', '.join(phase['dependencies'])}")
        
        # Methodology
        if 'methodology' in plan:
            st.subheader("🔬 Methodology")
            method = plan['methodology']
            st.write(f"**Approach:** {method.get('approach', 'Not specified')}")
            if method.get('techniques'):
                st.write(f"**Techniques:** {', '.join(method['techniques'])}")
            if method.get('tools'):
                st.write(f"**Tools:** {', '.join(method['tools'])}")
        
        # Risks
        if 'risks' in plan and plan['risks']:
            st.subheader("⚠️ Risks & Mitigation")
            for risk in plan['risks']:
                with st.expander(f"{risk.get('impact', '').upper()}: {risk.get('risk', 'Unknown risk')}"):
                    st.write(f"**Mitigation:** {risk.get('mitigation', 'No mitigation strategy')}")
    
    def _render_status_tab(self):
        """Render system status tab"""
        st.header("🔍 System Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Working Features")
            st.write("• AI Plan Generation: **Real**")
            st.write("• Plan Editing: **Real**")
            st.write("• AI Chat: **Real**")
            st.write("• Data Context: **Real**")
            st.write("• Export Functions: **Real**")
        
        with col2:
            st.subheader("📊 Current Status")
            st.write(f"• API: **{st.session_state.get('gemini_model', 'Not set')}**")
            st.write(f"• Files: **{len(st.session_state.get('uploaded_data', {}))}**")
            st.write(f"• Plan: **{'Generated' if st.session_state.generated_plan else 'Not generated'}**")
            st.write(f"• Chat History: **{len(st.session_state.chat_history)} messages**")
        
        # Show session data
        if st.checkbox("Show Session Data (Debug)"):
            st.json({
                "api_configured": st.session_state.get('api_configured', False),
                "model": st.session_state.get('gemini_model', 'Not set'),
                "plan_generated": bool(st.session_state.generated_plan),
                "files_count": len(st.session_state.get('uploaded_data', {})),
                "chat_messages": len(st.session_state.chat_history)
            })
    
    def _render_ai_assistant(self):
        """Render real AI assistant"""
        st.header("💬 AI Assistant")
        
        # Check API
        if not st.session_state.get('api_configured', False):
            st.warning("⚠️ Configure API in Stage 0")
            return
        
        # Quick actions
        with st.expander("⚡ Quick Actions"):
            if st.button("📊 Explain the plan", use_container_width=True):
                self._handle_chat_message("Please explain the current analysis plan in simple terms.")
            
            if st.button("💡 Suggest improvements", use_container_width=True):
                self._handle_chat_message("What improvements would you suggest for this analysis plan?")
            
            if st.button("⚠️ Identify risks", use_container_width=True):
                self._handle_chat_message("What are the main risks in this analysis approach?")
        
        # Chat interface
        st.subheader("Chat")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history[-5:]:  # Show last 5 messages
                if msg['role'] == 'user':
                    st.write(f"**You:** {msg['content']}")
                else:
                    st.write(f"**AI:** {msg['content']}")
        
        # Input area
        user_message = st.text_area(
            "Message:",
            placeholder="Ask about the plan, data, or analysis approach...",
            height=100,
            key="chat_input"
        )
        
        if st.button("Send", type="primary", use_container_width=True):
            if user_message:
                self._handle_chat_message(user_message)
                st.rerun()
    
    def _handle_chat_message(self, message: str):
        """Handle real chat with AI"""
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get AI response
        with st.spinner("AI is thinking..."):
            context = {
                'plan': st.session_state.generated_plan,
                'objective': st.session_state.analysis_context.get('objective', {}),
                'files': st.session_state.analysis_context.get('files', {})
            }
            
            response = self.manager.chat(message, context)
            
            # Add AI response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
    
    def _render_progress_indicator(self):
        """Render progress indicator"""
        stages = [
            ("Input & Objectives", True),
            ("Plan Generation", True),  # Current stage
            ("Data Understanding", False),
            ("Task Configuration", False),
            ("Execution", False),
            ("Review & Export", False)
        ]
        
        cols = st.columns(len(stages))
        for i, (stage_name, completed) in enumerate(stages):
            with cols[i]:
                if i == 1:  # Current stage
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem; 
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; border-radius: 10px;'>
                        <strong>Step {i+1}</strong><br>{stage_name}
                    </div>
                    """, unsafe_allow_html=True)
                elif completed:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem; 
                                background: #d4edda; border-radius: 10px;'>
                        <small>Step {i+1}</small><br>{stage_name}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem; 
                                background: #e0e0e0; border-radius: 10px;'>
                        <small>Step {i+1}</small><br>{stage_name}
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_action_buttons(self):
        """Render action buttons"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("← Previous", help="Go back to Input & Objectives"):
                st.session_state.current_stage = 0
                st.rerun()
        
        with col2:
            if st.button("💾 Save Plan", help="Save current plan"):
                if st.session_state.generated_plan:
                    # Save plan to file
                    plan_file = Path(__file__).parent.parent.parent / "data" / "current_plan.json"
                    plan_file.parent.mkdir(exist_ok=True)
                    with open(plan_file, "w") as f:
                        json.dump(st.session_state.generated_plan, f, indent=2)
                    st.success("✅ Plan saved!")
                else:
                    st.warning("No plan to save")
        
        with col3:
            if st.button("Continue →", type="primary", help="Proceed to Data Understanding"):
                if st.session_state.generated_plan:
                    st.session_state.current_stage = 2
                    st.session_state.plan_approved = True
                    st.success("✅ Moving to Data Understanding...")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("Please generate a plan first")

# Main execution
def main():
    page = PlanGenerationPage()
    page.render()

if __name__ == "__main__":
    main()