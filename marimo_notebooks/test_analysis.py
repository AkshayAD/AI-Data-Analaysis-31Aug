import marimo as mo

app = mo.App()

@app.cell
def __():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    return pd, np, plt, sns

@app.cell
def __(pd):
    # Load data
    df = pd.read_csv('data/sample/customer_purchases.csv')
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    df.head()
    return df,

@app.cell
def __(df):
    # Basic info
    mo.md(f"""
    ## Dataset Overview
    - **Rows**: {len(df)}
    - **Columns**: {len(df.columns)}
    - **Missing values**: {df.isnull().sum().sum()}
    """)
    return

@app.cell
def __(df):
    # Summary statistics
    mo.md("## Summary Statistics")
    return

@app.cell
def __(df):
    df.describe()
    return

@app.cell
def __(df, plt):
    # Visualizations
    mo.md("## Data Visualizations")
    return

@app.cell
def __(df, plt, sns):
    # Correlation heatmap for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 8))
        correlation = df[numeric_cols].corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)
        plt.title('Correlation Heatmap')
        plt.tight_layout()
        plt.show()
    return numeric_cols,

@app.cell
def __(df, numeric_cols, plt):
    # Distribution plots
    if len(numeric_cols) > 0:
        fig, axes = plt.subplots(1, min(3, len(numeric_cols)), figsize=(15, 5))
        if len(numeric_cols) == 1:
            axes = [axes]
        for i, col in enumerate(numeric_cols[:3]):
            axes[i].hist(df[col], bins=20, edgecolor='black')
            axes[i].set_title(f'Distribution of {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Frequency')
        plt.tight_layout()
        plt.show()
    return

@app.cell
def __(df):
    # Interactive data exploration
    mo.md("## Interactive Exploration")
    return

@app.cell
def __(df):
    # Show data types
    mo.md("### Data Types")
    return

@app.cell
def __(df):
    df.dtypes
    return

if __name__ == "__main__":
    app.run()
