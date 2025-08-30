import marimo as mo
import matplotlib.pyplot as plt
import seaborn as sns

app = mo.App()

@app.cell
def cell_0():
    mo.md("""# Data Analysis Report""")
    return

@app.cell
def cell_1():
    mo.md("""## Dataset: cleaned_sales.csv""")
    return

@app.cell
def cell_2():
    import pandas as pd
    df = pd.read_csv('/tmp/cleaned_sales.csv')
    df.head()
    return df

@app.cell
def cell_3():
    mo.md("""## Summary Statistics""")
    return

@app.cell
def cell_4():
    df.describe()
    return

@app.cell
def cell_5():
    mo.md("""## Data Visualizations""")
    return

@app.cell
def cell_6():
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    df['quantity'].hist(bins=30, edgecolor='black')
    plt.title('Distribution of quantity')
    plt.subplot(1, 3, 2)
    df.boxplot(column='quantity')
    plt.title('Box Plot')
    plt.subplot(1, 3, 3)
    df['quantity'].plot(kind='density')
    plt.title('Density Plot')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_7():
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    df['price'].hist(bins=30, edgecolor='black')
    plt.title('Distribution of price')
    plt.subplot(1, 3, 2)
    df.boxplot(column='price')
    plt.title('Box Plot')
    plt.subplot(1, 3, 3)
    df['price'].plot(kind='density')
    plt.title('Density Plot')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_8():
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    df['revenue'].hist(bins=30, edgecolor='black')
    plt.title('Distribution of revenue')
    plt.subplot(1, 3, 2)
    df.boxplot(column='revenue')
    plt.title('Box Plot')
    plt.subplot(1, 3, 3)
    df['revenue'].plot(kind='density')
    plt.title('Density Plot')
    plt.tight_layout()
    plt.show()
    return

if __name__ == '__main__':
    app.run()