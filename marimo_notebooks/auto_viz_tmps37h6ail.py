import marimo as mo
import matplotlib.pyplot as plt
import seaborn as sns

app = mo.App()

@app.cell
def cell_0():
    mo.md("""# Auto-Generated Visualizations""")
    return

@app.cell
def cell_1():
    import pandas as pd
    df = pd.read_csv('/tmp/tmps37h6ail.csv')
    df.head()
    return df

@app.cell
def cell_2():
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.hist(df['value'], bins=30, edgecolor='black')
    plt.title('Histogram: value')
    plt.xlabel('value')
    plt.ylabel('Frequency')
    plt.subplot(1, 2, 2)
    df.boxplot(column='value')
    plt.title('Box Plot: value')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_3():
    plt.figure(figsize=(10, 6))
    df['category'].value_counts().plot(kind='bar')
    plt.title('Count by category')
    plt.xlabel('category')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return

if __name__ == '__main__':
    app.run()