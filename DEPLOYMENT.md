# Guide de Déploiement Complet

Guide complet pour déployer le système de prévision de demande avec MLflow, Docker et Kubernetes.

## Table des matières

1. [MLflow Tracking Server](#mlflow-tracking-server)
2. [Build et Push Docker](#build-et-push-docker)
3. [Déploiement Kubernetes](#déploiement-kubernetes)
4. [Pipeline CI/CD](#pipeline-cicd)
5. [Intégration .NET](#intégration-net)

## MLflow Tracking Server

### Démarrage local

```bash
cd mlflow-server
docker-compose up -d
```

Accéder à l'UI MLflow: http://localhost:5000

### Configuration

Le serveur MLflow utilise:
- **Backend Store:** PostgreSQL (métadonnées)
- **Artifact Store:** Fichier système local (`./mlartifacts`)
- **Port:** 5000

### Production

Pour la production, considérer:
- Stockage objet (Azure Blob, S3, GCS) pour les artifacts
- Authentification HTTPS
- Backups PostgreSQL
- Réplication pour haute disponibilité

## Build et Push Docker

### Build local

```bash
cd forecast-service
docker build -t luxuryhouse/forecast-service:1.0.0 .
```

### Avec script (Linux/Mac)

```bash
chmod +x build.sh
./build.sh 1.0.0
```

### Avec script (Windows)

```powershell
.\build.ps1 -Version "1.0.0"
```

### Push vers Azure Container Registry

1. Se connecter à Azure:
```bash
az login
az acr login --name luxuryhouse
```

2. Tag et push:
```bash
docker tag luxuryhouse/forecast-service:1.0.0 luxuryhouse.azurecr.io/luxuryhouse/forecast-service:1.0.0
docker push luxuryhouse.azurecr.io/luxuryhouse/forecast-service:1.0.0
```

## Déploiement Kubernetes

### Prérequis

1. Cluster AKS configuré
2. `kubectl` configuré
3. Image Docker pushée dans ACR
4. Secret ACR créé:

```bash
kubectl create secret docker-registry acr-secret \
  --docker-server=luxuryhouse.azurecr.io \
  --docker-username=luxuryhouse \
  --docker-password=<acr-password> \
  -n ml-forecast
```

### Déploiement étape par étape

1. **Créer le namespace:**
```bash
kubectl apply -f k8s/namespace.yaml
```

2. **Créer les secrets:**
```bash
# Modifier k8s/secret.yaml avec vos valeurs
kubectl apply -f k8s/secret.yaml
```

3. **Appliquer les ressources:**
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml  # Optionnel
```

4. **Vérifier le déploiement:**
```bash
kubectl get pods -n ml-forecast
kubectl get svc -n ml-forecast
kubectl get hpa -n ml-forecast
```

5. **Voir les logs:**
```bash
kubectl logs -f deployment/forecast-service -n ml-forecast
```

### Mise à jour

Pour mettre à jour l'image:

```bash
kubectl set image deployment/forecast-service \
  forecast-api=luxuryhouse.azurecr.io/luxuryhouse/forecast-service:1.0.1 \
  -n ml-forecast

kubectl rollout status deployment/forecast-service -n ml-forecast
```

### Rollback

```bash
kubectl rollout undo deployment/forecast-service -n ml-forecast
```

## Pipeline CI/CD

### Configuration Azure DevOps

1. **Créer les Service Connections:**
   - `ACR-Connection`: Connection vers Azure Container Registry
   - `AKS-Prod`: Connection vers le cluster AKS

2. **Créer le pipeline:**
   - Créer un nouveau pipeline dans Azure DevOps
   - Sélectionner le repository
   - Utiliser `azure-pipelines.yml`

### Étapes du pipeline

1. **Build:** Build et push de l'image Docker
2. **Test:** Exécution des tests (si disponibles)
3. **Deploy:** Déploiement sur AKS (uniquement sur `main`)

### Déclenchement

Le pipeline se déclenche automatiquement sur:
- Push sur `main` ou `develop`
- Modifications dans `forecast-service/` ou `k8s/`

## Intégration .NET

### Configuration Production

Le fichier `appsettings.Production.json` configure:
- URL du service ML (service Kubernetes)
- Timeout et retry policies

### Retry Policy et Circuit Breaker

Le service utilise:
- **Retry Policy:** 3 tentatives avec backoff exponentiel
- **Circuit Breaker:** Ouvre après 5 erreurs, reste ouvert 30s

### Variables d'environnement

Pour Kubernetes, utiliser ConfigMap/Secret:

```yaml
env:
- name: MLService__BaseUrl
  valueFrom:
    configMapKeyRef:
      name: forecast-config
      key: ML_SERVICE_URL
```

## Entraînement et Promotion de Modèle

### Entraînement avec MLflow

```bash
cd forecast-service/training
export MLFLOW_TRACKING_URI=http://localhost:5000
python train_pipeline_mlflow.py
```

### Promotion vers Production

```bash
cd forecast-service/scripts
python promote_model.py --run-id <run_id>
```

Ou lister les modèles:

```bash
python promote_model.py --list
```

### Via MLflow UI

1. Aller sur http://localhost:5000
2. Sélectionner le modèle
3. Transition: Staging → Production

## Monitoring

### Health Checks

- **Liveness:** `/health`
- **Readiness:** `/health`
- **Model Info:** `/model/info`
- **Metrics:** `/model/metrics`

### Logs

```bash
# Logs Kubernetes
kubectl logs -f deployment/forecast-service -n ml-forecast

# Logs MLflow
docker-compose -f mlflow-server/docker-compose.yml logs -f
```

### Métriques

- CPU/Memory via HPA
- Latence via Application Insights
- Métriques ML via MLflow UI

## Troubleshooting

### Le modèle ne charge pas

1. Vérifier que MLflow est accessible:
```bash
curl http://mlflow-server:5000/health
```

2. Vérifier les logs du pod:
```bash
kubectl logs deployment/forecast-service -n ml-forecast
```

3. Vérifier les variables d'environnement:
```bash
kubectl describe pod <pod-name> -n ml-forecast
```

### Erreur de connexion au service ML

1. Vérifier que le service est accessible:
```bash
kubectl get svc -n ml-forecast
```

2. Tester depuis un pod:
```bash
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://forecast-service.ml-forecast.svc.cluster.local/health
```

### Circuit Breaker ouvert

Attendre 30 secondes ou redémarrer le service .NET pour réinitialiser le circuit breaker.
