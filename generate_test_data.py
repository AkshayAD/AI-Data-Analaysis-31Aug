#!/usr/bin/env python3
"""
Test Data Generator for AI Data Analysis Platform
Creates various test datasets for comprehensive testing
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path
import random

def create_test_data_directory():
    """Create directory structure for test data"""
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    subdirs = ["valid", "edge_cases", "large", "corrupted"]
    for subdir in subdirs:
        (test_dir / subdir).mkdir(exist_ok=True)
    
    print(f"✅ Created test data directory structure at {test_dir}")
    return test_dir

def generate_sales_data(rows=1000, start_date="2024-01-01", file_path=None):
    """Generate realistic sales data"""
    np.random.seed(42)
    
    # Date range
    start = pd.to_datetime(start_date)
    dates = pd.date_range(start, periods=rows, freq='H')
    
    # Product categories and regions
    products = ['Electronics', 'Clothing', 'Food', 'Books', 'Sports', 'Home']
    regions = ['North', 'South', 'East', 'West', 'Central']
    payment_methods = ['Credit Card', 'Cash', 'Online', 'Debit Card']
    customer_segments = ['Premium', 'Regular', 'New', 'Returning']
    
    # Generate data
    data = {
        'transaction_id': [f'TXN{i:06d}' for i in range(1, rows + 1)],
        'date': dates,
        'product_category': np.random.choice(products, rows),
        'product_name': [f'Product_{i%100:03d}' for i in range(rows)],
        'quantity': np.random.randint(1, 10, rows),
        'unit_price': np.round(np.random.uniform(10, 500, rows), 2),
        'discount_percent': np.random.choice([0, 5, 10, 15, 20], rows, p=[0.4, 0.2, 0.2, 0.1, 0.1]),
        'region': np.random.choice(regions, rows),
        'customer_id': [f'CUST{np.random.randint(1, 500):04d}' for _ in range(rows)],
        'customer_segment': np.random.choice(customer_segments, rows),
        'payment_method': np.random.choice(payment_methods, rows),
        'satisfaction_score': np.random.uniform(1, 5, rows),
        'delivery_days': np.random.randint(1, 7, rows),
        'returned': np.random.choice([True, False], rows, p=[0.05, 0.95])
    }
    
    df = pd.DataFrame(data)
    
    # Calculate revenue and profit
    df['revenue'] = df['quantity'] * df['unit_price'] * (1 - df['discount_percent']/100)
    df['profit'] = df['revenue'] * np.random.uniform(0.1, 0.4, rows)
    
    # Add some missing values randomly (5% of data)
    for col in ['satisfaction_score', 'delivery_days']:
        missing_idx = np.random.choice(df.index, size=int(0.05 * len(df)), replace=False)
        df.loc[missing_idx, col] = np.nan
    
    # Save to file
    if file_path:
        df.to_csv(file_path, index=False)
        print(f"✅ Generated sales data: {file_path} ({rows} rows)")
    
    return df

def generate_customer_data(rows=500, file_path=None):
    """Generate customer demographic data"""
    np.random.seed(42)
    
    data = {
        'customer_id': [f'CUST{i:04d}' for i in range(1, rows + 1)],
        'age': np.random.randint(18, 80, rows),
        'gender': np.random.choice(['M', 'F', 'Other'], rows, p=[0.45, 0.45, 0.1]),
        'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], rows),
        'state': np.random.choice(['NY', 'CA', 'IL', 'TX', 'AZ'], rows),
        'signup_date': pd.date_range(end=datetime.now(), periods=rows, freq='D'),
        'lifetime_value': np.round(np.random.lognormal(7, 2, rows), 2),
        'total_orders': np.random.randint(1, 100, rows),
        'preferred_category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], rows),
        'email_subscribed': np.random.choice([True, False], rows),
        'loyalty_tier': np.random.choice(['Bronze', 'Silver', 'Gold', 'Platinum'], rows, p=[0.4, 0.3, 0.2, 0.1])
    }
    
    df = pd.DataFrame(data)
    
    if file_path:
        df.to_csv(file_path, index=False)
        print(f"✅ Generated customer data: {file_path} ({rows} rows)")
    
    return df

def generate_product_data(rows=200, file_path=None):
    """Generate product catalog data"""
    np.random.seed(42)
    
    categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Sports', 'Home']
    
    data = {
        'product_id': [f'PROD{i:04d}' for i in range(1, rows + 1)],
        'product_name': [f'Product {i}' for i in range(1, rows + 1)],
        'category': np.random.choice(categories, rows),
        'subcategory': [f'Sub_{i%20}' for i in range(rows)],
        'brand': [f'Brand_{chr(65 + i%26)}' for i in range(rows)],
        'cost': np.round(np.random.uniform(5, 300, rows), 2),
        'price': np.round(np.random.uniform(10, 500, rows), 2),
        'stock_quantity': np.random.randint(0, 1000, rows),
        'supplier': [f'Supplier_{i%10}' for i in range(rows)],
        'launch_date': pd.date_range(end=datetime.now(), periods=rows, freq='W'),
        'rating': np.round(np.random.uniform(3.0, 5.0, rows), 1),
        'review_count': np.random.randint(0, 5000, rows)
    }
    
    df = pd.DataFrame(data)
    
    # Calculate margin
    df['margin'] = ((df['price'] - df['cost']) / df['price'] * 100).round(2)
    
    if file_path:
        df.to_csv(file_path, index=False)
        print(f"✅ Generated product data: {file_path} ({rows} rows)")
    
    return df

def create_edge_case_files(test_dir):
    """Create edge case test files"""
    edge_dir = test_dir / "edge_cases"
    
    # 1. Empty CSV
    pd.DataFrame().to_csv(edge_dir / "empty.csv", index=False)
    print(f"✅ Created empty.csv")
    
    # 2. Single row CSV
    single_row = pd.DataFrame({'col1': [1], 'col2': ['test']})
    single_row.to_csv(edge_dir / "single_row.csv", index=False)
    print(f"✅ Created single_row.csv")
    
    # 3. Single column CSV
    single_col = pd.DataFrame({'only_column': range(10)})
    single_col.to_csv(edge_dir / "single_column.csv", index=False)
    print(f"✅ Created single_column.csv")
    
    # 4. All missing values
    missing_df = pd.DataFrame({
        'col1': [np.nan] * 10,
        'col2': [None] * 10,
        'col3': [np.nan] * 10
    })
    missing_df.to_csv(edge_dir / "all_missing.csv", index=False)
    print(f"✅ Created all_missing.csv")
    
    # 5. Special characters in column names
    special_chars = pd.DataFrame({
        'Column 1!': range(5),
        'Column@2': range(5),
        'Column#3': range(5),
        'Column$4%': range(5)
    })
    special_chars.to_csv(edge_dir / "special_chars.csv", index=False)
    print(f"✅ Created special_chars.csv")
    
    # 6. Mixed data types
    mixed_types = pd.DataFrame({
        'mixed_column': [1, 'two', 3.0, True, None, datetime.now(), 'seven', 8, 9.5, False]
    })
    mixed_types.to_csv(edge_dir / "mixed_types.csv", index=False)
    print(f"✅ Created mixed_types.csv")
    
    # 7. Very wide dataset (many columns)
    wide_data = pd.DataFrame(
        np.random.randn(10, 100),
        columns=[f'col_{i}' for i in range(100)]
    )
    wide_data.to_csv(edge_dir / "wide_dataset.csv", index=False)
    print(f"✅ Created wide_dataset.csv (100 columns)")
    
    # 8. Duplicate column names
    dup_cols = pd.DataFrame({
        'name': ['A', 'B'],
        'value': [1, 2]
    })
    # Manually create CSV with duplicate column names
    with open(edge_dir / "duplicate_columns.csv", 'w') as f:
        f.write("name,name,value,value\n")
        f.write("A,B,1,2\n")
        f.write("C,D,3,4\n")
    print(f"✅ Created duplicate_columns.csv")
    
    # 9. JSON file
    json_data = {
        'data': [
            {'id': 1, 'value': 'test1'},
            {'id': 2, 'value': 'test2'}
        ]
    }
    with open(edge_dir / "test_data.json", 'w') as f:
        json.dump(json_data, f)
    print(f"✅ Created test_data.json")
    
    # 10. Excel file with multiple sheets
    with pd.ExcelWriter(edge_dir / "multi_sheet.xlsx") as writer:
        pd.DataFrame({'A': [1, 2, 3]}).to_excel(writer, sheet_name='Sheet1', index=False)
        pd.DataFrame({'B': [4, 5, 6]}).to_excel(writer, sheet_name='Sheet2', index=False)
    print(f"✅ Created multi_sheet.xlsx")

def create_large_dataset(test_dir, rows=100000):
    """Create a large dataset for performance testing"""
    large_dir = test_dir / "large"
    
    print(f"⏳ Generating large dataset ({rows} rows)...")
    large_df = generate_sales_data(rows=rows)
    file_path = large_dir / f"large_sales_{rows}.csv"
    large_df.to_csv(file_path, index=False)
    
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"✅ Created large dataset: {file_path} ({file_size_mb:.2f} MB)")
    
    return file_path

def create_corrupted_files(test_dir):
    """Create corrupted files for error testing"""
    corrupt_dir = test_dir / "corrupted"
    
    # 1. Malformed CSV
    with open(corrupt_dir / "malformed.csv", 'w') as f:
        f.write("col1,col2,col3\n")
        f.write("1,2\n")  # Missing column
        f.write("3,4,5,6\n")  # Extra column
        f.write("7,8,9\n")
    print(f"✅ Created malformed.csv")
    
    # 2. Binary file with .csv extension
    with open(corrupt_dir / "binary.csv", 'wb') as f:
        f.write(b'\x00\x01\x02\x03\x04\x05')
    print(f"✅ Created binary.csv")
    
    # 3. File with invalid encoding
    with open(corrupt_dir / "invalid_encoding.csv", 'wb') as f:
        f.write("col1,col2\n".encode('utf-8'))
        f.write(b'\xff\xfe Invalid UTF-8 bytes \xc3\x28\n')
    print(f"✅ Created invalid_encoding.csv")

def main():
    """Generate all test data"""
    print("\n" + "="*60)
    print("🎯 TEST DATA GENERATION FOR AI DATA ANALYSIS PLATFORM")
    print("="*60)
    
    # Create directory structure
    test_dir = create_test_data_directory()
    
    # Generate valid datasets
    print("\n📊 Generating Valid Datasets...")
    print("-"*40)
    
    valid_dir = test_dir / "valid"
    generate_sales_data(1000, file_path=valid_dir / "sales_data.csv")
    generate_customer_data(500, file_path=valid_dir / "customer_data.csv")
    generate_product_data(200, file_path=valid_dir / "product_data.csv")
    
    # Generate small datasets for quick testing
    generate_sales_data(100, file_path=valid_dir / "sales_small.csv")
    generate_customer_data(50, file_path=valid_dir / "customer_small.csv")
    
    # Generate edge cases
    print("\n⚠️ Generating Edge Case Files...")
    print("-"*40)
    create_edge_case_files(test_dir)
    
    # Generate large dataset
    print("\n📦 Generating Large Dataset...")
    print("-"*40)
    create_large_dataset(test_dir, rows=50000)  # 50k rows for testing
    
    # Generate corrupted files
    print("\n❌ Generating Corrupted Files...")
    print("-"*40)
    create_corrupted_files(test_dir)
    
    # Create summary
    print("\n" + "="*60)
    print("✅ TEST DATA GENERATION COMPLETE")
    print("="*60)
    
    print("\n📁 Directory Structure:")
    print("test_data/")
    print("├── valid/           # Valid test datasets")
    print("│   ├── sales_data.csv (1000 rows)")
    print("│   ├── customer_data.csv (500 rows)")
    print("│   ├── product_data.csv (200 rows)")
    print("│   ├── sales_small.csv (100 rows)")
    print("│   └── customer_small.csv (50 rows)")
    print("├── edge_cases/      # Edge case files")
    print("│   ├── empty.csv")
    print("│   ├── single_row.csv")
    print("│   ├── single_column.csv")
    print("│   ├── all_missing.csv")
    print("│   ├── special_chars.csv")
    print("│   ├── mixed_types.csv")
    print("│   ├── wide_dataset.csv")
    print("│   ├── duplicate_columns.csv")
    print("│   ├── test_data.json")
    print("│   └── multi_sheet.xlsx")
    print("├── large/           # Large datasets")
    print("│   └── large_sales_50000.csv")
    print("└── corrupted/       # Corrupted files")
    print("    ├── malformed.csv")
    print("    ├── binary.csv")
    print("    └── invalid_encoding.csv")
    
    print("\n🎯 Ready for comprehensive testing!")
    
    return test_dir

if __name__ == "__main__":
    main()