"""
Pipeline d'entraînement du modèle de prévision de demande
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from app.models.xgboost_predictor import LuxuryDemandPredictor
from app.features.feature_engineering import LuxuryForecastFeatureEngine

def load_training_data(data_path: str) -> pd.DataFrame:
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

def train_model():
    """Pipeline d'entraînement complet"""
    print("Loading training data...")
    df = load_training_data("data/training_data.csv")
    
    print(f"Data shape: {df.shape}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    print("Training model...")
    predictor = LuxuryDemandPredictor()
    model = predictor.train(df, target='quantity')
    
    print("Model training completed!")
    print(f"Feature importance (top 10):")
    
    if hasattr(model, 'feature_importances_'):
        feature_names = predictor.feature_engine.create_features(df).columns
        exclude_cols = ['date', 'product_id', 'quantity', 'product_name', 'forecast_week']
        feature_cols = [col for col in feature_names 
                       if col not in exclude_cols and not col.startswith('Unnamed')]
        
        importances = model.feature_importances_
        top_indices = np.argsort(importances)[-10:][::-1]
        
        for idx in top_indices:
            print(f"  {feature_cols[idx]}: {importances[idx]:.4f}")
    
    return predictor, model

if __name__ == "__main__":
    predictor, model = train_model()
    print("\nTraining pipeline completed successfully!")
