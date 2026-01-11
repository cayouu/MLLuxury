"""
Hyperparameter tuning pour le modèle XGBoost
"""
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
import pandas as pd
import numpy as np

def tune_hyperparameters(X, y):
    """Recherche de grille pour optimiser les hyperparamètres"""
    
    # Paramètres à tester
    param_grid = {
        'max_depth': [4, 6, 8],
        'learning_rate': [0.01, 0.05, 0.1],
        'n_estimators': [300, 500, 700],
        'subsample': [0.8, 0.9],
        'colsample_bytree': [0.8, 0.9],
        'min_child_weight': [1, 3, 5]
    }
    
    # Utiliser TimeSeriesSplit pour la validation
    tscv = TimeSeriesSplit(n_splits=3)
    
    # Modèle de base
    base_model = xgb.XGBRegressor(
        objective='reg:squarederror',
        random_state=42
    )
    
    # Grid search
    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_mean_absolute_percentage_error',
        n_jobs=-1,
        verbose=2
    )
    
    grid_search.fit(X, y)
    
    print("Best parameters:", grid_search.best_params_)
    print("Best score:", grid_search.best_score_)
    
    return grid_search.best_estimator_, grid_search.best_params_

if __name__ == "__main__":
    # Exemple d'utilisation
    print("Hyperparameter tuning example")
    print("Note: This requires training data. Use train_pipeline.py first.")
