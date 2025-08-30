import marimo as mo
import pandas as pd
import numpy as np

app = mo.App()

@app.cell
def cell_0():
    mo.md("""# Analysis Notebook: test_fixed""")
    return

@app.cell
def cell_1():
    import pandas as pd
    df = pd.read_csv('data/sample/sales_data.csv')
    df.head()
    return df

@app.cell
def cell_2():
    df.info()
    return

@app.cell
def cell_3():
    df.describe()
    return

@app.cell
def cell_4():
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.hist(df['quantity'], bins=30, edgecolor='black')
    plt.xlabel('quantity')
    plt.ylabel('Frequency')
    plt.title('Histogram: quantity')
    plt.show()
    return plt.figure(figsize

if __name__ == '__main__':
    app.run()