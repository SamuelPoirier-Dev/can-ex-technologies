# Monopoly simplifié multijoueur

Exercice Can-Ex Tech : un Monopoly simplifié jouable à plusieurs, chacun depuis
son navigateur. Backend Python + FastAPI, frontend React + TypeScript.

Le suivi des étapes et des décisions est dans [PLAN.md](PLAN.md).

## Prérequis

- [uv](https://docs.astral.sh/uv/) (installe Python 3.12 automatiquement)
- Node.js 20+ et npm

## Lancer le projet

Dans deux terminaux :

```bash
# Terminal 1, depuis backend/
uv run uvicorn app.main:app --reload --port 8000
```

```bash
# Terminal 2, depuis frontend/
npm install
npm run dev
```

Puis ouvrir http://localhost:5173. Le serveur Vite redirige `/api` vers le
backend (port 8000).

## Lancer les tests

```bash
# Depuis backend/
uv run pytest
```
