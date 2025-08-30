import pytest
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "python"))

from marimo_integration import NotebookBuilder, NotebookRunner


def test_notebook_builder_basic():
    """Test basic notebook building"""
    builder = NotebookBuilder()
    builder.add_import("import numpy as np")
    builder.add_cell("x = 5")
    builder.add_cell("print(x)")
    
    content = builder.build()
    
    assert "import marimo as mo" in content
    assert "import numpy as np" in content
    assert "x = 5" in content
    assert "print(x)" in content
    assert "@app.cell" in content


def test_notebook_builder_markdown():
    """Test adding markdown cells"""
    builder = NotebookBuilder()
    builder.add_markdown("# Test Notebook")
    builder.add_markdown("This is a test")
    
    content = builder.build()
    
    assert 'mo.md("""# Test Notebook""")' in content
    assert 'mo.md("""This is a test""")' in content


def test_notebook_builder_data_load():
    """Test adding data load cell"""
    builder = NotebookBuilder()
    builder.add_data_load("df", "data.csv")
    
    content = builder.build()
    
    assert "import pandas as pd" in content
    assert "df = pd.read_csv('data.csv')" in content
    assert "df.head()" in content


def test_notebook_builder_plot():
    """Test adding plot cells"""
    builder = NotebookBuilder()
    
    # Test scatter plot
    builder.add_plot("df", plot_type="scatter", x="col1", y="col2")
    content = builder.build()
    assert "plt.scatter" in content
    assert "col1" in content
    assert "col2" in content
    
    # Test histogram
    builder = NotebookBuilder()
    builder.add_plot("df", plot_type="histogram", column="values")
    content = builder.build()
    assert "plt.hist" in content
    assert "values" in content


def test_notebook_builder_save():
    """Test saving notebook to file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        builder = NotebookBuilder()
        builder.add_cell("x = 10")
        builder.add_cell("print(x)")
        
        notebook_path = Path(tmpdir) / "test_notebook.py"
        saved_path = builder.save(notebook_path)
        
        assert saved_path.exists()
        content = saved_path.read_text()
        assert "x = 10" in content
        assert "print(x)" in content


def test_notebook_runner_creation():
    """Test creating notebook runner"""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = NotebookRunner(Path(tmpdir))
        assert runner.notebook_dir == Path(tmpdir)
        
        # Test default directory
        runner = NotebookRunner()
        assert runner.notebook_dir.name == "marimo_notebooks"


def test_notebook_runner_create_notebook():
    """Test creating notebook through runner"""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = NotebookRunner(Path(tmpdir))
        
        cells = [
            "x = 5",
            "y = x * 2",
            "print(f'Result: {y}')"
        ]
        
        notebook_path = runner.create_notebook("test", cells)
        
        assert notebook_path.exists()
        assert notebook_path.name == "test.py"
        
        content = notebook_path.read_text()
        assert "x = 5" in content
        assert "y = x * 2" in content
        assert "@app.cell" in content


def test_notebook_runner_nonexistent_notebook():
    """Test running non-existent notebook"""
    runner = NotebookRunner()
    result = runner.run_notebook("nonexistent.py")
    
    assert 'error' in result
    assert 'not found' in result['error'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])