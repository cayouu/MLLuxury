# Luxury Demand Forecast Service

Service ML Python pour la prévision de demande dans le secteur du luxe (sacs à main et malles).

## Architecture

- **FastAPI** : API REST pour exposer les prédictions
- **XGBoost** : Modèle de machine learning pour les prévisions
- **MLflow** : Gestion des modèles et tracking des expériences
- **Pandas/NumPy** : Traitement des données

## Installation

```bash
pip install -r requirements.txt
```

## Démarrage du service

```bash
cd forecast-service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur `http://localhost:8000`

## Documentation API

Une fois le service démarré, accédez à :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

## Endpoints principaux

### POST /forecast
Génère des prévisions de demande pour une liste de produits.

**Request body:**
```json
{
  "product_ids": ["BAG-001", "BAG-002"],
  "start_date": "2024-01-01",
  "forecast_horizon_weeks": 13,
  "channel": "All",
  "countries": ["FR", "US"]
}
```

### GET /model/metrics
Retourne les métriques du modèle en production.

### GET /health
Health check endpoint.

## Entraînement du modèle

```bash
cd training
python train_pipeline.py
```

## Structure des données

Les données d'entraînement doivent contenir :
- `date` : Date de la vente
- `product_id` : ID du produit
- `quantity` : Quantité vendue
- `country` : Pays de la vente
- `channel` : Canal de vente (Boutique, Online, VIP)
- `price` : Prix du produit
- `collection` : Collection (optionnel)
