import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
import joblib
import os

def train_and_evaluate_models():
    # Load data
    data_path = os.path.join(os.path.dirname(__file__), 'ev_data_synthetic.csv')
    if not os.path.exists(data_path):
        print(f"Error: Could not find dataset at {data_path}")
        return
        
    df = pd.read_csv(data_path)
    
    # Define features and targets
    # Including Brand now
    features = ['Brand', 'Battery_Capacity_kWh', 'Motor_Power_kW', 'Weight_kg', 'Max_Charge_Power_kW', 'Drag_Coefficient']
    
    X = df[features]
    y_range = df['Range_km']
    y_chargetime = df['Charge_Time_mins']
    
    # Train-test split
    X_train, X_test, yr_train, yr_test, yc_train, yc_test = train_test_split(
        X, y_range, y_chargetime, test_size=0.2, random_state=42
    )
    
    # Preprocessing for categorical data
    categorical_features = ['Brand']
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough' # keep numeric features as is
    )

    # Range Model Pipeline
    print("--- Training Range Prediction Model ---")
    rf_range = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    rf_range.fit(X_train, yr_train)
    
    yr_pred = rf_range.predict(X_test)
    print(f"Range MAE: {mean_absolute_error(yr_test, yr_pred):.2f} km")
    print(f"Range R2 Score: {r2_score(yr_test, yr_pred):.3f}")
    
    # Extract feature names after one-hot encoding
    ohe = rf_range.named_steps['preprocessor'].transformers_[0][1]
    cat_feature_names = ohe.get_feature_names_out(categorical_features)
    numeric_features = [f for f in features if f not in categorical_features]
    all_feature_names = list(cat_feature_names) + numeric_features

    # Feature Importance for Range
    rf_range_model = rf_range.named_steps['regressor']
    importance_range = pd.Series(rf_range_model.feature_importances_, index=all_feature_names).sort_values(ascending=False)
    print("\nFeature Importances for Range (Top 10):")
    print(importance_range.head(10))
    
    # Charge Time Model Pipeline
    print("\n--- Training Charge Time Prediction Model ---")
    rf_charge = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    rf_charge.fit(X_train, yc_train)
    
    yc_pred = rf_charge.predict(X_test)
    print(f"Charge Time MAE: {mean_absolute_error(yc_test, yc_pred):.2f} mins")
    print(f"Charge Time R2 Score: {r2_score(yc_test, yc_pred):.3f}")
    
    # Feature Importance for Charge Time
    rf_charge_model = rf_charge.named_steps['regressor']
    importance_charge = pd.Series(rf_charge_model.feature_importances_, index=all_feature_names).sort_values(ascending=False)
    print("\nFeature Importances for Charge Time (Top 10):")
    print(importance_charge.head(10))
    
    # Save the models and feature importances
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(rf_range, os.path.join(models_dir, 'rf_range_model.pkl'))
    joblib.dump(rf_charge, os.path.join(models_dir, 'rf_charge_model.pkl'))
    
    # We can save importance_range to dict but limit it to top 15 or so for the UI
    importances = {
        'Range': importance_range.head(15).to_dict(),
        'ChargeTime': importance_charge.head(15).to_dict()
    }
    joblib.dump(importances, os.path.join(models_dir, 'feature_importances.pkl'))
    
    print(f"\nModels saved successfully in {models_dir}")

if __name__ == "__main__":
    train_and_evaluate_models()
