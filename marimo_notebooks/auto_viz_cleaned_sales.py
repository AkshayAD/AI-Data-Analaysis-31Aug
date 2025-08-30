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
    df = pd.read_csv('/tmp/cleaned_sales.csv')
    df.head()
    return df

@app.cell
def cell_2():
    import seaborn as sns
    plt.figure(figsize=(10, 8))
    correlation = df[['quantity', 'price', 'revenue']].corr()
    sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_3():
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.hist(df['quantity'], bins=30, edgecolor='black')
    plt.title('Histogram: quantity')
    plt.xlabel('quantity')
    plt.ylabel('Frequency')
    plt.subplot(1, 2, 2)
    df.boxplot(column='quantity')
    plt.title('Box Plot: quantity')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_4():
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.hist(df['price'], bins=30, edgecolor='black')
    plt.title('Histogram: price')
    plt.xlabel('price')
    plt.ylabel('Frequency')
    plt.subplot(1, 2, 2)
    df.boxplot(column='price')
    plt.title('Box Plot: price')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_5():
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.hist(df['revenue'], bins=30, edgecolor='black')
    plt.title('Histogram: revenue')
    plt.xlabel('revenue')
    plt.ylabel('Frequency')
    plt.subplot(1, 2, 2)
    df.boxplot(column='revenue')
    plt.title('Box Plot: revenue')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_6():
    plt.figure(figsize=(10, 6))
    df['date'].value_counts().plot(kind='bar')
    plt.title('Count by date')
    plt.xlabel('date')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_7():
    plt.figure(figsize=(10, 6))
    df['product'].value_counts().plot(kind='bar')
    plt.title('Count by product')
    plt.xlabel('product')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_8():
    df['date'] = pd.to_datetime(df['date'])
    plt.figure(figsize=(12, 6))
    for col in ['quantity', 'price', 'revenue']:
        plt.plot(df['date'], df[col], label=col, marker='o')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('Time Series')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return

if __name__ == '__main__':
    app.run()