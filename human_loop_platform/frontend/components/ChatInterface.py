"""
Chat Interface Component
Real-time chat with AI teammates
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

class ChatInterface:
    """Component for chatting with AI teammates"""
    
    AI_TEAMMATES = {
        'manager': {
            'name': '👔 Manager AI',
            'role': 'Generate and refine analysis plans',
            'color': '#667eea'
        },
        'reviewer': {
            'name': '✅ Reviewer AI',
            'role': 'Validate plans and provide quality checks',
            'color': '#48bb78'
        },
        'associate': {
            'name': '📊 Associate AI',
            'role': 'Handle data understanding and preparation',
            'color': '#ed8936'
        },
        'analyst': {
            'name': '🧮 Analyst AI',
            'role': 'Execute analysis tasks and modeling',
            'color': '#38b2ac'
        }
    }
    
    def __init__(self):
        """Initialize chat interface"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = {
                'manager': [],
                'reviewer': [],
                'associate': [],
                'analyst': []
            }
        if 'active_teammate' not in st.session_state:
            st.session_state.active_teammate = 'manager'
    
    def render_sidebar_chat(self, context: Optional[Dict] = None):
        """Render chat interface in sidebar"""
        
        st.sidebar.markdown("---")
        st.sidebar.header("💬 AI Teammate Chat")
        
        # Teammate selector
        teammate = st.sidebar.selectbox(
            "Chat with:",
            options=list(self.AI_TEAMMATES.keys()),
            format_func=lambda x: self.AI_TEAMMATES[x]['name'],
            key="teammate_selector"
        )
        st.session_state.active_teammate = teammate
        
        # Show teammate info
        teammate_info = self.AI_TEAMMATES[teammate]
        st.sidebar.caption(f"Role: {teammate_info['role']}")
        
        # Chat history container
        chat_container = st.sidebar.container()
        with chat_container:
            self._display_chat_history(teammate)
        
        # Input area
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            user_message = st.text_input(
                "Message:",
                key=f"chat_input_{teammate}",
                placeholder="Ask a question..."
            )
        with col2:
            send_button = st.button("Send", key=f"send_{teammate}")
        
        if send_button and user_message:
            # Add user message to history
            self._add_message(teammate, 'user', user_message)
            
            # Get AI response (simulated for now)
            response = self._get_ai_response(teammate, user_message, context)
            self._add_message(teammate, teammate, response)
            
            # Clear input and rerun
            st.rerun()
        
        # Action buttons
        st.sidebar.markdown("---")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("📋 Send Plan", key=f"send_plan_{teammate}"):
                self._send_to_teammate(teammate, 'plan', context)
        
        with col2:
            if st.button("🔄 Clear Chat", key=f"clear_{teammate}"):
                st.session_state.chat_history[teammate] = []
                st.rerun()
    
    def render_main_chat(self, context: Optional[Dict] = None):
        """Render full chat interface in main area"""
        
        st.header("💬 AI Teammate Collaboration")
        
        # Teammate tabs
        tabs = st.tabs([self.AI_TEAMMATES[t]['name'] for t in self.AI_TEAMMATES.keys()])
        
        for i, (teammate_id, teammate_info) in enumerate(self.AI_TEAMMATES.items()):
            with tabs[i]:
                self._render_teammate_chat(teammate_id, teammate_info, context)
    
    def _render_teammate_chat(self, teammate_id: str, teammate_info: Dict, context: Optional[Dict]):
        """Render individual teammate chat"""
        
        # Chat header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {teammate_info['name']}")
            st.caption(teammate_info['role'])
        with col2:
            if st.button("Clear History", key=f"clear_main_{teammate_id}"):
                st.session_state.chat_history[teammate_id] = []
                st.rerun()
        
        # Chat history
        chat_container = st.container()
        with chat_container:
            self._display_chat_history(teammate_id, height=400)
        
        # Input area
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            message = st.text_input(
                "Your message:",
                key=f"main_chat_input_{teammate_id}",
                placeholder=f"Ask {teammate_info['name'].split()[0]} a question..."
            )
        
        with col2:
            if st.button("Send", type="primary", key=f"main_send_{teammate_id}"):
                if message:
                    self._add_message(teammate_id, 'user', message)
                    response = self._get_ai_response(teammate_id, message, context)
                    self._add_message(teammate_id, teammate_id, response)
                    st.rerun()
        
        with col3:
            # Quick actions dropdown
            action = st.selectbox(
                "Quick Action",
                ["", "Request Review", "Ask for Suggestions", "Send Context"],
                key=f"action_{teammate_id}"
            )
            
            if action:
                self._handle_quick_action(teammate_id, action, context)
    
    def _display_chat_history(self, teammate: str, height: Optional[int] = None):
        """Display chat history for a teammate"""
        
        history = st.session_state.chat_history[teammate]
        
        if not history:
            st.info("No messages yet. Start a conversation!")
            return
        
        # Create scrollable container
        if height:
            container_style = f"height: {height}px; overflow-y: auto;"
        else:
            container_style = "max-height: 300px; overflow-y: auto;"
        
        st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)
        
        for msg in history:
            if msg['role'] == 'user':
                # User message (right-aligned)
                st.markdown(
                    f"""
                    <div style='text-align: right; margin: 10px 0;'>
                        <div style='display: inline-block; background: #e3f2fd; 
                                    padding: 10px; border-radius: 10px; max-width: 70%;'>
                            <strong>You:</strong><br/>{msg['content']}
                            <br/><small style='color: #666;'>{msg['timestamp']}</small>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                # AI message (left-aligned)
                color = self.AI_TEAMMATES[teammate]['color']
                name = self.AI_TEAMMATES[teammate]['name']
                st.markdown(
                    f"""
                    <div style='text-align: left; margin: 10px 0;'>
                        <div style='display: inline-block; background: {color}20; 
                                    padding: 10px; border-radius: 10px; max-width: 70%;
                                    border-left: 3px solid {color};'>
                            <strong>{name}:</strong><br/>{msg['content']}
                            <br/><small style='color: #666;'>{msg['timestamp']}</small>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _add_message(self, teammate: str, role: str, content: str):
        """Add message to chat history"""
        
        st.session_state.chat_history[teammate].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().strftime("%H:%M")
        })
        
        # Keep only last 50 messages per teammate
        if len(st.session_state.chat_history[teammate]) > 50:
            st.session_state.chat_history[teammate].pop(0)
    
    def _get_ai_response(self, teammate: str, message: str, context: Optional[Dict]) -> str:
        """Get response from AI teammate"""
        
        try:
            if teammate == 'manager':
                # Import and use actual AI Manager
                from backend.ai_teammates.manager import AIManager
                manager = AIManager()
                return manager.chat(message, context)
            
            elif teammate == 'reviewer':
                # Simulated reviewer response
                return self._simulate_reviewer_response(message, context)
            
            elif teammate == 'associate':
                # Simulated associate response
                return self._simulate_associate_response(message, context)
            
            elif teammate == 'analyst':
                # Simulated analyst response
                return self._simulate_analyst_response(message, context)
            
        except Exception as e:
            return f"I'm having trouble processing your request. Error: {str(e)}"
    
    def _simulate_reviewer_response(self, message: str, context: Optional[Dict]) -> str:
        """Simulate Reviewer AI response"""
        
        responses = {
            'review': "I'll review your plan for completeness and best practices. Let me analyze...",
            'validate': "Validating the plan structure and checking for potential issues...",
            'suggest': "Based on my analysis, here are my suggestions for improvement...",
            'default': "I'm the Reviewer AI. I can help validate your plan and suggest improvements. How can I assist?"
        }
        
        message_lower = message.lower()
        for key in responses:
            if key in message_lower:
                return responses[key]
        
        return responses['default']
    
    def _simulate_associate_response(self, message: str, context: Optional[Dict]) -> str:
        """Simulate Associate AI response"""
        
        responses = {
            'data': "I can help you understand your data better. Let me analyze the structure...",
            'quality': "I'll assess the data quality and identify any issues that need attention...",
            'prepare': "I'll prepare the data for analysis by handling missing values and outliers...",
            'default': "I'm the Associate AI. I handle data understanding and preparation. What would you like to know?"
        }
        
        message_lower = message.lower()
        for key in responses:
            if key in message_lower:
                return responses[key]
        
        return responses['default']
    
    def _simulate_analyst_response(self, message: str, context: Optional[Dict]) -> str:
        """Simulate Analyst AI response"""
        
        responses = {
            'model': "I can help you choose and train the right models for your analysis...",
            'analyze': "I'll perform the statistical analysis and generate insights...",
            'visualize': "I'll create visualizations to help understand the patterns in your data...",
            'default': "I'm the Analyst AI. I execute analysis tasks and build models. How can I help?"
        }
        
        message_lower = message.lower()
        for key in responses:
            if key in message_lower:
                return responses[key]
        
        return responses['default']
    
    def _send_to_teammate(self, teammate: str, content_type: str, context: Optional[Dict]):
        """Send specific content to teammate"""
        
        if content_type == 'plan' and context and 'plan' in context:
            message = f"Please review this analysis plan:\n```\n{json.dumps(context['plan'], indent=2)[:500]}...\n```"
            self._add_message(teammate, 'user', message)
            response = self._get_ai_response(teammate, message, context)
            self._add_message(teammate, teammate, response)
            st.rerun()
    
    def _handle_quick_action(self, teammate: str, action: str, context: Optional[Dict]):
        """Handle quick action selection"""
        
        action_messages = {
            "Request Review": "Please review the current plan and provide your feedback.",
            "Ask for Suggestions": "What improvements would you suggest for this analysis?",
            "Send Context": f"Here's the current context: {json.dumps(context, indent=2)[:200] if context else 'No context available'}"
        }
        
        if action in action_messages:
            message = action_messages[action]
            self._add_message(teammate, 'user', message)
            response = self._get_ai_response(teammate, message, context)
            self._add_message(teammate, teammate, response)
            st.rerun()