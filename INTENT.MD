Exercice: Can-Ex Tech <> Monopoly
Exercice de programmation, timeboxé à 2 heures
Objectif
Implémenter un jeu de Monopoly simplifié, sous forme d'application web multijoueur où plusieurs joueurs
s'affrontent chacun depuis leur navigateur, à partir des règles ci-dessous. L'exercice sert de point de départ à une
discussion technique lors de l'entrevue suivante : tu devras présenter ton code, expliquer tes choix et le faire
évoluer avec nous.
Règles du jeu
Se déplacer. À son tour, le joueur actif lance un dé et avance d'autant de cases sur un plateau circulaire fixe
(qui revient au point de départ).
Acheter ou payer. Certaines cases sont des propriétés dotées d'un prix et d'un loyer, les autres sont vides et il
ne s'y passe rien. Quand un joueur arrive sur une propriété qui n'appartient à personne, il l'achète (son argent
diminue, la propriété est enregistrée). Si elle appartient à quelqu'un d'autre, il verse le loyer à ce propriétaire.
S'il la possède déjà, rien ne se passe.
Entrées et sorties d'argent. Tout le monde commence avec une réserve d'argent fixe, et passer par la case
de départ rapporte un salaire. Un joueur qui ne peut pas payer un loyer fait faillite et est éliminé. Le dernier
joueur en lice gagne.
Livrable attendu
Un dépôt Git contenant une application web :
Backend : Python + FastAPI.
Frontend : React + TypeScript.
L'application est multijoueur : un joueur crée une partie de 2 à 4 joueurs, les autres la rejoignent depuis leur
propre navigateur avec un lien et un code de partie.
Chaque joueur voit le plateau, l'argent et les propriétés de chacun, joue son tour quand c'est le sien, et voit la
partie se mettre à jour en direct devant lui (déplacements des autres, transactions, faillites, gagnant).
Un README qui nous permet de lancer l'app
Contraintes et attentes
Timebox : 2 heures. C'est court pour une app fullstack, et c'est voulu. On ne cherche pas un produit fini, on
cherche à voir comment tu structures un problème et où tu choisis d'investir ton temps. Arrête-toi à 2 heures,
remets ce que tu as, et note dans le README ce que tu ferais avec plus de temps.
IA : permise et même encouragée (c'est en bonne partie ce qui rend le timebox réaliste). Par contre, tu es
responsable de chaque ligne remise : lors du débrief, on te demandera d'expliquer et de modifier ton code en
direct.
Remise : le lien vers ton dépôt Git.
Ce qu'on évalue
1. Modélisation et architecture.
2. Qualité et lisibilité du code.
3. Jugement. (Gestion du scope dans le timebox, choix assumés)
Ce qu'on n'évalue pas
L'esthétique de l'interface, la performance, ou le respect des règles officielles du Monopoly au-delà de celles
décrites ici. En cas d'ambiguïté dans les règles, tranche toi-même et documente ta décision.