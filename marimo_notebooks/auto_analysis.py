import marimo as mo

app = mo.App()

@app.cell
def cell_0():
    mo.md("""# Automated Analysis Report""")
    return

@app.cell
def cell_1():
    import pandas as pd
    df = pd.read_csv('/root/repo/data/sample/sales_data.csv')
    df.head()
    return df

@app.cell
def cell_2():
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.hist(df['quantity'], bins=30, edgecolor='black')
    plt.xlabel('quantity')
    plt.ylabel('Frequency')
    plt.title('Histogram: quantity')
    plt.show()
    return

@app.cell
def cell_3():
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.hist(df['price'], bins=30, edgecolor='black')
    plt.xlabel('price')
    plt.ylabel('Frequency')
    plt.title('Histogram: price')
    plt.show()
    return

@app.cell
def cell_4():
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.hist(df['revenue'], bins=30, edgecolor='black')
    plt.xlabel('revenue')
    plt.ylabel('Frequency')
    plt.title('Histogram: revenue')
    plt.show()
    return

if __name__ == '__main__':
    app.run()