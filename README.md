# Monopoly Québec : Monopoly simplifié multijoueur

Exercice Can-Ex Tech (timebox de 2 heures). Un Monopoly simplifié où chaque
joueur joue depuis son propre navigateur : un joueur crée une partie de 2 à 4
joueurs, les autres la rejoignent avec un lien ou un code, et tout le monde voit
la partie évoluer en direct (déplacements, achats, loyers, faillites, gagnant).

- **Backend** : Python 3.12, FastAPI, WebSocket.
- **Frontend** : React + TypeScript (Vite).
- **Suivi du travail** : les étapes et toutes les décisions numérotées (D1 à D44)
  sont dans [PLAN.md](PLAN.md).

## Lancer le projet

Prérequis : [uv](https://docs.astral.sh/uv/) (il installe Python 3.12 tout
seul) et Node.js 20+ avec npm.

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

Puis ouvrir http://localhost:5173. Le serveur Vite redirige `/api` et `/ws`
vers le backend (port 8000), donc le navigateur ne parle qu'à une seule adresse.

**Jouer à plusieurs sur une seule machine** : créer une partie, puis ouvrir le
lien affiché dans un autre onglet (un onglet = un joueur). Une fenêtre privée
ouverte sur le même lien suit la partie en spectateur une fois qu'elle a
commencé.

La documentation interactive de l'API (Swagger) est sur
http://localhost:8000/docs.

## Lancer les tests

```bash
# Depuis backend/
uv run pytest
```

82 tests couvrent :

- **les règles** (`tests/game/`) : déplacement circulaire, salaire, achat, loyer,
  faillite, gagnant, ordre des tours, plus une simulation qui vérifie que les
  parties se terminent ;
- **l'API REST** (`tests/api/test_games.py`) : création, jonction, tour, codes
  d'erreur, absence de jeton dans l'état ;
- **le temps réel** (`tests/api/test_live.py`, `test_hub.py`) : diffusion à
  plusieurs clients, partie inconnue, connexions fermées.

Le frontend n'a pas de tests automatisés (voir « Avec plus de temps »). Il a été
vérifié en jouant des parties complètes dans Chrome.

## Architecture

```
frontend/src                            backend/app
┌─────────────────────────────┐         ┌──────────────────────────────────────┐
│ components/  écrans         │         │ api/       routes REST + WebSocket   │
│ hooks/useGame  WebSocket ───┼── WS ──▶│            schémas, erreurs → HTTP   │
│ api/client     REST ────────┼─ HTTP ─▶├──────────────────────────────────────┤
│ lib/  logique d'affichage   │         │ rooms.py   parties en mémoire,       │
│       pure                  │         │            jetons des joueurs        │
└─────────────────────────────┘         ├──────────────────────────────────────┤
                                        │ game/      règles du jeu, en Python  │
                                        │            pur (sans FastAPI)        │
                                        └──────────────────────────────────────┘
```

- **`backend/app/game/`, le domaine** : toutes les règles du jeu, sans dépendance
  web.
  - `Game` est l'objet central : il détient l'état d'une partie et garantit ses
    règles.
  - Il expose deux actions : `add_player(name)` et `play_turn(player_id, roll)`.
  - Un tour renvoie des événements typés (`Moved`, `RentPaid`, `Bankrupted`…).
  - Le dé est passé en paramètre, ce qui rend les tests déterministes.
- **`backend/app/rooms.py`** : `GameRoom` ajoute à une partie les jetons
  d'accès des joueurs ; `RoomRegistry` garde les parties en mémoire sous un
  code court.
- **`backend/app/api/`, la couche web** : elle reste mince (lire l'entrée,
  appeler le domaine, renvoyer l'état).
  - `LiveHub` envoie l'état complet de la partie à tous les navigateurs
    connectés, après chaque changement.
  - Le dé, le registre et le jeton passent par l'injection de dépendances de
    FastAPI (`Depends`).
- **`frontend/src/`** :
  - `useGame` s'abonne au WebSocket, qui est la seule source de l'état
    affiché ;
  - `lib/` regroupe la logique d'affichage en fonctions pures (position des
    cases sur l'anneau, texte du journal) ;
  - `components/` contient les écrans.

## Design de l'API

### REST

| Méthode | Route | Corps | Réponse |
|---|---|---|---|
| `POST` | `/api/games` | `{max_players, player_name}` | 201 `{player_id, token, game}` (le créateur est le premier joueur) |
| `POST` | `/api/games/{code}/players` | `{player_name}` | 201 `{player_id, token, game}` |
| `GET` | `/api/games/{code}` | — | `game` |
| `POST` | `/api/games/{code}/turns` | — + `Authorization: Bearer <token>` | `{events, game}` |

- Le **dé est tiré par le serveur**, jamais fourni par le client.
- L'identité du joueur vient du **jeton**, jamais d'un id envoyé par le client.
- `game` est l'**état complet** de la partie :
  - le plateau, avec le propriétaire de chaque case ;
  - les joueurs : argent, position, propriétés, éliminé ou non ;
  - le joueur actif, le statut, le gagnant ;
  - le journal des événements, chaque événement marqué par un champ `type`.

  Il ne contient jamais de jeton.

### WebSocket

`WS /ws/games/{code}`, en lecture seule. Le serveur envoie
`{"type": "state", "game": {...}}` à la connexion, puis après chaque jonction et
chaque tour. Les actions passent toujours par REST.

### Erreurs

| Cas | Code |
|---|---|
| Partie inconnue | 404 (WebSocket : fermeture avec le code applicatif 4404) |
| Jeton absent ou invalide | 401 |
| Pas son tour, partie pleine, déjà commencée ou terminée | 409 |
| Entrée invalide (nom vide, 1 ou 5 joueurs…) | 422 |

## Règles : interprétations retenues

L'énoncé laisse certains cas ouverts ; voici les choix faits (détails et
justifications dans [PLAN.md](PLAN.md)).

- **Achat automatique** d'une propriété libre si l'argent suffit (≥ prix) ;
  sinon, rien ne se passe (D1, D2).
- **Faillite** : un joueur qui ne peut pas payer tout le loyer donne ce qui lui
  reste au propriétaire, est éliminé, et ses propriétés redeviennent libres (D3).
- **Salaire** versé en passant ou en s'arrêtant sur le départ, avant l'effet de
  la case d'arrivée (D4, D5).
- **Démarrage** automatique quand la partie est pleine ; ordre de jeu = ordre
  d'arrivée (D7).
- **Un clic = un tour complet** : déplacement, salaire, achat ou loyer,
  faillite, joueur suivant (D9).
- **Équilibrage** : 500 $ au départ, 100 $ de salaire, loyer égal au prix (D24).
  Avec des valeurs plus « réalistes » (1 500 $, 200 $, loyer à 10 % du prix),
  les simulations montraient qu'aucune partie ne se terminait.

## Principaux choix techniques

- **Domaine sans framework** (D19, D21) : les règles se lisent et se testent
  sans FastAPI.
- **État complet poussé par WebSocket** (D10, D35, D39) : le client remplace son
  état au lieu de le reconstruire ; une reconnexion récupère tout d'un coup.
- **Stockage en mémoire, sans verrou** (D11, D30) : routes `async` qui ne
  s'interrompent pas pendant qu'elles modifient une partie, ce qui suffit sur un
  seul processus.
- **Jeton par onglet** (`sessionStorage`, D38) : plusieurs joueurs peuvent jouer
  dans un même navigateur ; recharger la page garde sa place.
- **Pas de routeur ni de bibliothèque d'état côté frontend** (D16, D40) : deux
  écrans seulement.

## Avec plus de temps

- **Plateaux personnalisables** : permettre de personnaliser les cases du
  plateau, sur le modèle des extensions (add-ons) des jeux de table modernes.
  Le plateau est déjà une définition statique séparée de l'état de la partie
  (`Board` dans `app/game/board.py`), ce qui rend ce point accessible.
- **Composant `Square` côté frontend** : extraire de `Board.tsx` tout le contenu
  d'une case (nom, prix, couleur du propriétaire, pions) dans un sous-composant.
  `Board` ne garderait que la grille et le placement des cases.
- **Test de bout en bout automatisé** : un script Playwright qui joue une partie
  complète dans un vrai navigateur (deux onglets joueurs et un spectateur). Il a
  servi à la vérification manuelle mais n'est pas intégré au dépôt ; il
  protégerait le lien entre frontend et backend, aujourd'hui non testé
  automatiquement.
- **Tests frontend** (Vitest) sur les fonctions pures de `src/lib/` et les
  composants.
- **Types TypeScript générés** depuis le schéma OpenAPI de FastAPI, au lieu de
  `src/api/types.ts` écrit à la main.
- **Persistance et passage à l'échelle** : les parties sont en mémoire (perdues
  au redémarrage) et l'absence de verrou suppose un seul processus. Pour
  plusieurs instances : un stockage partagé (Redis, PostgreSQL) et une
  diffusion entre serveurs (Redis pub/sub, par exemple).
- **Déconnexions et abandons** : un joueur qui quitte bloque la partie ;
  ajouter un délai de tour, un abandon explicite ou un remplacement.
- **Messages d'erreur en français** : ceux du backend sont en anglais et
  s'affichent tels quels.
