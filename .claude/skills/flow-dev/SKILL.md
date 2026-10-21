---
name: flow-dev
description: Flux de travail itératif de Samuel — plan par étapes, validation avant exécution, revue avant commit.
disable-model-invocation: true
---

# Flux de travail

## Démarrage
- Résume la demande (INTENT.md, ou fournie dans la conversation). Je la lis en
  parallèle pour qu'on soit sur la même longueur d'onde.
- Avant de planifier, liste les **ambiguïtés** de la demande et propose une
  hypothèse pour chacune. Une fois validées, elles deviennent les premières
  décisions du journal.
- Propose ensuite un plan détaillé, découpé en étapes avec un commit par étape :
  - ordonne les étapes par priorité ;
  - pour un nouveau projet, la première étape est un **squelette exécutable de
    bout en bout** (par exemple, backend et frontend qui démarrent et
    communiquent), sans fonctionnalité.
- Tiens un PLAN.md : les étapes avec leur statut, et un journal des décisions
  numérotées (D1, D2…) avec leur justification.

## Pour chaque étape
1. **Proposition** : détaille le travail et les décisions à prendre. Attends
   mon accord avant d'exécuter.
2. **Exécution**, sans commit :
   - reste dans la portée de l'étape : aucune fonctionnalité hors de la demande sans
     mon accord ;
   - les tests existants sont mis à jour ou déplacés au besoin, et de nouveaux
     tests couvrent le nouveau comportement ;
   - garde la logique métier dans des fonctions faciles à tester, séparées des
     routes et des composants ;
   - vérifie toi-même (tests, exécution réelle) avant de me remettre l'étape ;
   - consigne les nouvelles décisions dans PLAN.md.
3. **Récapitulatif** : ce qui a été fait, les fichiers modifiés, ce qui a changé
   en cours de route, et les commandes de test manuel (en précisant depuis quel
   dossier les lancer).
4. **Revue** : je teste, je commente, je pose des questions. Tu peux contribuer
   à la discussion et proposer des alternatives. On itère jusqu'à ma validation.
5. **Commit** : seulement quand je le demande explicitement.
6. On passe à l'étape suivante.

## Conventions
- Conversation et documents en français ; code, commentaires et messages de
  commit en anglais.
- Explique brièvement les notions techniques utilisées au passage.
- Si la demande ne dit rien à ce sujet, inclure un README.md : lancer le
  projet, lancer les tests, design de l'API, décisions (reprises de PLAN.md) et
  ce qu'on ferait avec plus de temps.
