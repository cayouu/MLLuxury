# Luxury Forecast Frontend

Interface Vue.js pour visualiser les prévisions de demande et la planification de production.

## Technologies

- Vue 3 (Composition API)
- TypeScript
- Vue Router
- Axios
- Chart.js
- Vite

## Installation

```bash
cd frontend
npm install
```

## Développement

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:3000`

## Build

```bash
npm run build
```

## Configuration

L'API backend est configurée dans `vite.config.ts` avec un proxy vers `http://localhost:5000`.

Pour changer l'URL de l'API, modifiez la configuration dans:
- `vite.config.ts` (proxy pour le développement)
- `src/services/api.ts` (baseURL pour la production)

## Fonctionnalités

### Dashboard
- Vue d'ensemble des métriques clés
- Alertes de production
- Top 10 des recommandations

### Prévisions
- Liste des prévisions par produit
- Graphiques de prévisions hebdomadaires
- Intervalles de confiance
- Détails par semaine

### Planification de Production
- Génération de plan par collection
- Recommandations prioritaires
- Alertes de rupture de stock
- Résumé financier

## Structure

```
frontend/
├── src/
│   ├── views/          # Pages principales
│   │   ├── Dashboard.vue
│   │   ├── Forecasts.vue
│   │   └── Production.vue
│   ├── services/       # Services API
│   │   └── api.ts
│   ├── router/         # Configuration routing
│   │   └── index.ts
│   ├── App.vue         # Composant racine
│   ├── main.ts         # Point d'entrée
│   └── style.css       # Styles globaux
├── index.html
├── package.json
└── vite.config.ts
```
