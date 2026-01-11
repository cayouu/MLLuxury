# Kubernetes Manifests

Manifests Kubernetes pour déployer le service de prévision ML sur AKS (Azure Kubernetes Service).

## Structure

- `namespace.yaml` - Namespace Kubernetes
- `configmap.yaml` - Configuration de l'application
- `secret.yaml` - Secrets (à créer avec vos valeurs)
- `deployment.yaml` - Déploiement des pods
- `service.yaml` - Service ClusterIP
- `hpa.yaml` - Horizontal Pod Autoscaler
- `ingress.yaml` - Ingress pour exposition externe

## Prérequis

1. Cluster AKS configuré
2. `kubectl` configuré pour votre cluster
3. Image Docker pushée dans Azure Container Registry
4. Secret ACR créé: `kubectl create secret docker-registry acr-secret --docker-server=<acr-name>.azurecr.io --docker-username=<acr-name> --docker-password=<acr-password> -n ml-forecast`

## Déploiement

### 1. Créer le namespace

```bash
kubectl apply -f namespace.yaml
```

### 2. Créer les secrets

```bash
# Modifier secret.yaml avec vos valeurs
kubectl apply -f secret.yaml
```

### 3. Appliquer les ressources

```bash
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
kubectl apply -f ingress.yaml  # Optionnel
```

### 4. Vérifier le déploiement

```bash
kubectl get pods -n ml-forecast
kubectl get svc -n ml-forecast
kubectl get hpa -n ml-forecast
```

### 5. Voir les logs

```bash
kubectl logs -f deployment/forecast-service -n ml-forecast
```

## Mise à jour de l'image

Pour mettre à jour l'image Docker:

```bash
kubectl set image deployment/forecast-service forecast-api=<new-image-tag> -n ml-forecast
kubectl rollout status deployment/forecast-service -n ml-forecast
```

## Rollback

```bash
kubectl rollout undo deployment/forecast-service -n ml-forecast
```
