"""
Stage 0: Input & Objectives with Gemini API Configuration
Enhanced with real API integration and model selection
"""

import streamlit as st
from pathlib import Path
import sys
import json
import os
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import hashlib

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from components.FileUploader import FileUploader
from components.ObjectiveInput import ObjectiveInput

class InputObjectivePage:
    """Enhanced Input & Objectives page with Gemini API configuration"""
    
    def __init__(self):
        """Initialize the page with session state"""
        # Initialize core components
        self.file_uploader = FileUploader()
        self.objective_input = ObjectiveInput()
        
        # Initialize session state for API configuration
        if 'gemini_api_key' not in st.session_state:
            st.session_state.gemini_api_key = ""
        
        if 'gemini_model' not in st.session_state:
            st.session_state.gemini_model = "gemini-2.0-flash"
        
        if 'api_configured' not in st.session_state:
            st.session_state.api_configured = False
            
        if 'uploaded_data' not in st.session_state:
            st.session_state.uploaded_data = {}
            
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = []
    
    def render(self):
        """Render the main page"""
        # Header with configuration status
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h1>🚀 AI-Powered Data Analysis Platform</h1>
                <p style='font-size: 1.1rem; color: #666;'>Human-in-the-Loop Intelligence for Better Insights</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.session_state.api_configured:
                st.success("🔑 API Connected")
            else:
                st.warning("⚠️ API Not Configured")
        
        # Progress indicator
        self._render_progress_indicator()
        
        # API Configuration Section (Always Visible)
        with st.expander("🔑 Gemini API Configuration", expanded=not st.session_state.api_configured):
            self._render_api_configuration()
        
        # Main content - only show if API is configured
        if st.session_state.api_configured:
            # Tabs for different input sections
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Objectives", "📁 Data Upload", "✅ Review & Proceed", "🔍 System Status"])
            
            with tab1:
                self._render_objectives_tab()
            
            with tab2:
                self._render_data_upload_tab()
            
            with tab3:
                self._render_review_tab()
                
            with tab4:
                self._render_status_tab()
        else:
            st.info("👆 Please configure your Gemini API key above to continue")
        
        # Sidebar with help and real-time status
        self._render_sidebar()
    
    def _render_api_configuration(self):
        """Render API configuration section"""
        col1, col2 = st.columns(2)
        
        with col1:
            # API Key Input
            api_key = st.text_input(
                "Enter your Gemini API Key",
                type="password",
                value=st.session_state.gemini_api_key,
                help="Get your API key from https://makersuite.google.com/app/apikey"
            )
            
            if api_key != st.session_state.gemini_api_key:
                st.session_state.gemini_api_key = api_key
                st.session_state.api_configured = False
        
        with col2:
            # Model Selection with Latest Models
            available_models = {
                "gemini-2.0-flash": "Gemini 2.0 Flash (Recommended - Fast & Efficient)",
                "gemini-2.0-flash-thinking-exp": "Gemini 2.0 Flash Thinking (Advanced Reasoning)",
                "gemini-2.5-flash": "Gemini 2.5 Flash (Latest - Default)",
                "gemini-2.5-pro": "Gemini 2.5 Pro (Most Capable)",
                "gemini-1.5-flash": "Gemini 1.5 Flash (Legacy)",
                "gemini-1.5-pro": "Gemini 1.5 Pro (Legacy)"
            }
            
            selected_model = st.selectbox(
                "Select Gemini Model",
                options=list(available_models.keys()),
                format_func=lambda x: available_models[x],
                index=list(available_models.keys()).index(st.session_state.gemini_model),
                help="Choose the model based on your needs. 2.5 Flash is recommended for most use cases."
            )
            
            if selected_model != st.session_state.gemini_model:
                st.session_state.gemini_model = selected_model
        
        # Test API Connection
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔌 Test Connection", type="primary"):
                if api_key:
                    with st.spinner("Testing API connection..."):
                        success, message = self._test_api_connection(api_key, selected_model)
                        if success:
                            st.success(message)
                            st.session_state.api_configured = True
                        else:
                            st.error(message)
                            st.session_state.api_configured = False
                else:
                    st.error("Please enter an API key first")
        
        with col2:
            if st.button("💾 Save Configuration"):
                if api_key:
                    self._save_api_config(api_key, selected_model)
                    st.success("Configuration saved!")
                else:
                    st.error("Please enter an API key first")
        
        with col3:
            if st.session_state.api_configured:
                st.info(f"✅ Connected to {selected_model}")
    
    def _test_api_connection(self, api_key: str, model: str) -> tuple[bool, str]:
        """Test the Gemini API connection"""
        try:
            # Configure the API
            genai.configure(api_key=api_key)
            
            # Try to initialize the model
            model_instance = genai.GenerativeModel(model)
            
            # Send a simple test prompt
            response = model_instance.generate_content("Say 'API Connected' if you can read this.")
            
            if response and response.text:
                return True, f"✅ Successfully connected to {model}"
            else:
                return False, "❌ API responded but no content generated"
                
        except Exception as e:
            return False, f"❌ Connection failed: {str(e)}"
    
    def _save_api_config(self, api_key: str, model: str):
        """Save API configuration to file (hashed for security)"""
        config_dir = Path(__file__).parent.parent.parent / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Hash the API key for storage (never store plain text)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        
        config = {
            "model": model,
            "key_hash": key_hash,
            "configured_at": datetime.now().isoformat()
        }
        
        with open(config_dir / "api_config.json", "w") as f:
            json.dump(config, f, indent=2)
    
    def _render_objectives_tab(self):
        """Render objectives input tab"""
        st.header("📝 Define Your Analysis Objective")
        
        # Use the ObjectiveInput component but store in session state
        objective_data = self.objective_input.render()
        
        if objective_data:
            st.session_state.analysis_objective = objective_data
            
        # Show current objective if set
        if 'analysis_objective' in st.session_state:
            with st.expander("Current Objective", expanded=False):
                st.json(st.session_state.analysis_objective)
    
    def _render_data_upload_tab(self):
        """Render data upload tab with real file processing"""
        st.header("📁 Upload Your Data Files")
        
        uploaded_files = st.file_uploader(
            "Choose files to analyze",
            accept_multiple_files=True,
            type=['csv', 'xlsx', 'json', 'txt', 'pdf', 'parquet'],
            help="Upload your data files. Multiple formats supported."
        )
        
        if uploaded_files:
            for file in uploaded_files:
                if file.name not in st.session_state.processed_files:
                    with st.spinner(f"Processing {file.name}..."):
                        processed_data = self._process_uploaded_file(file)
                        if processed_data:
                            st.session_state.uploaded_data[file.name] = processed_data
                            st.session_state.processed_files.append(file.name)
                            st.success(f"✅ {file.name} processed successfully")
        
        # Display processed files
        if st.session_state.uploaded_data:
            st.subheader("Processed Files")
            for filename, data in st.session_state.uploaded_data.items():
                with st.expander(f"📄 {filename}"):
                    st.write(f"**Type:** {data['type']}")
                    st.write(f"**Size:** {data['size']} bytes")
                    if data['type'] == 'dataframe':
                        st.write(f"**Rows:** {data['rows']}, **Columns:** {data['columns']}")
                        st.write("**Preview:**")
                        st.dataframe(data['preview'], use_container_width=True)
                    elif data['type'] == 'text':
                        st.write(f"**Length:** {data['length']} characters")
                        st.text(data['preview'][:500])
    
    def _process_uploaded_file(self, file):
        """Actually process the uploaded file and extract data"""
        try:
            file_data = {
                'name': file.name,
                'size': file.size,
                'uploaded_at': datetime.now().isoformat()
            }
            
            # Process based on file type
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
                file_data.update({
                    'type': 'dataframe',
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'preview': df.head(10),
                    'data': df  # Store full dataframe
                })
                
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
                file_data.update({
                    'type': 'dataframe',
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'preview': df.head(10),
                    'data': df
                })
                
            elif file.name.endswith('.json'):
                content = json.load(file)
                file_data.update({
                    'type': 'json',
                    'preview': content,
                    'data': content
                })
                
            else:
                # Text files
                content = file.read().decode('utf-8')
                file_data.update({
                    'type': 'text',
                    'length': len(content),
                    'preview': content[:1000],
                    'data': content
                })
            
            return file_data
            
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
            return None
    
    def _render_review_tab(self):
        """Render review and proceed tab"""
        st.header("✅ Review Your Input")
        
        # Check readiness
        ready = True
        issues = []
        
        if not st.session_state.api_configured:
            ready = False
            issues.append("❌ API not configured")
        
        if not st.session_state.get('analysis_objective'):
            ready = False
            issues.append("❌ No analysis objective defined")
        
        if not st.session_state.uploaded_data:
            ready = False
            issues.append("❌ No data files uploaded")
        
        # Display status
        if ready:
            st.success("✅ All requirements met! Ready to proceed.")
            
            # Show summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Configuration")
                st.write(f"**Model:** {st.session_state.gemini_model}")
                st.write(f"**API Status:** Connected ✅")
                
                if 'analysis_objective' in st.session_state:
                    st.subheader("Objective")
                    obj = st.session_state.analysis_objective
                    st.write(f"**Goal:** {obj.get('objective', 'Not set')}")
                    st.write(f"**Type:** {obj.get('analysis_type', 'Not set')}")
            
            with col2:
                st.subheader("Data Files")
                for filename in st.session_state.uploaded_data:
                    st.write(f"✅ {filename}")
            
            # Proceed button
            if st.button("🚀 Generate Analysis Plan", type="primary", use_container_width=True):
                # Save all context for next stage
                self._save_complete_context()
                st.session_state.current_stage = 1
                st.success("✅ Moving to Plan Generation...")
                st.balloons()
                st.rerun()
        else:
            st.warning("⚠️ Please complete all requirements before proceeding")
            for issue in issues:
                st.write(issue)
    
    def _render_status_tab(self):
        """Render system status showing what's real vs mock"""
        st.header("🔍 System Status & Transparency")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Working Features")
            st.write("• API Configuration: **Real**")
            st.write("• File Upload: **Real**")
            st.write("• Data Processing: **Real**")
            st.write("• Navigation: **Real**")
            st.write("• Session State: **Real**")
            
        with col2:
            st.subheader("🚧 In Development")
            st.write("• Advanced Analytics: **Partial**")
            st.write("• Export Functions: **Partial**")
            st.write("• Real-time Updates: **Planned**")
            st.write("• Team Collaboration: **Planned**")
        
        # Data Pipeline Status
        st.subheader("📊 Data Pipeline Status")
        pipeline_status = {
            "Upload": "✅ Working",
            "Processing": "✅ Working",
            "Storage": "✅ Session-based",
            "Analysis": "🚧 Implementing",
            "Export": "🚧 Implementing"
        }
        
        for stage, status in pipeline_status.items():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(f"**{stage}:**")
            with col2:
                st.write(status)
        
        # Show raw session state for debugging
        if st.checkbox("Show Session State (Debug)"):
            st.json({
                "api_configured": st.session_state.api_configured,
                "model": st.session_state.gemini_model,
                "files_uploaded": len(st.session_state.uploaded_data),
                "objective_set": 'analysis_objective' in st.session_state,
                "current_stage": st.session_state.get('current_stage', 0)
            })
    
    def _render_progress_indicator(self):
        """Render progress indicator"""
        stages = [
            ("Input & Objectives", True),  # Current stage
            ("Plan Generation", False),
            ("Data Understanding", False),
            ("Task Configuration", False),
            ("Execution", False),
            ("Review & Export", False)
        ]
        
        cols = st.columns(len(stages))
        for i, (stage_name, active) in enumerate(stages):
            with cols[i]:
                if i == 0:  # Current stage
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem; 
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; border-radius: 10px;'>
                        <strong>Step {i+1}</strong><br>{stage_name}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem; 
                                background: #e0e0e0; border-radius: 10px;'>
                        <small>Step {i+1}</small><br>{stage_name}
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Render sidebar with real-time status and help"""
        with st.sidebar:
            st.header("🔍 Real-Time Status")
            
            # API Status
            if st.session_state.api_configured:
                st.success("🔑 API: Connected")
                st.caption(f"Model: {st.session_state.gemini_model}")
            else:
                st.error("🔑 API: Not Connected")
            
            # Data Status
            if st.session_state.uploaded_data:
                st.success(f"📁 Files: {len(st.session_state.uploaded_data)}")
                for filename in st.session_state.uploaded_data:
                    st.caption(f"• {filename}")
            else:
                st.warning("📁 Files: None")
            
            # Objective Status
            if 'analysis_objective' in st.session_state:
                st.success("📝 Objective: Set")
            else:
                st.warning("📝 Objective: Not Set")
            
            st.divider()
            
            # Help Section
            with st.expander("📚 Help & Tips"):
                st.write("""
                **Getting Started:**
                1. Enter your Gemini API key
                2. Select your preferred model
                3. Test the connection
                4. Define your analysis objective
                5. Upload your data files
                6. Review and proceed
                
                **Model Selection Guide:**
                - **2.5 Flash**: Best for most use cases (default)
                - **2.5 Pro**: For complex reasoning tasks
                - **2.0 Flash**: Fast and efficient
                - **2.0 Flash Thinking**: Advanced reasoning
                """)
    
    def _save_complete_context(self):
        """Save all context for next stages"""
        context = {
            "api_config": {
                "model": st.session_state.gemini_model,
                "configured": st.session_state.api_configured
            },
            "objective": st.session_state.get('analysis_objective', {}),
            "files": {
                name: {
                    "type": data['type'],
                    "size": data['size'],
                    "rows": data.get('rows', 0),
                    "columns": data.get('columns', 0)
                }
                for name, data in st.session_state.uploaded_data.items()
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file for persistence
        context_file = Path(__file__).parent.parent.parent / "data" / "analysis_context.json"
        context_file.parent.mkdir(exist_ok=True)
        
        with open(context_file, "w") as f:
            json.dump(context, f, indent=2)
        
        # Also keep in session state
        st.session_state.analysis_context = context

# Main execution
def main():
    page = InputObjectivePage()
    page.render()

if __name__ == "__main__":
    main()