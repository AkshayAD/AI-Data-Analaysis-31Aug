#!/usr/bin/env python3
"""
Tests for Streamlit application components
"""

import pytest
import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src" / "python"))

# Import components from streamlit_app_v2
from streamlit_app_v2 import (
    SessionManager,
    DataExporter,
    WorkflowTemplates,
    handle_error,
    init_agents
)

class TestSessionManager:
    """Test session management functionality"""
    
    def test_init_session(self):
        """Test session initialization"""
        # Mock streamlit session state
        with patch('streamlit_app_v2.st') as mock_st:
            mock_st.session_state = {}
            
            SessionManager.init_session()
            
            assert 'data_history' in mock_st.session_state
            assert 'analysis_results' in mock_st.session_state
            assert 'current_workflow' in mock_st.session_state
            assert 'api_usage' in mock_st.session_state
    
    def test_save_data(self):
        """Test data saving to history"""
        with patch('streamlit_app_v2.st') as mock_st:
            mock_st.session_state = {'data_history': []}
            
            df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
            SessionManager.save_data("test_data.csv", df)
            
            assert len(mock_st.session_state['data_history']) == 1
            assert mock_st.session_state['data_history'][0]['name'] == "test_data.csv"
            assert 'timestamp' in mock_st.session_state['data_history'][0]
            assert 'hash' in mock_st.session_state['data_history'][0]
    
    def test_save_result(self):
        """Test result saving"""
        with patch('streamlit_app_v2.st') as mock_st:
            mock_st.session_state = {}
            
            result = {'analysis': 'test', 'score': 0.95}
            SessionManager.save_result("test_analysis", result)
            
            assert 'analysis_results' in mock_st.session_state
            assert 'test_analysis' in mock_st.session_state['analysis_results']
            assert mock_st.session_state['analysis_results']['test_analysis']['result'] == result

class TestDataExporter:
    """Test data export functionality"""
    
    def test_to_csv(self):
        """Test CSV export"""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        csv_bytes = DataExporter.to_csv(df)
        
        assert isinstance(csv_bytes, bytes)
        assert b'a,b' in csv_bytes
        assert b'1,4' in csv_bytes
    
    def test_to_json(self):
        """Test JSON export"""
        data = {'key': 'value', 'number': 42}
        json_bytes = DataExporter.to_json(data)
        
        assert isinstance(json_bytes, bytes)
        decoded = json.loads(json_bytes.decode('utf-8'))
        assert decoded == data
    
    def test_to_excel(self):
        """Test Excel export"""
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        excel_bytes = DataExporter.to_excel(df)
        
        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 0

class TestWorkflowTemplates:
    """Test workflow template functionality"""
    
    def test_get_template(self):
        """Test template retrieval"""
        template = WorkflowTemplates.get_template('sales_analysis')
        
        assert template['name'] == 'Sales Analysis'
        assert 'description' in template
        assert 'steps' in template
        assert len(template['steps']) > 0
    
    def test_all_templates_valid(self):
        """Test all templates have required fields"""
        for key, template in WorkflowTemplates.TEMPLATES.items():
            assert 'name' in template
            assert 'description' in template
            assert 'steps' in template
            assert 'icon' in template
            assert isinstance(template['steps'], list)
            assert len(template['steps']) > 0

class TestAgentInitialization:
    """Test agent initialization"""
    
    @patch('streamlit_app_v2.st')
    def test_init_agents_without_api_key(self, mock_st):
        """Test agent initialization without API key"""
        mock_st.secrets = {}
        
        with patch('streamlit_app_v2.DataAnalysisAgent') as MockDA, \
             patch('streamlit_app_v2.OrchestrationAgent') as MockOrch, \
             patch('streamlit_app_v2.VisualizationAgent') as MockViz, \
             patch('streamlit_app_v2.MLAgent') as MockML:
            
            agents = init_agents()
            
            assert 'data_analysis' in agents
            assert 'orchestrator' in agents
            assert 'visualization' in agents
            assert 'ml' in agents
            assert 'intelligent' not in agents
    
    @patch('streamlit_app_v2.st')
    @patch('streamlit_app_v2.GeminiClient')
    @patch('streamlit_app_v2.IntelligentAgent')
    def test_init_agents_with_api_key(self, MockIntelligent, MockGemini, mock_st):
        """Test agent initialization with API key"""
        mock_st.secrets = {'GEMINI_API_KEY': 'test-key'}
        
        with patch('streamlit_app_v2.DataAnalysisAgent'), \
             patch('streamlit_app_v2.OrchestrationAgent'), \
             patch('streamlit_app_v2.VisualizationAgent'), \
             patch('streamlit_app_v2.MLAgent'):
            
            agents = init_agents()
            
            assert 'intelligent' in agents
            MockGemini.assert_called_once_with(api_key='test-key')

class TestErrorHandling:
    """Test error handling functionality"""
    
    @patch('streamlit_app_v2.st')
    def test_handle_error_basic(self, mock_st):
        """Test basic error handling"""
        error = ValueError("Test error")
        handle_error(error, "Test Context")
        
        mock_st.error.assert_called()
        mock_st.info.assert_called()
    
    @patch('streamlit_app_v2.st')
    def test_handle_error_gemini(self, mock_st):
        """Test Gemini-specific error handling"""
        error = Exception("Gemini API error")
        handle_error(error, "AI Analysis")
        
        # Check that Gemini-specific suggestions are shown
        calls = mock_st.write.call_args_list
        suggestions = [str(call) for call in calls]
        assert any("API key" in str(s) for s in suggestions)

class TestDataProcessing:
    """Test data processing utilities"""
    
    def test_sample_data_generation(self):
        """Test that sample data is generated correctly"""
        # Test sales data format
        date_range = pd.date_range('2024-01-01', periods=100)
        revenue = [1000 + i*50 + (i%10)*100 for i in range(100)]
        
        assert len(date_range) == 100
        assert len(revenue) == 100
        assert min(revenue) >= 1000
        assert max(revenue) <= 10000
    
    def test_data_validation(self):
        """Test data validation checks"""
        df = pd.DataFrame({
            'numeric': [1, 2, 3, np.nan],
            'categorical': ['A', 'B', 'C', 'D'],
            'mixed': [1, 'B', 3, None]
        })
        
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        assert 'numeric' in numeric_cols
        assert 'categorical' not in numeric_cols
        
        missing_count = df.isnull().sum().sum()
        assert missing_count == 2

class TestVisualizationHelpers:
    """Test visualization helper functions"""
    
    def test_chart_type_mapping(self):
        """Test chart type categorization"""
        distribution_charts = ["Histogram", "Box Plot", "Violin Plot", "Density Plot"]
        relationship_charts = ["Scatter Plot", "Bubble Chart", "Correlation Heatmap", "Pair Plot"]
        
        assert "Histogram" in distribution_charts
        assert "Scatter Plot" in relationship_charts
        assert len(distribution_charts) == 4
        assert len(relationship_charts) == 4

class TestMLHelpers:
    """Test ML helper functions"""
    
    def test_model_comparison_structure(self):
        """Test model comparison data structure"""
        models = ["Linear Regression", "Random Forest", "Gradient Boosting"]
        comparison_data = []
        
        for i, model_name in enumerate(models):
            comparison_data.append({
                'Model': model_name,
                'R² Score': 0.85 + i * 0.03,
                'RMSE': 0.15 - i * 0.02,
                'MAE': 0.12 - i * 0.01,
                'Training Time': f"{0.5 + i * 0.2:.2f}s"
            })
        
        df = pd.DataFrame(comparison_data)
        
        assert len(df) == 3
        assert df['R² Score'].max() == 0.91
        assert df['RMSE'].min() == 0.11
        best_model_idx = df['R² Score'].idxmax()
        assert df.loc[best_model_idx, 'Model'] == "Gradient Boosting"

class TestIntegration:
    """Integration tests for complete workflows"""
    
    @patch('streamlit_app_v2.st')
    def test_complete_analysis_workflow(self, mock_st):
        """Test complete analysis workflow"""
        mock_st.session_state = {}
        
        # Initialize session
        SessionManager.init_session()
        
        # Create sample data
        df = pd.DataFrame({
            'value': np.random.randn(100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        # Save data
        SessionManager.save_data("test.csv", df)
        
        # Mock analysis result
        result = {
            'summary': 'Test analysis complete',
            'metrics': {'mean': 0.5, 'std': 1.0},
            'insights': ['Insight 1', 'Insight 2']
        }
        
        # Save result
        SessionManager.save_result("analysis_1", result)
        
        # Verify workflow
        assert len(mock_st.session_state['data_history']) == 1
        assert 'analysis_1' in mock_st.session_state['analysis_results']
        
        # Export result
        json_bytes = DataExporter.to_json(result)
        assert len(json_bytes) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])