# PLAN — Monopoly simplifié multijoueur

Timebox : 2 heures. Backend Python + FastAPI, frontend React + TypeScript.

## Étapes

| # | Étape | Statut |
|---|---|---|
| 1 | Squelette exécutable de bout en bout (FastAPI + Vite/React/TS, `/api/health`) | Fait |
| 2 | Moteur de jeu pur + tests unitaires des règles | À faire |
| 3 | API REST : créer, rejoindre, lire l'état, jouer son tour | À faire |
| 4 | Temps réel : WebSocket par partie, diffusion de l'état | À faire |
| 5 | Frontend jouable : lobby, plateau, joueurs, tour, journal, gagnant | À faire |
| 6 | Finition : README complet, essai réel à plusieurs onglets | À faire |

Priorité en cas de manque de temps : on simplifie d'abord le visuel de l'étape 5,
jamais les tests du moteur.

## Journal des décisions

- **D1 — Achat sans fonds suffisants** : le joueur n'achète pas, rien ne se passe.
  La règle impose l'achat (« il l'achète »), donc pas de choix acheter/refuser.
- **D2 — Achat à 0 $** : autorisé (achat si argent ≥ prix).
- **D3 — Faillite** : le joueur qui ne peut pas payer le loyer verse tout ce qui
  lui reste au propriétaire ; ses propriétés redeviennent libres.
- **D4 — Salaire** : versé quand on passe ou s'arrête sur le départ ; pas au
  placement initial.
- **D5 — Ordre salaire / case** : salaire d'abord, puis l'effet de la case
  d'arrivée.
- **D6 — Plateau et constantes** : plateau fixe codé en dur (~16 cases, départ en
  case 0) ; 1 500 $ de départ, 200 $ de salaire, dé à 6 faces.
- **D7 — Démarrage** : le créateur choisit la taille (2 à 4) ; la partie démarre
  automatiquement quand elle est pleine ; ordre de jeu = ordre d'arrivée.
- **D8 — Identité** : pas de comptes ; le serveur remet un jeton de joueur à la
  jonction, gardé dans le `localStorage`. Seul son détenteur peut jouer son tour.
- **D9 — Tour** : un seul clic « Lancer le dé » résout tout le tour (déplacement,
  salaire, achat/loyer, faillite, joueur suivant). Pas de doubles.
- **D10 — Temps réel** : WebSocket par partie qui pousse l'état complet à chaque
  changement ; les actions passent par REST.
- **D11 — Persistance** : en mémoire seulement ; un redémarrage efface les parties.
- **D12 — Déconnexion / abandon** : non géré (noté pour « plus de temps »).
- **D13 — Dé injectable** : le dé est passé à la logique métier pour des tests
  déterministes.
- **D14 — Outillage Python** : `uv` (`pyproject.toml` + `uv.lock`, Python 3.12
  installé par uv). Code dans `backend/app/`, sans structure de paquet installable
  (la structure `src/` générée par uv a été retirée : inutile pour une app).
  Dépendances de dev : `pytest` et `httpx2` (Starlette déprécie `httpx` pour son
  client de test).
- **D15 — Communication front/back** : le proxy de Vite redirige `/api` vers le
  backend ; URL relatives côté frontend, pas de CORS, un seul port à ouvrir.
- **D16 — Frontend minimal** : React + TypeScript via Vite, sans bibliothèque
  d'état ni de style ; un routeur seulement si l'étape 5 l'exige.
- **D17 — Pas de tests frontend** dans le timebox : la logique métier est dans le
  backend, où elle est testée. Noté pour « plus de temps ».
