import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

class LuxuryForecastFeatureEngine:
    def __init__(self):
        self.encoders = {}
        self.scaler = StandardScaler()
        # Modèles iconiques (exemple)
        self.iconic_models = ['BAG-001', 'BAG-002']
        # Mapping GDP par pays (exemple simplifié)
        self.gdp_mapping = {
            'FR': 45000, 'US': 65000, 'CN': 12000, 
            'JP': 40000, 'UK': 47000, 'CH': 85000
        }
        
    def create_features(self, df):
        """Création de features spécifiques au luxe"""
        df = df.copy()
        
        # S'assurer que 'date' est datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        else:
            # Si pas de colonne date, créer une date par défaut
            df['date'] = pd.Timestamp.now()
        
        # Features temporelles
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['is_peak_season'] = df['month'].isin([11, 12, 1, 2]).astype(int)  # Fêtes + Fashion Weeks
        df['weeks_to_fashion_week'] = self._calculate_fashion_week_distance(df['date'])
        
        # Features produit
        if 'product_id' in df.columns:
            df['is_iconic_model'] = df['product_id'].isin(self.iconic_models).astype(int)
        else:
            df['is_iconic_model'] = 0
            
        # Features géographiques
        if 'country' in df.columns:
            df['country_gdp_per_capita'] = df['country'].map(self.gdp_mapping).fillna(40000)
            df['is_key_market'] = df['country'].isin(['US', 'CN', 'JP', 'FR', 'UK']).astype(int)
        else:
            df['country_gdp_per_capita'] = 40000
            df['is_key_market'] = 0
        
        # Features de prix (si disponibles)
        if 'price' not in df.columns:
            df['price'] = 5000  # Prix par défaut
        df['price_tier'] = pd.cut(
            df['price'], 
            bins=[0, 2000, 5000, 10000, np.inf], 
            labels=['Entry', 'Core', 'Premium', 'Exceptional']
        )
        
        # Lag features (nécessite des données historiques)
        if 'quantity' in df.columns and 'product_id' in df.columns:
            for lag in [1, 2, 4, 8, 12]:
                df[f'sales_lag_{lag}w'] = df.groupby('product_id')['quantity'].shift(lag).fillna(0)
            
            # Rolling statistics
            df['sales_rolling_4w'] = df.groupby('product_id')['quantity'].transform(
                lambda x: x.rolling(window=4, min_periods=1).mean()
            )
            df['sales_rolling_12w'] = df.groupby('product_id')['quantity'].transform(
                lambda x: x.rolling(window=12, min_periods=1).mean()
            )
        else:
            # Valeurs par défaut pour les prédictions futures
            for lag in [1, 2, 4, 8, 12]:
                df[f'sales_lag_{lag}w'] = 0
            df['sales_rolling_4w'] = 10
            df['sales_rolling_12w'] = 10
        
        # Features canal
        if 'channel' in df.columns:
            df['is_online'] = (df['channel'] == 'Online').astype(int)
        else:
            df['is_online'] = 0
        
        # Encodage catégoriel
        for col in ['collection', 'country', 'channel', 'price_tier']:
            if col in df.columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Gérer les nouvelles valeurs
                    try:
                        df[f'{col}_encoded'] = self.encoders[col].transform(df[col].astype(str))
                    except ValueError:
                        # Nouvelle valeur non vue, utiliser 0
                        df[f'{col}_encoded'] = 0
        
        return df
    
    def _calculate_fashion_week_distance(self, dates):
        """Distance à la prochaine Fashion Week (Paris, Milan, NYC)"""
        if isinstance(dates, pd.Series):
            dates_series = dates
        else:
            dates_series = pd.Series([dates])
        
        min_distances = []
        for date in dates_series:
            year = date.year
            fashion_weeks = [
                pd.Timestamp(year, 2, 15),   # Paris FW Février
                pd.Timestamp(year, 9, 20),   # Paris FW Septembre
                pd.Timestamp(year + 1, 2, 15) if date.month > 9 else pd.Timestamp(year, 2, 15)
            ]
            
            distances = [(fw - date).days for fw in fashion_weeks if (fw - date).days >= 0]
            min_distances.append(min(distances) if distances else 365)
        
        return min_distances if len(min_distances) > 1 else min_distances[0]
