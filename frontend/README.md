# Luxury Forecast – Frontend Angular 18

Interface Angular pour appeler l’**API .NET** et l’**API Python** via des pages dédiées et des boutons.

## Technologies

- Angular 18 (composants standalone)
- TypeScript
- Angular Router, HttpClient
- RxJS

## Lancer le frontend

```bash
cd frontend
npm install
npm start
```

Ouvre **http://localhost:4200**

## Utilisation

1. **Page d’accueil** (`/`) : deux boutons **API .NET** et **API Python** pour aller sur la page correspondante.
2. **Page API .NET** (`/api-dotnet`) : champs (collection, horizon, IDs produits) et boutons **Plan de production** et **Prévisions**. Bouton **Retour à l’accueil** en haut.
3. **Page API Python** (`/api-python`) : champs (IDs produits, horizon) et boutons **Prévisions**, **Health**, **Métriques modèle**. Bouton **Retour à l’accueil** en haut.

Le résultat (ou un message d’erreur) s’affiche sous les boutons après chaque appel.

## Backends

- **API .NET** : doit tourner sur **http://localhost:5000**  
  `cd LuxuryForecast.API && dotnet run`
- **API Python** : doit tourner sur **http://localhost:8000**  
  `cd forecast-service && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

En développement, le proxy Angular (`proxy.conf.json`) redirige :
- `/api` → http://localhost:5000
- `/python-api` → http://localhost:8000 (le préfixe `/python-api` est retiré côté Python)

## Structure

```
src/app/
├── pages/
│   ├── home/                 # Accueil, boutons de navigation
│   ├── api-dotnet/           # Page + composant API .NET
│   └── api-python/           # Page + composant API Python
├── services/
│   ├── api-dotnet.service.ts # Appels HTTP vers l’API .NET
│   └── api-python.service.ts # Appels HTTP vers l’API Python
├── utils/
│   └── http-error.util.ts   # Message d’erreur commun
├── app.config.ts
├── app.routes.ts
└── app.component.ts
```

## Build

```bash
npm run build
```

Les fichiers de sortie sont dans `dist/frontend/`.
