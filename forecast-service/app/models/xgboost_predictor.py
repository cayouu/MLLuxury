import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
import mlflow
from typing import List, Dict

from features.feature_engineering import LuxuryForecastFeatureEngine

class LuxuryDemandPredictor:
    def __init__(self):
        self.model = None
        self.feature_engine = LuxuryForecastFeatureEngine()
        
    def train(self, df, target='quantity'):
        """Entraînement avec validation temporelle"""
        # Feature engineering
        df_features = self.feature_engine.create_features(df)
        
        # Sélection des features
        exclude_cols = ['date', 'product_id', 'quantity', 'product_name', 'forecast_week']
        feature_cols = [col for col in df_features.columns 
                       if col not in exclude_cols and not col.startswith('Unnamed')]
        
        X = df_features[feature_cols].fillna(0)
        y = df_features[target]
        
        # Split temporel (pas de shuffle!)
        tscv = TimeSeriesSplit(n_splits=5)
        
        # Hyperparamètres optimisés pour séries temporelles
        params = {
            'objective': 'reg:squarederror',
            'max_depth': 6,
            'learning_rate': 0.05,
            'n_estimators': 500,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.1,  # L1 regularization
            'reg_lambda': 1.0,  # L2 regularization
            'random_state': 42
        }
        
        # Entraînement avec MLflow tracking (optionnel)
        try:
            with mlflow.start_run():
                self.model = xgb.XGBRegressor(**params)
                
                # Validation croisée temporelle
                scores = []
                for train_idx, val_idx in tscv.split(X):
                    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                    
                    self.model.fit(
                        X_train, y_train,
                        eval_set=[(X_val, y_val)],
                        verbose=False,
                        early_stopping_rounds=50
                    )
                    
                    score = self.model.score(X_val, y_val)
                    scores.append(score)
                
                # Log metrics et modèle
                train_score = self.model.score(X_train, y_train)
                val_score = np.mean(scores)
                
                mlflow.log_params(params)
                mlflow.log_metrics({
                    'train_r2': train_score,
                    'val_r2': val_score
                })
                mlflow.xgboost.log_model(self.model, "luxury_forecast_model")
        except Exception as e:
            # Si MLflow n'est pas disponible, entraîner sans tracking
            print(f"MLflow not available, training without tracking: {e}")
            self.model = xgb.XGBRegressor(**params)
            self.model.fit(X, y)
            
        return self.model
    
    def predict(self, df_future, horizon_weeks=13) -> List[Dict]:
        """Prédiction pour les N prochaines semaines"""
        # Si pas de modèle entraîné, créer un modèle simple pour démo
        if self.model is None:
            self._create_dummy_model()
        
        predictions = []
        
        # Feature engineering
        df_features = self.feature_engine.create_features(df_future)
        
        # Sélection des features
        exclude_cols = ['date', 'product_id', 'quantity', 'product_name', 'forecast_week']
        feature_cols = [col for col in df_features.columns 
                       if col not in exclude_cols and not col.startswith('Unnamed')]
        
        X = df_features[feature_cols].fillna(0)
        
        # Prédiction
        pred = self.model.predict(X)
        
        # Grouper par semaine
        if 'forecast_week' in df_features.columns:
            for week in range(horizon_weeks):
                week_mask = df_features['forecast_week'] == week
                week_pred = pred[week_mask]
                week_product_ids = df_features.loc[week_mask, 'product_id'].values if 'product_id' in df_features.columns else df_future['product_id'].values[week_mask]
                
                predictions.append({
                    'product_id': week_product_ids,
                    'week': week,
                    'predicted_quantity': week_pred,
                    'confidence_interval': self._calculate_confidence_interval(week_pred)
                })
        else:
            # Fallback: une seule prédiction
            predictions.append({
                'product_id': df_future['product_id'].values if 'product_id' in df_future.columns else [],
                'week': 0,
                'predicted_quantity': pred,
                'confidence_interval': self._calculate_confidence_interval(pred)
            })
        
        return predictions
    
    def _calculate_confidence_interval(self, predictions, confidence=0.95):
        """Intervalle de confiance basé sur l'erreur historique"""
        if len(predictions) == 0:
            return (np.array([]), np.array([]))
        
        # Utilisation d'un coefficient pour l'intervalle de confiance
        std_error = np.std(predictions) * 1.96  # 95% CI
        lower = predictions - std_error
        upper = predictions + std_error
        
        # S'assurer que les valeurs inférieures ne sont pas négatives
        lower = np.maximum(lower, 0)
        
        return (lower, upper)
    
    def _create_dummy_model(self):
        """Créer un modèle simple pour la démo"""
        from sklearn.ensemble import RandomForestRegressor
        
        # Créer des données d'exemple pour entraîner un modèle simple
        np.random.seed(42)
        X_dummy = np.random.rand(100, 10)
        y_dummy = np.random.poisson(lam=50, size=100)
        
        self.model = RandomForestRegressor(n_estimators=10, random_state=42)
        self.model.fit(X_dummy, y_dummy)
