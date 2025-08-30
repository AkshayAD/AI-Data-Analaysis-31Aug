import pytest
import tempfile
from pathlib import Path
import pandas as pd
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "python"))

from agents import DataAnalysisAgent, BaseAgent
from agents.base import AgentConfig


def test_agent_config():
    """Test agent configuration"""
    config = AgentConfig(name="TestAgent", description="Test", max_retries=5)
    assert config.name == "TestAgent"
    assert config.max_retries == 5


def test_data_analysis_agent_creation():
    """Test creating a data analysis agent"""
    agent = DataAnalysisAgent()
    assert agent.config.name == "DataAnalysisAgent"
    assert isinstance(agent, BaseAgent)


def test_data_analysis_agent_analyze():
    """Test data analysis functionality"""
    # Create test data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name,age,score\n")
        f.write("Alice,25,85\n")
        f.write("Bob,30,90\n")
        f.write("Charlie,35,78\n")
        test_file = f.name
    
    try:
        agent = DataAnalysisAgent()
        result = agent.execute({
            'type': 'analyze',
            'data_path': test_file
        })
        
        assert 'success' in result
        assert result['success'] == True
        assert 'analysis' in result
        assert result['analysis']['shape'] == (3, 3)
        assert 'age' in result['analysis']['columns']
        
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_data_analysis_agent_summary():
    """Test data summary functionality"""
    # Create test data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("x,y\n")
        f.write("1,2\n")
        f.write("3,4\n")
        test_file = f.name
    
    try:
        agent = DataAnalysisAgent()
        result = agent.execute({
            'type': 'summary',
            'data_path': test_file
        })
        
        assert 'success' in result
        assert result['success'] == True
        assert 'summary' in result
        assert result['summary']['rows'] == 2
        assert result['summary']['columns'] == 2
        
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_data_analysis_agent_clean():
    """Test data cleaning functionality"""
    # Create test data with duplicates
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("a,b\n")
        f.write("1,2\n")
        f.write("1,2\n")  # Duplicate
        f.write("3,4\n")
        test_file = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        output_file = f.name
    
    try:
        agent = DataAnalysisAgent()
        result = agent.execute({
            'type': 'clean',
            'data_path': test_file,
            'output_path': output_file
        })
        
        assert 'success' in result
        assert result['success'] == True
        assert result['rows_removed'] == 1
        assert result['original_shape'] == (3, 2)
        assert result['cleaned_shape'] == (2, 2)
        
        # Check output file
        df = pd.read_csv(output_file)
        assert len(df) == 2
        
    finally:
        Path(test_file).unlink(missing_ok=True)
        Path(output_file).unlink(missing_ok=True)


def test_agent_state_management():
    """Test agent state management"""
    agent = DataAnalysisAgent()
    
    # Test setting state
    agent.set_state("key1", "value1")
    agent.set_state("key2", 42)
    
    state = agent.get_state()
    assert state["key1"] == "value1"
    assert state["key2"] == 42
    
    # Test clearing state
    agent.clear_state()
    state = agent.get_state()
    assert len(state) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])