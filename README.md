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

## Avec plus de temps

- **Plateaux personnalisables** : permettre de personnaliser les cases du
  plateau, sur le modèle des extensions (add-ons) des jeux de table modernes.
  Le plateau est déjà une définition statique séparée de l'état de la partie
  (`Board` dans `app/game/board.py`), ce qui rend ce point accessible.
- **Composant `Square` côté frontend** : extraire de `Board.tsx` tout le contenu
  d'une case (nom, prix, couleur du propriétaire, pions) dans un sous-composant.
  `Board` ne garderait que la grille et le placement des cases.
