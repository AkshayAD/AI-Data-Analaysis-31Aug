import marimo as mo

app = mo.App()

@app.cell
def __():
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score
    import matplotlib.pyplot as plt
    return pd, np, train_test_split, RandomForestRegressor, mean_squared_error, r2_score, plt

@app.cell
def __(pd):
    # Load data
    df = pd.read_csv('data/sample/customer_purchases.csv')
    mo.md(f"## ML Pipeline: Predicting {'customer_lifetime_value'}")
    return df,

@app.cell
def __(df):
    # Show data info
    print(f"Dataset: {len(df)} rows, {len(df.columns)} columns")
    df.head()
    return

@app.cell
def __(df, np):
    # Prepare features and target
    target = 'customer_lifetime_value'
    
    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target in numeric_cols:
        numeric_cols.remove(target)
    
    X = df[numeric_cols].fillna(0)
    y = df[target]
    
    print(f"Features: {numeric_cols}")
    print(f"Target: {target}")
    return X, y, target, numeric_cols

@app.cell
def __(X, y, train_test_split):
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    return X_train, X_test, y_train, y_test

@app.cell
def __(X_train, y_train, RandomForestRegressor):
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
    model.fit(X_train, y_train)
    print("Model trained!")
    return model,

@app.cell
def __(X_test, y_test, model, mean_squared_error, r2_score):
    # Evaluate model
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    mo.md(f"""
    ## Model Performance
    - **MSE**: {mse:.2f}
    - **R² Score**: {r2:.3f}
    """)
    return y_pred, mse, r2

@app.cell
def __(y_test, y_pred, plt, target):
    # Prediction vs Actual plot
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel(f'Actual {target}')
    plt.ylabel(f'Predicted {target}')
    plt.title('Predictions vs Actual')
    plt.tight_layout()
    plt.show()
    return

@app.cell
def __(model, X, numeric_cols, plt):
    # Feature importance
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        feature_importance = dict(zip(numeric_cols, importance))
        
        # Sort by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        # Plot
        plt.figure(figsize=(10, 6))
        features, importances = zip(*sorted_features[:10])
        plt.barh(features, importances)
        plt.xlabel('Importance')
        plt.title('Top Feature Importances')
        plt.tight_layout()
        plt.show()
    return

if __name__ == "__main__":
    app.run()
