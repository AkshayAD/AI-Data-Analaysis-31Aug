import marimo as mo
import matplotlib.pyplot as plt

app = mo.App()

@app.cell
def cell_0():
    mo.md("""# Sales Data Analysis""")
    return

@app.cell
def cell_1():
    import pandas as pd
    sales_df = pd.read_csv('/root/repo/data/sample/sales_data.csv')
    sales_df.head()
    return sales_df

@app.cell
def cell_2():
    # Group by product and sum revenue
    product_revenue = sales_df.groupby('product')['revenue'].sum().sort_values(ascending=False)
    product_revenue
    return

@app.cell
def cell_3():
    # Create bar chart
    plt.figure(figsize=(10, 6))
    product_revenue.plot(kind='bar')
    plt.title('Total Revenue by Product')
    plt.xlabel('Product')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return

if __name__ == '__main__':
    app.run()