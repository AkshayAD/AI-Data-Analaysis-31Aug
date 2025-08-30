#!/usr/bin/env python3
"""
Simple CLI for AI Data Analysis Team
Phase 1: Basic functionality only
"""

import click
import json
import logging
from pathlib import Path
from typing import Optional

from agents import DataAnalysisAgent
from marimo_integration import NotebookRunner, NotebookBuilder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
def cli(debug):
    """AI Data Analysis Team - Simple CLI for Phase 1"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.argument('data_path', type=click.Path(exists=True))
@click.option('--task-type', type=click.Choice(['analyze', 'summary', 'clean']), default='analyze')
@click.option('--output', type=click.Path(), help='Output path for results')
def analyze(data_path, task_type, output):
    """Run data analysis on a file"""
    agent = DataAnalysisAgent()
    
    task = {
        'type': task_type,
        'data_path': data_path
    }
    
    if output and task_type == 'clean':
        task['output_path'] = output
    
    click.echo(f"Running {task_type} on {data_path}...")
    result = agent.execute(task)
    
    if 'error' in result:
        click.echo(f"Error: {result['error']}", err=True)
        return
    
    # Pretty print results
    click.echo(json.dumps(result, indent=2))
    
    # Save to file if output specified
    if output and task_type != 'clean':
        Path(output).write_text(json.dumps(result, indent=2))
        click.echo(f"Results saved to {output}")


@cli.command()
@click.argument('notebook_path', type=click.Path())
@click.option('--inputs', type=click.Path(exists=True), help='JSON file with inputs')
def run_notebook(notebook_path, inputs):
    """Run a Marimo notebook"""
    runner = NotebookRunner()
    
    input_data = None
    if inputs:
        input_data = json.loads(Path(inputs).read_text())
    
    click.echo(f"Running notebook {notebook_path}...")
    result = runner.run_notebook(notebook_path, input_data)
    
    if 'error' in result:
        click.echo(f"Error: {result['error']}", err=True)
    else:
        click.echo("Notebook executed successfully!")
        if 'output' in result:
            click.echo(result['output'])


@cli.command()
@click.argument('name')
@click.argument('data_path', type=click.Path(exists=True))
@click.option('--plot-type', type=click.Choice(['scatter', 'histogram']), default='histogram')
@click.option('--column', help='Column for histogram')
@click.option('--x', help='X column for scatter plot')
@click.option('--y', help='Y column for scatter plot')
def create_notebook(name, data_path, plot_type, column, x, y):
    """Create a simple analysis notebook"""
    builder = NotebookBuilder()
    
    # Add data loading
    builder.add_markdown(f"# Analysis Notebook: {name}")
    builder.add_import("import pandas as pd")
    builder.add_import("import numpy as np")
    builder.add_data_load("df", data_path)
    
    # Add basic info
    builder.add_cell("df.info()")
    builder.add_cell("df.describe()")
    
    # Add plot based on type
    if plot_type == 'histogram' and column:
        builder.add_plot("df", plot_type="histogram", column=column)
    elif plot_type == 'scatter' and x and y:
        builder.add_plot("df", plot_type="scatter", x=x, y=y)
    
    # Save notebook
    notebook_path = Path(f"marimo_notebooks/{name}.py")
    builder.save(notebook_path)
    
    click.echo(f"Notebook created: {notebook_path}")
    click.echo("Run it with: marimo run " + str(notebook_path))


@cli.command()
def quickstart():
    """Quick start guide and setup check"""
    click.echo("=== AI Data Analysis Team - Quick Start ===")
    click.echo()
    
    # Check installations
    checks = []
    try:
        import marimo
        checks.append("✓ Marimo installed")
    except ImportError:
        checks.append("✗ Marimo not installed - run: pip install marimo")
    
    try:
        import pandas
        checks.append("✓ Pandas installed")
    except ImportError:
        checks.append("✗ Pandas not installed - run: pip install pandas")
    
    for check in checks:
        click.echo(check)
    
    click.echo()
    click.echo("Example commands:")
    click.echo("  1. Analyze data: python cli.py analyze data.csv")
    click.echo("  2. Create notebook: python cli.py create-notebook my_analysis data.csv --column price")
    click.echo("  3. Run notebook: python cli.py run-notebook my_notebook.py")
    click.echo()
    click.echo("For more help: python cli.py --help")


if __name__ == '__main__':
    cli()