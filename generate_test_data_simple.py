#!/usr/bin/env python3
"""
Simple Test Data Generator for AI Data Analysis Platform
Creates test CSV files without external dependencies
"""

import csv
import random
import json
from datetime import datetime, timedelta
from pathlib import Path

def create_test_data_directory():
    """Create directory structure for test data"""
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    subdirs = ["valid", "edge_cases", "large", "corrupted"]
    for subdir in subdirs:
        (test_dir / subdir).mkdir(exist_ok=True)
    
    print(f"✅ Created test data directory structure at {test_dir}")
    return test_dir

def generate_sales_csv(rows=1000, file_path=None):
    """Generate sales data CSV without pandas"""
    if file_path is None:
        return
    
    random.seed(42)
    
    products = ['Electronics', 'Clothing', 'Food', 'Books', 'Sports', 'Home']
    regions = ['North', 'South', 'East', 'West', 'Central']
    payment_methods = ['Credit Card', 'Cash', 'Online', 'Debit Card']
    customer_segments = ['Premium', 'Regular', 'New', 'Returning']
    
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        headers = [
            'transaction_id', 'date', 'product_category', 'product_name',
            'quantity', 'unit_price', 'discount_percent', 'region',
            'customer_id', 'customer_segment', 'payment_method',
            'satisfaction_score', 'delivery_days', 'returned', 'revenue', 'profit'
        ]
        writer.writerow(headers)
        
        # Generate data rows
        start_date = datetime(2024, 1, 1)
        for i in range(rows):
            date = (start_date + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S')
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(10, 500), 2)
            discount = random.choice([0, 5, 10, 15, 20])
            revenue = round(quantity * unit_price * (1 - discount/100), 2)
            profit = round(revenue * random.uniform(0.1, 0.4), 2)
            
            # Add some missing values (5% chance)
            satisfaction = round(random.uniform(1, 5), 2) if random.random() > 0.05 else ''
            delivery = random.randint(1, 7) if random.random() > 0.05 else ''
            
            row = [
                f'TXN{i+1:06d}',
                date,
                random.choice(products),
                f'Product_{i%100:03d}',
                quantity,
                unit_price,
                discount,
                random.choice(regions),
                f'CUST{random.randint(1, 500):04d}',
                random.choice(customer_segments),
                random.choice(payment_methods),
                satisfaction,
                delivery,
                'true' if random.random() < 0.05 else 'false',
                revenue,
                profit
            ]
            writer.writerow(row)
    
    print(f"✅ Generated sales data: {file_path} ({rows} rows)")

def generate_customer_csv(rows=500, file_path=None):
    """Generate customer data CSV"""
    if file_path is None:
        return
    
    random.seed(42)
    
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        headers = [
            'customer_id', 'age', 'gender', 'city', 'state',
            'signup_date', 'lifetime_value', 'total_orders',
            'preferred_category', 'email_subscribed', 'loyalty_tier'
        ]
        writer.writerow(headers)
        
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
        states = ['NY', 'CA', 'IL', 'TX', 'AZ']
        categories = ['Electronics', 'Clothing', 'Food', 'Books']
        tiers = ['Bronze', 'Silver', 'Gold', 'Platinum']
        
        start_date = datetime(2020, 1, 1)
        for i in range(rows):
            signup_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            
            row = [
                f'CUST{i+1:04d}',
                random.randint(18, 80),
                random.choice(['M', 'F', 'Other']),
                random.choice(cities),
                random.choice(states),
                signup_date,
                round(random.uniform(100, 10000), 2),
                random.randint(1, 100),
                random.choice(categories),
                'true' if random.random() < 0.7 else 'false',
                random.choices(tiers, weights=[40, 30, 20, 10])[0]
            ]
            writer.writerow(row)
    
    print(f"✅ Generated customer data: {file_path} ({rows} rows)")

def generate_product_csv(rows=200, file_path=None):
    """Generate product data CSV"""
    if file_path is None:
        return
    
    random.seed(42)
    
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        headers = [
            'product_id', 'product_name', 'category', 'subcategory',
            'brand', 'cost', 'price', 'stock_quantity', 'supplier',
            'launch_date', 'rating', 'review_count', 'margin'
        ]
        writer.writerow(headers)
        
        categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Sports', 'Home']
        
        start_date = datetime(2023, 1, 1)
        for i in range(rows):
            cost = round(random.uniform(5, 300), 2)
            price = round(random.uniform(10, 500), 2)
            margin = round((price - cost) / price * 100, 2) if price > 0 else 0
            launch_date = (start_date + timedelta(weeks=i)).strftime('%Y-%m-%d')
            
            row = [
                f'PROD{i+1:04d}',
                f'Product {i+1}',
                random.choice(categories),
                f'Sub_{i%20}',
                f'Brand_{chr(65 + i%26)}',
                cost,
                price,
                random.randint(0, 1000),
                f'Supplier_{i%10}',
                launch_date,
                round(random.uniform(3.0, 5.0), 1),
                random.randint(0, 5000),
                margin
            ]
            writer.writerow(row)
    
    print(f"✅ Generated product data: {file_path} ({rows} rows)")

def create_edge_case_files(test_dir):
    """Create edge case test files"""
    edge_dir = test_dir / "edge_cases"
    
    # 1. Empty CSV
    with open(edge_dir / "empty.csv", 'w') as f:
        f.write("")
    print(f"✅ Created empty.csv")
    
    # 2. Single row CSV
    with open(edge_dir / "single_row.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['col1', 'col2'])
        writer.writerow([1, 'test'])
    print(f"✅ Created single_row.csv")
    
    # 3. Single column CSV
    with open(edge_dir / "single_column.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['only_column'])
        for i in range(10):
            writer.writerow([i])
    print(f"✅ Created single_column.csv")
    
    # 4. All missing values
    with open(edge_dir / "all_missing.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['col1', 'col2', 'col3'])
        for _ in range(10):
            writer.writerow(['', '', ''])
    print(f"✅ Created all_missing.csv")
    
    # 5. Special characters in column names
    with open(edge_dir / "special_chars.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Column 1!', 'Column@2', 'Column#3', 'Column$4%'])
        for i in range(5):
            writer.writerow([i, i+1, i+2, i+3])
    print(f"✅ Created special_chars.csv")
    
    # 6. Mixed data types
    with open(edge_dir / "mixed_types.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['mixed_column'])
        values = [1, 'two', 3.0, 'True', '', datetime.now(), 'seven', 8, 9.5, 'False']
        for val in values:
            writer.writerow([val])
    print(f"✅ Created mixed_types.csv")
    
    # 7. Very wide dataset (many columns)
    with open(edge_dir / "wide_dataset.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        headers = [f'col_{i}' for i in range(100)]
        writer.writerow(headers)
        for _ in range(10):
            row = [random.random() for _ in range(100)]
            writer.writerow(row)
    print(f"✅ Created wide_dataset.csv (100 columns)")
    
    # 8. Duplicate column names
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
    generate_sales_csv(1000, file_path=valid_dir / "sales_data.csv")
    generate_customer_csv(500, file_path=valid_dir / "customer_data.csv")
    generate_product_csv(200, file_path=valid_dir / "product_data.csv")
    
    # Generate small datasets for quick testing
    generate_sales_csv(100, file_path=valid_dir / "sales_small.csv")
    generate_customer_csv(50, file_path=valid_dir / "customer_small.csv")
    
    # Generate edge cases
    print("\n⚠️ Generating Edge Case Files...")
    print("-"*40)
    create_edge_case_files(test_dir)
    
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
    print("│   └── test_data.json")
    print("└── corrupted/       # Corrupted files")
    print("    ├── malformed.csv")
    print("    ├── binary.csv")
    print("    └── invalid_encoding.csv")
    
    print("\n🎯 Ready for comprehensive testing!")
    
    return test_dir

if __name__ == "__main__":
    main()