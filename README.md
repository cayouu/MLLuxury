# Luxury Demand Forecast - Système de Prévision de Demande pour Maroquinerie de Luxe

Exemple concret d'intégration et d'utilisation de modèles d'IA dans le secteur du luxe (sacs à main et malles) pour la prévision de la demande.

## Architecture du Projet

### Solution .NET (Backend API)
- **LuxuryForecast.API** : API ASP.NET Core 8
  - Controllers pour les prévisions, données historiques et planification de production
  - Services d'intégration avec le service ML Python
  - Modèles de données et logique métier

### Service ML Python
- **forecast-service** : Service FastAPI
  - Modèles XGBoost pour les prévisions
  - Feature engineering spécifique au luxe
  - Pipeline d'entraînement et hyperparameter tuning
  - Intégration MLflow (optionnel)

### Frontend Angular
- **frontend** : Interface utilisateur Angular 18
  - Page d’accueil avec navigation vers les API .NET et Python
  - Page dédiée aux appels API .NET (plan de production, prévisions)
  - Page dédiée aux appels API Python (prévisions, health, métriques modèle)
  - Services séparés par backend (`ApiDotnetService`, `ApiPythonService`)

## Technologies Utilisées

### Backend .NET
- ASP.NET Core 8.0
- Entity Framework Core (exemple)
- HttpClient pour communication avec service ML
- Memory Cache pour optimisation

### Service ML Python
- FastAPI
- XGBoost / Random Forest
- scikit-learn
- Pandas / NumPy
- MLflow (optionnel)

### Frontend Angular
- Angular 18 (standalone components)
- TypeScript
- Angular Router, HttpClient
- RxJS

## Démarrage Rapide

### Développement Local

#### 1. MLflow Tracking Server (optionnel pour développement)

```bash
cd mlflow-server
docker-compose up -d
```

Accéder à l'UI MLflow: http://localhost:5000

#### 2. Service ML Python

```bash
cd forecast-service
pip install -r requirements.txt

# Développement (sans MLflow)
python start.py

# Ou avec MLflow
export MLFLOW_TRACKING_URI=http://localhost:5000
python start.py
```

#### 3. API .NET

```bash
cd LuxuryForecast.API
dotnet restore
dotnet run
```

L'API sera accessible sur `http://localhost:5000` (voir `Properties/launchSettings.json`)

#### 4. Frontend Angular

```bash
cd frontend
npm install
npm start
```

L'interface sera accessible sur `http://localhost:4200`. Le proxy redirige `/api` vers l’API .NET (port 5000) et `/python-api` vers le service Python (port 8000).

### Production

Voir le guide complet de déploiement dans [DEPLOYMENT.md](DEPLOYMENT.md) pour:
- Déploiement avec Docker
- Déploiement Kubernetes (AKS)
- Pipeline CI/CD Azure DevOps
- Configuration MLflow en production

## Fonctionnalités

### Prévision de Demande
- Prédiction de la demande pour les 13 prochaines semaines (horizon configurable)
- Prise en compte de la saisonnalité (Fashion Weeks, fêtes)
- Features spécifiques au luxe (modèles iconiques, prix, pays, canaux)
- Intervalles de confiance pour chaque prédiction

### Planification de Production
- Recommandations de quantités de production optimales
- Détection des risques de rupture de stock
- Priorisation des produits selon plusieurs critères
- Alertes automatiques (risque élevé, incertitude)

### Intégration
- Communication HTTP/REST entre .NET et Python
- Cache pour optimiser les performances
- Logging et gestion d'erreurs

## Exemples d'Utilisation

### API .NET - Prévision pour une collection

```http
GET /api/ProductionPlanning/recommendations/Spring2024?horizonWeeks=13
```

Réponse :
```json
{
  "collectionId": "Spring2024",
  "generatedAt": "2024-01-15T10:30:00Z",
  "forecastHorizon": "13 weeks",
  "totalProductsAnalyzed": 3,
  "recommendations": [
    {
      "productId": "BAG-001",
      "totalPredictedDemand": 650.5,
      "recommendedProductionQuantity": 780,
      "confidenceLevel": 0.87,
      "riskOfStockout": 0.25
    }
  ],
  "alerts": [],
  "summary": {
    "totalUnitsToProduct": 2340,
    "highPriorityItems": 0,
    "estimatedRevenue": 11700000
  }
}
```

### Service ML Python - Prévision directe

```http
POST http://localhost:8000/forecast
Content-Type: application/json

{
  "product_ids": ["BAG-001", "BAG-002"],
  "start_date": "2024-01-15",
  "forecast_horizon_weeks": 13
}
```

## Métriques Attendues

- **MAPE** : 8-12% (excellent pour le luxe avec forte variabilité)
- **R²** : 0.85-0.90
- **Précision sur modèles iconiques** : 95%+

## Impact Business

- Réduction des ruptures de stock de 40%
- Diminution des invendus de 25%
- Optimisation de trésorerie (production juste nécessaire)
- Amélioration de la satisfaction client (disponibilité)

## Particularités du Luxe

- Gestion des collections limitées (scarcity intentionnelle)
- Pics imprévisibles (célébrités portant le produit)
- Importance du stock sécurité pour VIP/clientèle fidèle
- Saisonnalité marquée (Fashion Weeks, fêtes)

## Structure du Projet

```
.
├── LuxuryForecast.API/          # Backend .NET
│   ├── Controllers/
│   ├── Services/
│   ├── Models/
│   └── Program.cs
├── forecast-service/             # Service ML Python
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── features/
│   │   └── utils/
│   ├── training/
│   └── data/
├── frontend/                     # Frontend Angular 18
│   ├── src/app/
│   │   ├── pages/               # home, api-dotnet, api-python
│   │   ├── services/            # api-dotnet.service, api-python.service
│   │   └── utils/               # http-error.util
│   ├── proxy.conf.json          # Proxy /api → 5000, /python-api → 8000
│   └── angular.json
└── README.md
```

## Configuration

### appsettings.json (.NET)
```json
{
  "MLService": {
    "BaseUrl": "http://localhost:8000"
  }
}
```

### Variables d'environnement (Python)
```bash
MODEL_URI=models:/luxury_forecast_model/production
```

## Développement

Ce projet est un exemple complet pour développeur senior .NET avec connaissances en Python et ML. Il démontre :

1. Architecture microservices (.NET + Python)
2. Intégration ML dans un système de production
3. Feature engineering spécifique au domaine (luxe)
4. Bonnes pratiques (logging, cache, erreurs)
5. Documentation et structure de code professionnelle

## Notes

- Pour la production, configurer MLflow pour la gestion des modèles
- Adapter les modèles de données à votre schéma de base de données réel
- Implémenter l'authentification/autorisation selon vos besoins
- Ajouter des tests unitaires et d'intégration
