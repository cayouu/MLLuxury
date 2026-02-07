# Luxury Forecast – Frontend Angular 18

Une seule page avec un menu pour appeler l’**API .NET** ou l’**API Python**.

## Lancer le frontend

```bash
cd frontend
npm install
npm start
```

Ouvre http://localhost:4200

## Utilisation

1. **API cible** : choisir « API .NET » ou « API Python ».
2. **Action** : selon l’API, choisir l’action dans le menu déroulant (plan de production, prévisions, health, métriques).
3. Renseigner les options (collection, IDs produits, horizon) si besoin.
4. Cliquer sur **Appeler l’API** : le résultat (ou l’erreur) s’affiche en dessous.

## Backends

- **API .NET** : doit tourner sur **http://localhost:5000**  
  `cd LuxuryForecast.API && dotnet run`
- **API Python** : doit tourner sur **http://localhost:8000**  
  `cd forecast-service && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

Le proxy Angular redirige `/api` vers le .NET et `/python-api` vers le Python.
