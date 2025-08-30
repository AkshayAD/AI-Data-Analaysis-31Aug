#!/usr/bin/env python3
"""
Test that the trained ML model can make predictions
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))

from agents import MLAgent

def test_predictions():
    """Test model training and predictions"""
    print("Testing ML Model Predictions...")
    
    # Initialize ML agent
    ml_agent = MLAgent()
    
    # Train model
    print("\n1. Training model on customer data...")
    train_result = ml_agent.execute({
        "ml_task": "train",
        "data_path": "data/sample/customer_purchases.csv",
        "target_column": "customer_lifetime_value",
        "model_type": "auto"
    })
    
    if "error" in train_result:
        print(f"❌ Training failed: {train_result['error']}")
        return False
    
    print(f"✅ Model trained successfully")
    print(f"   - Model ID: {train_result['model_id']}")
    print(f"   - R² Score: {train_result['metrics']['r2']:.3f}")
    
    # Create test data for predictions
    print("\n2. Creating test data for predictions...")
    test_data = pd.DataFrame({
        'customer_id': ['TEST001', 'TEST002', 'TEST003'],
        'age': [30, 45, 25],
        'membership_days': [400, 800, 200],
        'total_orders': [15, 35, 5],
        'avg_order_value': [55.00, 85.00, 35.00],
        'last_order_days_ago': [10, 5, 20]
    })
    
    # Save test data
    test_path = '/tmp/test_customers.csv'
    test_data.to_csv(test_path, index=False)
    print(f"✅ Test data created with {len(test_data)} samples")
    
    # Make predictions
    print("\n3. Making predictions...")
    predict_result = ml_agent.execute({
        "ml_task": "predict",
        "model_id": train_result['model_id'],
        "data_path": test_path,
        "output_path": "/tmp/predictions.csv"
    })
    
    if "error" in predict_result:
        print(f"❌ Prediction failed: {predict_result['error']}")
        return False
    
    print(f"✅ Predictions completed")
    print(f"   - Number of predictions: {predict_result['predictions_count']}")
    print(f"   - Output saved to: {predict_result['output_path']}")
    
    # Load and display predictions
    predictions_df = pd.read_csv(predict_result['output_path'])
    print("\n4. Prediction Results:")
    print("-" * 50)
    for _, row in predictions_df.iterrows():
        print(f"Customer {row['customer_id']}:")
        print(f"  Age: {row['age']}, Orders: {row['total_orders']}")
        print(f"  Predicted CLV: ${row['prediction']:.2f}")
    
    # Evaluate model on original data
    print("\n5. Evaluating model performance...")
    eval_result = ml_agent.execute({
        "ml_task": "evaluate",
        "model_id": train_result['model_id'],
        "data_path": "data/sample/customer_purchases.csv"
    })
    
    if "error" in eval_result:
        print(f"❌ Evaluation failed: {eval_result['error']}")
        return False
    
    print(f"✅ Model evaluation complete")
    metrics = eval_result.get('metrics', {})
    print(f"   - Mean Absolute Error: ${metrics.get('mae', 0):.2f}")
    print(f"   - R² Score: {metrics.get('r2', 0):.3f}")
    
    return True

if __name__ == "__main__":
    success = test_predictions()
    
    if success:
        print("\n" + "="*50)
        print("✅ ML PREDICTIONS TEST PASSED")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ ML PREDICTIONS TEST FAILED")
        print("="*50)
        sys.exit(1)