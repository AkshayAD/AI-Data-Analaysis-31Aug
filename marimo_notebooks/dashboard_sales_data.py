import marimo as mo
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = mo.App()

@app.cell
def cell_0():
    mo.md("""# Interactive Dashboard""")
    return

@app.cell
def cell_1():
    import pandas as pd
    df = pd.read_csv('/root/repo/data/sample/sales_data.csv')
    df.head()
    return df

@app.cell
def cell_2():
    # Interactive scatter plot
    fig = px.scatter(df, x='quantity', y='price', 
                     title='Interactive Scatter Plot')
    fig.show()
    return

if __name__ == '__main__':
    app.run()