from typing import List, Dict, Any, Optional
from pathlib import Path
import marimo as mo


class NotebookBuilder:
    """Simple builder for creating Marimo notebooks programmatically"""
    
    def __init__(self):
        self.cells: List[str] = []
        self.imports: List[str] = []
    
    def add_import(self, import_statement: str) -> 'NotebookBuilder':
        """Add an import statement"""
        self.imports.append(import_statement)
        return self
    
    def add_cell(self, code: str) -> 'NotebookBuilder':
        """Add a code cell"""
        self.cells.append(code)
        return self
    
    def add_markdown(self, markdown: str) -> 'NotebookBuilder':
        """Add a markdown cell"""
        code = f'mo.md("""{markdown}""")'
        self.cells.append(code)
        return self
    
    def add_data_load(self, variable_name: str, file_path: str) -> 'NotebookBuilder':
        """Add a cell to load data"""
        code = f"""
import pandas as pd
{variable_name} = pd.read_csv('{file_path}')
{variable_name}.head()
"""
        self.cells.append(code.strip())
        return self
    
    def add_plot(self, data_var: str, plot_type: str = 'scatter', **kwargs) -> 'NotebookBuilder':
        """Add a simple plot cell"""
        if plot_type == 'scatter':
            x = kwargs.get('x', 'x')
            y = kwargs.get('y', 'y')
            code = f"""
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.scatter({data_var}['{x}'], {data_var}['{y}'])
plt.xlabel('{x}')
plt.ylabel('{y}')
plt.title('Scatter Plot: {x} vs {y}')
plt.show()
"""
        elif plot_type == 'histogram':
            column = kwargs.get('column', 'value')
            code = f"""
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.hist({data_var}['{column}'], bins=30, edgecolor='black')
plt.xlabel('{column}')
plt.ylabel('Frequency')
plt.title('Histogram: {column}')
plt.show()
"""
        else:
            code = f"# Unsupported plot type: {plot_type}"
        
        self.cells.append(code.strip())
        return self
    
    def build(self) -> str:
        """Build the notebook content"""
        content = []
        
        # Add imports
        content.append("import marimo as mo")
        for imp in self.imports:
            content.append(imp)
        content.append("")
        content.append("app = mo.App()")
        content.append("")
        
        # Add cells
        for i, cell_code in enumerate(self.cells):
            content.append(f"@app.cell")
            content.append(f"def cell_{i}():")
            # Indent cell code
            for line in cell_code.split('\n'):
                if line.strip():
                    content.append(f"    {line}")
            content.append(f"    return")
            content.append("")
        
        # Add main
        content.append("if __name__ == '__main__':")
        content.append("    app.run()")
        
        return '\n'.join(content)
    
    def save(self, file_path: Path) -> Path:
        """Save the notebook to a file"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(self.build())
        return file_path