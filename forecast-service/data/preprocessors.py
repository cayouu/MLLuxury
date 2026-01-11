"""
Preprocessors pour les données de ventes
"""
import pandas as pd
import numpy as np
from typing import List, Optional

class SalesDataPreprocessor:
    """Preprocesseur pour les données de ventes historiques"""
    
    def __init__(self):
        self.scalers = {}
        self.outlier_threshold = 3  # Écart-type pour détection d'outliers
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoyage des données"""
        df = df.copy()
        
        # Supprimer les doublons
        df = df.drop_duplicates()
        
        # Gérer les valeurs manquantes
        df = self._handle_missing_values(df)
        
        # Détecter et traiter les outliers
        df = self._handle_outliers(df)
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gérer les valeurs manquantes"""
        # Remplacer les valeurs manquantes dans les colonnes numériques par la médiane
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].median(), inplace=True)
        
        # Remplacer les valeurs manquantes dans les colonnes catégorielles par "Unknown"
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col].fillna("Unknown", inplace=True)
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Détecter et traiter les outliers"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                
                # Remplacer les outliers par la limite (capping)
                upper_bound = mean + self.outlier_threshold * std
                lower_bound = mean - self.outlier_threshold * std
                
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def aggregate_by_period(self, df: pd.DataFrame, period: str = 'W') -> pd.DataFrame:
        """Agréger les données par période (semaine, mois, etc.)"""
        if 'date' not in df.columns:
            raise ValueError("DataFrame must have a 'date' column")
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        aggregated = df.groupby([pd.Grouper(freq=period), 'product_id', 'country', 'channel']).agg({
            'quantity': 'sum',
            'price': 'mean',
            'revenue': 'sum' if 'revenue' in df.columns else lambda x: (x * df.loc[x.index, 'quantity']).sum()
        }).reset_index()
        
        return aggregated
