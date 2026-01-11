"""
Pipeline d'entraînement avec tracking MLflow complet
"""
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from datetime import datetime
import mlflow
import mlflow.xgboost
from mlflow.tracking import MlflowClient
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
import xgboost as xgb

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from app.models.xgboost_predictor import LuxuryDemandPredictor
from app.features.feature_engineering import LuxuryForecastFeatureEngine

# Configuration MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT_NAME = "luxury_demand_forecast"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

def load_training_data(data_path: str = None) -> pd.DataFrame:
    """Charger les données d'entraînement"""
    # Dans un vrai projet, ceci chargerait depuis une base de données
    # Pour l'exemple, on génère des données synthétiques
    np.random.seed(42)
    
    dates = pd.date_range('2022-01-01', '2024-12-31', freq='W')
    products = ['BAG-001', 'BAG-002', 'BAG-003']
    countries = ['FR', 'US', 'CN', 'JP', 'UK']
    channels = ['Boutique', 'Online', 'VIP']
    
    data = []
    for date in dates:
        for product in products:
            for country in countries[:3]:  # Limiter pour la démo
                for channel in channels[:2]:
                    # Générer des ventes avec saisonnalité
                    base_demand = 50
                    seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * date.dayofyear / 365)
                    holiday_boost = 1.5 if date.month in [11, 12, 1] else 1.0
                    
                    quantity = int(np.random.poisson(base_demand * seasonal_factor * holiday_boost))
                    
                    data.append({
                        'date': date,
                        'product_id': product,
                        'country': country,
                        'channel': channel,
                        'quantity': quantity,
                        'price': 5000 if product == 'BAG-001' else 8000,
                        'collection': 'Spring 2024' if date.month in [3, 4, 5] else 'Fall 2024'
                    })
    
    return pd.DataFrame(data)

def train_and_register_model():
    """
    Entraînement avec tracking complet MLflow
    """
    
    print("🚀 Démarrage de l'entraînement avec MLflow tracking...")
    
    # Chargement des données
    print("📊 Chargement des données...")
    df = load_training_data()
    print(f"   - {len(df)} échantillons chargés")
    
    # Feature engineering
    print("🔧 Feature engineering...")
    feature_engine = LuxuryForecastFeatureEngine()
    df_features = feature_engine.create_features(df)
    
    # Sélection des features
    exclude_cols = ['date', 'product_id', 'quantity', 'product_name', 'forecast_week']
    feature_cols = [col for col in df_features.columns 
                   if col not in exclude_cols and not col.startswith('Unnamed')]
    
    X = df_features[feature_cols].fillna(0)
    y = df_features['quantity']
    
    # Split temporel
    print("✂️  Split temporel des données...")
    tscv = TimeSeriesSplit(n_splits=5)
    splits = list(tscv.split(X))
    train_idx, test_idx = splits[-1]  # Utiliser le dernier split pour train/test
    
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    print(f"   - Train: {len(X_train)} échantillons")
    print(f"   - Test: {len(X_test)} échantillons")
    
    # Démarrage d'une "run" MLflow
    run_name = f"xgboost_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    with mlflow.start_run(run_name=run_name):
        
        # 1. LOG DES PARAMÈTRES
        params = {
            'max_depth': 6,
            'learning_rate': 0.05,
            'n_estimators': 500,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'objective': 'reg:squarederror'
        }
        mlflow.log_params(params)
        
        # Log des infos dataset
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        mlflow.log_param("features_count", len(feature_cols))
        mlflow.log_param("experiment_name", EXPERIMENT_NAME)
        
        # 2. ENTRAÎNEMENT
        print("🎯 Entraînement du modèle...")
        model = xgb.XGBRegressor(**params, random_state=42)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=50,
            verbose=False
        )
        
        # 3. ÉVALUATION ET LOG DES MÉTRIQUES
        print("📈 Évaluation du modèle...")
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # MAPE (en évitant division par zéro)
        mask = y_test != 0
        mape = (np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])).mean() * 100 if mask.any() else 0
        
        mlflow.log_metrics({
            'mae': mae,
            'rmse': rmse,
            'r2_score': r2,
            'mape': mape
        })
        
        print(f"✅ Résultats:")
        print(f"   - MAE: {mae:.2f}")
        print(f"   - RMSE: {rmse:.2f}")
        print(f"   - R²: {r2:.3f}")
        print(f"   - MAPE: {mape:.1f}%")
        
        # 4. LOG DES ARTIFACTS (feature importance)
        try:
            import matplotlib
            matplotlib.use('Agg')  # Backend non-interactif
            import matplotlib.pyplot as plt
            
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            feature_importance.head(15).plot(x='feature', y='importance', kind='barh', ax=ax)
            plt.title('Top 15 Feature Importance')
            plt.tight_layout()
            plt.savefig('/tmp/feature_importance.png', dpi=100, bbox_inches='tight')
            plt.close()
            mlflow.log_artifact('/tmp/feature_importance.png', artifact_path="plots")
            
            # Prédictions vs réalité
            fig, ax = plt.subplots(figsize=(10, 6))
            plt.scatter(y_test, y_pred, alpha=0.5)
            plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
            plt.xlabel('Actual')
            plt.ylabel('Predicted')
            plt.title('Predictions vs Actual')
            plt.savefig('/tmp/predictions_scatter.png', dpi=100, bbox_inches='tight')
            plt.close()
            mlflow.log_artifact('/tmp/predictions_scatter.png', artifact_path="plots")
        except ImportError:
            print("⚠️  matplotlib non disponible, saut des plots")
        
        # 5. LOG DU MODÈLE
        print("💾 Enregistrement du modèle dans MLflow...")
        mlflow.xgboost.log_model(
            model,
            artifact_path="model",
            registered_model_name="luxury_demand_forecast"
        )
        
        print("✅ Modèle enregistré dans MLflow Registry")
        
        # 6. TAGGING pour filtrer les modèles
        mlflow.set_tag("model_type", "xgboost")
        mlflow.set_tag("dataset", "sales_synthetic")
        mlflow.set_tag("environment", "development")
        mlflow.set_tag("training_date", datetime.now().strftime('%Y-%m-%d'))
        
        run_id = mlflow.active_run().info.run_id
        print(f"🎯 Run ID: {run_id}")
        print(f"📊 Voir résultats: {MLFLOW_TRACKING_URI}/#/experiments")
        
        return run_id

if __name__ == "__main__":
    try:
        run_id = train_and_register_model()
        print(f"\n✅ Entraînement terminé avec succès!")
        print(f"   Run ID: {run_id}")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'entraînement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
