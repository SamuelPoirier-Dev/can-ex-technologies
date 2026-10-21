# PLAN — Monopoly simplifié multijoueur

Timebox : 2 heures. Backend Python + FastAPI, frontend React + TypeScript.

## Étapes

| # | Étape | Statut |
|---|---|---|
| 1 | Squelette exécutable de bout en bout (FastAPI + Vite/React/TS, `/api/health`) | Fait |
| 2 | Moteur de jeu pur + tests unitaires des règles | Fait |
| 3 | API REST : créer, rejoindre, lire l'état, jouer son tour | Fait |
| 4 | Temps réel : WebSocket par partie, diffusion de l'état | Fait |
| 5 | Frontend jouable : lobby, plateau, joueurs, tour, journal, gagnant | Fait |
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
- **D6 — Plateau et constantes** : plateau fixe codé en dur (16 cases, départ en
  case 0, thème ville de Québec), dé à 6 faces. Montants révisés par D24.
- **D7 — Démarrage** : le créateur choisit la taille (2 à 4) ; la partie démarre
  automatiquement quand elle est pleine ; ordre de jeu = ordre d'arrivée.
- **D8 — Identité** : pas de comptes ; le serveur remet un jeton de joueur à la
  jonction, gardé côté navigateur (`sessionStorage`, voir D38). Seul son détenteur peut jouer son tour.
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
- **D18 — Propriété des cases** : stockée dans `Game.owners` (`{case: joueur}`),
  pas dans `Square`. Le plateau reste statique ; les propriétés d'un joueur se
  déduisent du dictionnaire (une seule source de vérité).
- **D19 — Agrégat `Game`** : les règles sont des méthodes de `Game`
  (`add_player`, `play_turn`), découpées en étapes privées (`_move`,
  `_resolve_square`, `_buy`, `_pay_rent`, `_bankrupt`, `_advance_turn`). Les
  invariants restent au même endroit.
- **D20 — Événements typés** (`app/game/events.py`) : `Moved`, `SalaryCollected`,
  `PropertyBought`, `RentPaid`, `Bankrupted`, `GameWon`. Renvoyés par
  `play_turn` et ajoutés au journal de la partie.
- **D21 — Domaine sans framework** : dataclasses dans `app/game/`, ni FastAPI ni
  Pydantic ; les schémas d'API viendront à l'étape 3.
- **D22 — Erreurs métier** : `GameError` et ses sous-classes, traduites en codes
  HTTP par l'API.
- **D23 — Identifiants de joueurs séquentiels** (`p1`, `p2`…) : déterministes et
  lisibles. Ce ne sont pas des secrets ; l'autorisation passera par un jeton
  séparé (D8, étape 3).
- **D24 — Équilibrage** : 500 $ de départ, 100 $ de salaire, loyer = prix.
  Les simulations montraient qu'avec 1 500 $ / 200 $ / loyer à 10 %, aucune
  partie ne se terminait (le salaire dépasse les loyers). Réglage choisi pour
  qu'une partie de démonstration finisse vite (~20 tours à 2 joueurs, ~50 à 4).
  Ce sont des constantes ajustables ; `tests/game/test_balance.py` garantit
  qu'une partie à 2 joueurs se termine en moins de 200 tours.
- **D25 — `GameRoom` autour de `Game`** (`app/rooms.py`) : associe les jetons aux
  joueurs (les connexions WebSocket sont finalement dans `LiveHub`, voir D33). Le domaine ignore jetons et
  réseau. `RoomRegistry` stocke les salles en mémoire (`{code: GameRoom}`).
- **D26 — Code de partie** : 6 caractères sans 0/O ni 1/I ; sert d'identifiant
  dans l'URL ; accepté sans tenir compte de la casse.
- **D27 — Jeton** : `secrets.token_urlsafe`, envoyé en `Authorization: Bearer`.
  L'identité du joueur est déduite du jeton, jamais d'un id envoyé par le client.
  Le dé est tiré par le serveur, jamais fourni par le client.
- **D28 — Dé injecté par `Depends(get_dice)`** : les tests le remplacent par un dé
  fixe via `dependency_overrides`.
- **D29 — Erreurs → HTTP** (`app/main.py`) : partie inconnue 404, jeton
  absent/invalide 401, autres `GameError` 409 (conflit avec l'état) ; entrées
  invalides 422 via Pydantic.
- **D30 — Concurrence** : routes `async` sans `await` pendant la modification
  d'une partie ; sur un seul processus, pas d'entrelacement, donc pas de verrou.
  À revoir avec plusieurs processus (il faudrait aussi un stockage partagé).
- **D31 — État complet dans chaque réponse** (`game_state` dans
  `app/api/schemas.py`) : plateau avec propriétaires, joueurs, joueur actif,
  statut, gagnant, journal ; chaque événement porte un champ `type`. Jamais de
  jeton. Le même état sera poussé par WebSocket (étape 4).
- **D32 — Fabrique `create_app()`** : chaque test crée une app neuve avec son
  propre registre, donc pas d'état partagé entre tests.
- **D33 — `LiveHub` séparé de `GameRoom`** (`app/api/hub.py`) : registre
  `{code: connexions}` et diffusion. `rooms.py` reste indépendant de FastAPI et le
  hub se teste seul avec de faux WebSockets. La route WebSocket est dans
  `app/api/live.py`.
- **D34 — WebSocket en lecture seule, sans jeton** : l'état ne contient aucun
  secret ; les actions restent en REST avec jeton. Un spectateur peut suivre.
- **D35 — État complet à chaque message** (`{"type": "state", "game": ...}`) :
  le client remplace son état ; une reconnexion reçoit tout d'un coup. L'état est
  envoyé à la connexion, puis après chaque jonction et chaque tour (pas à la
  création : personne n'écoute encore).
- **D36 — Robustesse** : un envoi qui échoue retire la connexion sans faire
  échouer la requête du joueur ; une partie inconnue ferme le WebSocket avec le
  code applicatif 4404.
- **D37 — Dépendances partagées** (`app/api/deps.py`) : registre, hub, dé, jeton.
  `HTTPConnection` sert à la fois aux requêtes HTTP et aux WebSockets. Les tests
  d'API partagent leur client (`tests/api/conftest.py`) et leurs utilitaires
  (`tests/api/helpers.py`).
- **D38 — `sessionStorage` plutôt que `localStorage`** (révise D8) : propre à
  chaque onglet, donc plusieurs joueurs possibles dans un même navigateur (tests
  et démo) ; survit au rechargement. Fermer l'onglet fait perdre sa place.
- **D39 — Le WebSocket est la seule source de l'état affiché** : la réponse REST
  d'un tour ne sert qu'aux erreurs. Même chemin de mise à jour pour tous.
- **D40 — Pas de routeur** : deux écrans (`/` et `/game/CODE`), lus depuis
  `window.location` ; navigation par `history.pushState`.
- **D41 — Plateau en anneau sur une grille 5×5** : le pourtour compte 16 cases ;
  `ringCell` (`src/lib/board.ts`) calcule la position. Départ en bas à droite,
  sens horaire comme au Monopoly. Le centre affiche le dé et le bouton.
- **D42 — Types TypeScript écrits à la main** (`src/api/types.ts`), calqués sur
  les schémas Pydantic. Génération depuis OpenAPI notée pour « plus de temps ».
- **D43 — Reconnexion WebSocket** après 1 s, sauf code 4404 (« Partie
  introuvable »).
- **D44 — Logique d'affichage dans des fonctions pures** (`src/lib/` : position
  des cases, couleurs, texte du journal), séparées des composants.
