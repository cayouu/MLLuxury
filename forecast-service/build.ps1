# PowerShell script de build et push de l'image Docker

param(
    [string]$Version = "1.0.0",
    [string]$ACRName = "luxuryhouse.azurecr.io"
)

$ImageName = "luxuryhouse/forecast-service"

Write-Host "🏗️  Building Docker image..." -ForegroundColor Cyan
docker build -t "${ImageName}:$Version" -t "${ImageName}:latest" .

Write-Host "🏷️  Tagging image for Azure Container Registry..." -ForegroundColor Cyan
docker tag "${ImageName}:$Version" "$ACRName/${ImageName}:$Version"
docker tag "${ImageName}:latest" "$ACRName/${ImageName}:latest"

Write-Host "📤 Pushing to Azure Container Registry..." -ForegroundColor Cyan
if (Get-Command az -ErrorAction SilentlyContinue) {
    az acr login --name $ACRName.Replace(".azurecr.io", "")
    docker push "$ACRName/${ImageName}:$Version"
    docker push "$ACRName/${ImageName}:latest"
    Write-Host "✅ Image pushed: $ACRName/${ImageName}:$Version" -ForegroundColor Green
} else {
    Write-Host "⚠️  Azure CLI not found. Skipping push." -ForegroundColor Yellow
    Write-Host "   Image built locally: ${ImageName}:$Version" -ForegroundColor Yellow
}
