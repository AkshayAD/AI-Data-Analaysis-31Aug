"""
Plan Editor Component
Allows editing of analysis plans in YAML/JSON format with validation
"""

import streamlit as st
import yaml
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PlanEditor:
    """Component for editing and validating analysis plans"""
    
    def __init__(self):
        """Initialize plan editor"""
        if 'current_plan' not in st.session_state:
            st.session_state.current_plan = None
        if 'plan_format' not in st.session_state:
            st.session_state.plan_format = 'yaml'
        if 'plan_history' not in st.session_state:
            st.session_state.plan_history = []
    
    def render(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Render the plan editor interface"""
        
        st.subheader("📝 Analysis Plan Editor")
        
        # Format selector
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            format_choice = st.radio(
                "Format",
                ["YAML", "JSON"],
                horizontal=True,
                key="plan_format_selector"
            )
            st.session_state.plan_format = format_choice.lower()
        
        with col2:
            # Validation status
            is_valid, validation_msg = self._validate_plan(plan)
            if is_valid:
                st.success("✅ Valid")
            else:
                st.error("❌ Invalid")
        
        with col3:
            # Quick actions
            cols = st.columns(3)
            with cols[0]:
                if st.button("🔄 Reset", help="Reset to original plan"):
                    return self._reset_plan()
            with cols[1]:
                if st.button("↩️ Undo", help="Undo last change"):
                    return self._undo_change()
            with cols[2]:
                if st.button("✓ Validate", help="Validate plan structure"):
                    self._show_validation_details(plan)
        
        # Convert plan to editable format
        if st.session_state.plan_format == 'yaml':
            plan_text = yaml.dump(plan, default_flow_style=False, sort_keys=False)
            language = 'yaml'
        else:
            plan_text = json.dumps(plan, indent=2)
            language = 'json'
        
        # Editor area
        edited_text = st.text_area(
            "Edit Plan",
            value=plan_text,
            height=500,
            key="plan_editor_text",
            help="Edit the plan directly. Changes are validated in real-time."
        )
        
        # Parse edited text back to dict
        try:
            if st.session_state.plan_format == 'yaml':
                edited_plan = yaml.safe_load(edited_text)
            else:
                edited_plan = json.loads(edited_text)
            
            # Validate edited plan
            is_valid, msg = self._validate_plan(edited_plan)
            
            if is_valid:
                # Store in history
                if plan != edited_plan:
                    self._add_to_history(plan)
                return edited_plan
            else:
                st.error(f"Validation Error: {msg}")
                return plan
                
        except yaml.YAMLError as e:
            st.error(f"YAML Syntax Error: {str(e)}")
            return plan
        except json.JSONDecodeError as e:
            st.error(f"JSON Syntax Error: {str(e)}")
            return plan
        except Exception as e:
            st.error(f"Error parsing plan: {str(e)}")
            return plan
    
    def render_plan_summary(self, plan: Dict[str, Any]):
        """Render a summary view of the plan"""
        
        st.subheader("📋 Plan Summary")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Phases",
                len(plan.get('phases', [])),
                help="Number of analysis phases"
            )
        
        with col2:
            total_tasks = sum(
                len(phase.get('tasks', [])) 
                for phase in plan.get('phases', [])
            )
            st.metric(
                "Total Tasks",
                total_tasks,
                help="Total number of tasks"
            )
        
        with col3:
            duration = plan.get('metadata', {}).get('estimated_duration', 0)
            st.metric(
                "Est. Duration",
                f"{duration} min",
                help="Estimated completion time"
            )
        
        with col4:
            confidence = plan.get('metadata', {}).get('confidence', 0)
            st.metric(
                "Confidence",
                f"{confidence:.0%}",
                help="Plan confidence score"
            )
        
        # Phases overview
        st.markdown("### 🎯 Analysis Phases")
        
        for i, phase in enumerate(plan.get('phases', []), 1):
            with st.expander(f"Phase {i}: {phase.get('name', 'Unknown')}", expanded=(i==1)):
                st.markdown(f"**Description:** {phase.get('description', 'N/A')}")
                st.markdown(f"**Owner:** {phase.get('owner', 'Not assigned')}")
                st.markdown(f"**Tasks:** {len(phase.get('tasks', []))}")
                
                # Task list
                tasks = phase.get('tasks', [])
                if tasks:
                    st.markdown("#### Tasks:")
                    for task in tasks:
                        review_icon = "👁️" if task.get('requires_human_review') else ""
                        st.write(f"• {task.get('name', 'Unnamed task')} {review_icon}")
                        st.caption(f"  Type: {task.get('type', 'unknown')} | "
                                 f"Est: {task.get('estimated_time', 5)} min")
        
        # Quality Gates
        if plan.get('quality_gates'):
            st.markdown("### 🚦 Quality Gates")
            for gate in plan['quality_gates']:
                st.info(f"After **{gate.get('after_phase', 'Unknown')}**: "
                       f"{', '.join(gate.get('criteria', []))}")
        
        # Success Metrics
        if plan.get('success_metrics'):
            st.markdown("### 📊 Success Metrics")
            for metric in plan['success_metrics']:
                st.write(f"• **{metric.get('metric', 'Unknown')}**: "
                        f"{metric.get('target', 'N/A')} "
                        f"({metric.get('measurement', 'N/A')})")
        
        # Risks
        if plan.get('risks'):
            st.markdown("### ⚠️ Identified Risks")
            for risk in plan['risks']:
                impact_color = {
                    'low': '🟢',
                    'medium': '🟡', 
                    'high': '🔴'
                }.get(risk.get('impact', 'medium'), '🟡')
                
                st.write(f"{impact_color} **{risk.get('risk', 'Unknown risk')}**")
                st.caption(f"Mitigation: {risk.get('mitigation', 'None specified')}")
    
    def _validate_plan(self, plan: Dict[str, Any]) -> tuple[bool, str]:
        """Validate plan structure"""
        
        if not isinstance(plan, dict):
            return False, "Plan must be a dictionary"
        
        # Check required fields
        required_fields = ['phases']
        for field in required_fields:
            if field not in plan:
                return False, f"Missing required field: {field}"
        
        # Validate phases
        if not isinstance(plan['phases'], list):
            return False, "Phases must be a list"
        
        if len(plan['phases']) == 0:
            return False, "Plan must have at least one phase"
        
        # Validate each phase
        for i, phase in enumerate(plan['phases']):
            if not isinstance(phase, dict):
                return False, f"Phase {i+1} must be a dictionary"
            
            if 'name' not in phase:
                return False, f"Phase {i+1} missing name"
            
            if 'tasks' in phase and not isinstance(phase['tasks'], list):
                return False, f"Phase {i+1} tasks must be a list"
        
        return True, "Plan is valid"
    
    def _show_validation_details(self, plan: Dict[str, Any]):
        """Show detailed validation results"""
        
        is_valid, msg = self._validate_plan(plan)
        
        if is_valid:
            st.success(f"✅ {msg}")
            
            # Show plan statistics
            st.info(
                f"**Plan Statistics:**\n"
                f"- Phases: {len(plan.get('phases', []))}\n"
                f"- Total Tasks: {sum(len(p.get('tasks', [])) for p in plan.get('phases', []))}\n"
                f"- Quality Gates: {len(plan.get('quality_gates', []))}\n"
                f"- Success Metrics: {len(plan.get('success_metrics', []))}\n"
                f"- Identified Risks: {len(plan.get('risks', []))}"
            )
        else:
            st.error(f"❌ {msg}")
            
            # Suggest fixes
            st.warning("**Suggested Fixes:**")
            if "Missing required field" in msg:
                st.write("• Add the missing field to your plan")
            if "must be a list" in msg:
                st.write("• Ensure the field is formatted as a list (YAML: use '-' prefix)")
            if "must be a dictionary" in msg:
                st.write("• Ensure the field is formatted as a dictionary/object")
    
    def _add_to_history(self, plan: Dict[str, Any]):
        """Add plan to history for undo functionality"""
        
        st.session_state.plan_history.append(plan.copy())
        
        # Keep only last 10 versions
        if len(st.session_state.plan_history) > 10:
            st.session_state.plan_history.pop(0)
    
    def _undo_change(self) -> Dict[str, Any]:
        """Undo last change"""
        
        if st.session_state.plan_history:
            return st.session_state.plan_history.pop()
        
        st.warning("No changes to undo")
        return st.session_state.current_plan
    
    def _reset_plan(self) -> Dict[str, Any]:
        """Reset to original plan"""
        
        if st.session_state.plan_history:
            # Return first plan in history
            original = st.session_state.plan_history[0]
            st.session_state.plan_history.clear()
            return original
        
        return st.session_state.current_plan