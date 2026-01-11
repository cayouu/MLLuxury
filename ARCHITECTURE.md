# Architecture du Système de Prévision de Demande

## Vue d'ensemble

Ce projet illustre une architecture microservices pour l'intégration de modèles ML dans un système de production .NET, avec un focus sur le secteur du luxe (maroquinerie).

## Composants Principaux

### 1. API .NET (LuxuryForecast.API)

**Technologies:**
- ASP.NET Core 8.0
- C# 12 (.NET 8)

**Structure:**
```
LuxuryForecast.API/
├── Controllers/
│   ├── ForecastController.cs          # Endpoints pour les prévisions
│   ├── HistoricalDataController.cs    # Gestion des données historiques
│   └── ProductionPlanningController.cs # Planification de production
├── Services/
│   ├── ForecastMLService.cs           # Service d'intégration ML (HTTP)
│   ├── DataAggregationService.cs      # Agrégation des données de ventes
│   ├── InventoryOptimizationService.cs # Logique métier d'optimisation
│   └── ProductService.cs              # Service produits
├── Models/
│   └── SalesPredictionRequest.cs      # Modèles de données
└── Program.cs                         # Configuration et DI
```

**Endpoints principaux:**
- `POST /api/Forecast` - Générer des prévisions
- `GET /api/ProductionPlanning/recommendations/{collectionId}` - Plan de production
- `GET /api/HistoricalData/prepare-training-data` - Préparer données d'entraînement

### 2. Service ML Python (forecast-service)

**Technologies:**
- FastAPI
- XGBoost / scikit-learn
- Pandas / NumPy
- MLflow (optionnel)

**Structure:**
```
forecast-service/
├── app/
│   ├── main.py                        # API FastAPI
│   ├── models/
│   │   └── xgboost_predictor.py      # Modèle XGBoost
│   ├── features/
│   │   └── feature_engineering.py    # Feature engineering
│   └── utils/
│       ├── model_registry.py          # MLflow utilities
│       └── validators.py              # Validation
├── training/
│   ├── train_pipeline.py              # Pipeline d'entraînement
│   └── hyperparameter_tuning.py      # Optimisation hyperparamètres
└── data/
    └── preprocessors.py               # Préprocessing
```

**Endpoints:**
- `POST /forecast` - Prédictions de demande
- `GET /model/metrics` - Métriques du modèle
- `GET /health` - Health check

## Flux de Données

### Prévision de Demande

```
1. Client → API .NET (ProductionPlanningController)
2. API .NET → ForecastMLService (service interne)
3. ForecastMLService → Service Python (HTTP POST /forecast)
4. Service Python → Feature Engineering → Modèle XGBoost
5. Service Python → Prédictions + Intervalles de confiance
6. ForecastMLService → Traitement métier (calcul production optimale)
7. API .NET → Réponse avec recommandations et alertes
```

### Entraînement du Modèle

```
1. DataAggregationService → Agrégation données historiques
2. Export données → CSV/Parquet (ou API directe)
3. train_pipeline.py → Feature Engineering → Entraînement XGBoost
4. MLflow → Enregistrement modèle et métriques
5. Déploiement → Chargement modèle dans service Python
```

## Features ML Spécifiques au Luxe

### Feature Engineering

1. **Temporelles:**
   - Saisonnalité (Fashion Weeks, fêtes)
   - Périodes de pointe
   - Distance aux Fashion Weeks

2. **Produits:**
   - Modèles iconiques (flag)
   - Tier de prix (Entry, Core, Premium, Exceptional)
   - Âge de la collection

3. **Géographiques:**
   - Pays/GDP par habitant
   - Marchés clés (flag)
   - Indicateurs économiques

4. **Canal:**
   - Boutique vs Online
   - Taux de pénétration online

5. **Historiques:**
   - Lag features (1, 2, 4, 8, 12 semaines)
   - Rolling statistics (moyennes, volatilité)
   - Trends

### Modèle

- **XGBoost Regressor** pour séries temporelles
- Validation temporelle (TimeSeriesSplit)
- Hyperparamètres optimisés pour prévisions
- MLflow pour tracking et versioning

## Intégration

### Communication Inter-Services

- **Protocole:** HTTP/REST
- **Format:** JSON
- **Service Discovery:** Configuration (appsettings.json)
- **Timeout:** Par défaut HttpClient (100s)

### Cache

- **MemoryCache** dans .NET pour optimiser les appels ML
- TTL: 6 heures pour les prévisions
- Clé: `forecast_{productIds}_{horizonWeeks}`

### Gestion d'Erreurs

- Logging structuré (ILogger)
- Try-catch avec messages d'erreur explicites
- Health checks pour monitoring

## Déploiement

### Développement Local

1. **Service Python:**
   ```bash
   cd forecast-service
   pip install -r requirements.txt
   python start.py
   ```

2. **API .NET:**
   ```bash
   cd LuxuryForecast.API
   dotnet run
   ```

### Production (Recommandations)

- **Containerisation:** Docker pour les deux services
- **Orchestration:** Kubernetes ou Docker Compose
- **MLflow Server:** Pour gestion des modèles
- **Base de données:** SQL Server pour données historiques
- **Monitoring:** Application Insights / Prometheus
- **Load Balancing:** Pour haute disponibilité

## Métriques de Performance

### ML

- **MAPE:** 8-12% (objectif)
- **R²:** 0.85-0.90
- **Précision modèles iconiques:** 95%+

### API

- **Latence prévision:** < 500ms (avec cache)
- **Throughput:** 100+ req/s
- **Disponibilité:** 99.9%

## Évolutions Possibles

1. **Real-time:** Streaming avec Kafka pour données temps réel
2. **MLOps:** Pipeline CI/CD pour retraining automatique
3. **A/B Testing:** Tests de différents modèles en parallèle
4. **Multi-modèles:** Ensemble de modèles (XGBoost + LSTM)
5. **Explicabilité:** SHAP values pour expliquer les prédictions
6. **Dashboard:** Interface de visualisation (React/Vue)
