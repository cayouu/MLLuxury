# MLflow Tracking Server

Serveur MLflow pour le versioning et le registry des modèles de prévision de demande.

## Démarrage

```bash
docker-compose up -d
```

Le serveur MLflow sera accessible sur `http://localhost:5000`

## Configuration

- **Backend Store:** PostgreSQL (pour métadonnées)
- **Artifact Store:** Système de fichiers local (`./mlartifacts`)
- **Port:** 5000

## Utilisation

1. Accéder à l'UI MLflow: http://localhost:5000
2. L'expérience `luxury_demand_forecast` sera créée automatiquement lors du premier entraînement
3. Les modèles peuvent être promus en Production via l'UI ou le script `scripts/promote_model.py`

## Production

Pour la production, considérer:
- Utiliser un stockage objet (S3, Azure Blob, GCS) pour les artifacts
- Configurer l'authentification
- Utiliser HTTPS
- Mettre en place des backups de la base PostgreSQL
