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
    df = pd.read_csv('/tmp/cleaned_customers.csv')
    df.head()
    return df

@app.cell
def cell_2():
    import seaborn as sns
    plt.figure(figsize=(10, 8))
    correlation = df[['age', 'membership_days', 'total_orders', 'avg_order_value', 'last_order_days_ago', 'customer_lifetime_value']].corr()
    sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_3():
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.hist(df['age'], bins=30, edgecolor='black')
    plt.title('Histogram: age')
    plt.xlabel('age')
    plt.ylabel('Frequency')
    plt.subplot(1, 2, 2)
    df.boxplot(column='age')
    plt.title('Box Plot: age')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_4():
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.hist(df['membership_days'], bins=30, edgecolor='black')
    plt.title('Histogram: membership_days')
    plt.xlabel('membership_days')
    plt.ylabel('Frequency')
    plt.subplot(1, 2, 2)
    df.boxplot(column='membership_days')
    plt.title('Box Plot: membership_days')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_5():
    plt.figure(figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.hist(df['total_orders'], bins=30, edgecolor='black')
    plt.title('Histogram: total_orders')
    plt.xlabel('total_orders')
    plt.ylabel('Frequency')
    plt.subplot(1, 2, 2)
    df.boxplot(column='total_orders')
    plt.title('Box Plot: total_orders')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_6():
    plt.figure(figsize=(10, 6))
    df['customer_id'].value_counts().plot(kind='bar')
    plt.title('Count by customer_id')
    plt.xlabel('customer_id')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return

if __name__ == '__main__':
    app.run()