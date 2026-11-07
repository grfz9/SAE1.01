---
description: Trouve et ajoute les liens qui manquent entre les fiches
argument-hint: (optionnel) un domaine ou une fiche
---
Objectif : densifier le graphe du Cortex. Cible : $ARGUMENTS (si rien n'est précisé : toutes les fiches).

1. Lance `python3 outils/construire.py` puis lis `INDEX.md`.
2. Pour chaque fiche orpheline ou peu reliée, lis-la et cherche (Grep sur les mots clés)
   les fiches qui parlent du même sujet, du même client, du même produit, etc.
3. Ajoute les liens `[[...]]` pertinents dans les deux sens, en fin de fiche, ligne « Lié à : ».
   N'invente pas de lien artificiel : seulement s'il y a un vrai rapport.
4. Pour chaque lien cassé listé dans INDEX.md : crée la fiche manquante si tu as de quoi la remplir,
   sinon corrige le lien vers la bonne fiche.
5. Relance `python3 outils/construire.py` et résume ce que tu as relié.
