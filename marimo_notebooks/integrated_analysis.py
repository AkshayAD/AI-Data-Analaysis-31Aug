import marimo as mo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

app = mo.App()

@app.cell
def cell_0():
    mo.md("""# Customer Lifetime Value Analysis""")
    return

@app.cell
def cell_1():
    mo.md("""## Complete Pipeline Results""")
    return

@app.cell
def cell_2():
    import pandas as pd
    df = pd.read_csv('/tmp/cleaned_customers.csv')
    print(f"Loaded {len(df)} customer records")
    df.head()
    return df

@app.cell
def cell_3():
    # Summary statistics
    summary = df.describe()
    print("Key metrics:")
    print(f"Average CLV: ${df['customer_lifetime_value'].mean():.2f}")
    print(f"Average orders: {df['total_orders'].mean():.1f}")
    print(f"Average age: {df['age'].mean():.1f} years")
    summary
    return summary

@app.cell
def cell_4():
    # Correlation analysis
    plt.figure(figsize=(10, 8))
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlation = df[numeric_cols].corr()
    sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0, fmt='.2f')
    plt.title('Feature Correlation Matrix')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def cell_5():
    # Customer Lifetime Value Distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    # Histogram
    axes[0].hist(df['customer_lifetime_value'], bins=20, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('Customer Lifetime Value ($)')
    axes[0].set_ylabel('Number of Customers')
    axes[0].set_title('CLV Distribution')
    axes[0].grid(True, alpha=0.3)
    # Box plot by age group
    df['age_group'] = pd.cut(df['age'], bins=[0, 30, 40, 50, 100], labels=['<30', '30-40', '40-50', '50+'])
    df.boxplot(column='customer_lifetime_value', by='age_group', ax=axes[1])
    axes[1].set_xlabel('Age Group')
    axes[1].set_ylabel('Customer Lifetime Value ($)')
    axes[1].set_title('CLV by Age Group')
    plt.suptitle('')
    plt.tight_layout()
    plt.show()
    return

if __name__ == '__main__':
    app.run()