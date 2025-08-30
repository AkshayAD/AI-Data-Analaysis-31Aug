import marimo as mo
import subprocess
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
import tempfile
import logging

logger = logging.getLogger(__name__)


class NotebookRunner:
    """Simple Marimo notebook runner - no over-engineering"""
    
    def __init__(self, notebook_dir: Optional[Path] = None):
        self.notebook_dir = notebook_dir or Path("marimo_notebooks")
        self.notebook_dir.mkdir(exist_ok=True)
    
    def run_notebook(self, notebook_path: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a Marimo notebook with given inputs"""
        try:
            notebook_path = Path(notebook_path)
            if not notebook_path.exists():
                # Check in notebook directory
                notebook_path = self.notebook_dir / notebook_path
                if not notebook_path.exists():
                    return {'error': f'Notebook not found: {notebook_path}'}
            
            # For Phase 1: Simple execution using marimo CLI
            # In real implementation, we'd use marimo's Python API
            result = self._execute_notebook_cli(notebook_path, inputs)
            return result
            
        except Exception as e:
            logger.error(f"Failed to run notebook: {e}")
            return {'error': str(e)}
    
    def _execute_notebook_cli(self, notebook_path: Path, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute notebook using CLI (simplified for Phase 1)"""
        try:
            # Create a temporary file for inputs if provided
            input_file = None
            if inputs:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(inputs, f)
                    input_file = f.name
            
            # Run the notebook
            cmd = ['marimo', 'run', str(notebook_path)]
            if input_file:
                cmd.extend(['--args', input_file])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout for Phase 1
            )
            
            # Clean up input file
            if input_file:
                Path(input_file).unlink(missing_ok=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'notebook': str(notebook_path)
                }
            else:
                return {
                    'error': f'Notebook execution failed: {result.stderr}'
                }
                
        except subprocess.TimeoutExpired:
            return {'error': 'Notebook execution timed out'}
        except Exception as e:
            return {'error': str(e)}
    
    def create_notebook(self, name: str, cells: List[str]) -> Path:
        """Create a simple Marimo notebook from code cells"""
        notebook_path = self.notebook_dir / f"{name}.py"
        
        # Create a basic Marimo notebook structure
        notebook_content = [
            "import marimo as mo",
            "",
            "app = mo.App()",
            ""
        ]
        
        # Add cells
        for i, cell_code in enumerate(cells):
            notebook_content.append(f"@app.cell")
            notebook_content.append(f"def cell_{i}():")
            # Indent cell code
            for line in cell_code.split('\n'):
                notebook_content.append(f"    {line}")
            notebook_content.append(f"    return")
            notebook_content.append("")
        
        # Add main
        notebook_content.append("if __name__ == '__main__':")
        notebook_content.append("    app.run()")
        
        # Write notebook
        notebook_path.write_text('\n'.join(notebook_content))
        
        return notebook_path