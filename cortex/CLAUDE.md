# Cortex : ta mémoire

Ce dossier est la mémoire longue de l'utilisateur. Chaque fichier de `fiches/` est une
**fiche** : une seule idée, reliée aux autres par des liens `[[...]]`. Ensemble, elles
forment un graphe que l'on voit dans `carte.html`.

## Avant de répondre

- Un bloc `<cortex>` est ajouté automatiquement à chaque message : il contient les fiches
  « toujours relues », celles qui ressemblent à la question, et le sommaire de toutes les fiches.
  **Appuie-toi dessus en priorité** : ce que disent les fiches passe avant tes suppositions.
- Si un titre du sommaire semble utile mais que la fiche n'a pas été injectée, lis-la (Read).
  Suis aussi ses liens `[[...]]` quand c'est pertinent. En cas de doute, cherche dans `fiches/` (Grep).
- Quand ta réponse s'appuie sur une fiche, cite-la brièvement, par exemple « (d'après *Prix de vente*) ».
- Si une fiche contredit ce que l'utilisateur dit maintenant, signale-le et propose de la mettre à jour.

## Après avoir répondu : ranger

Range sans qu'on te le demande tout ce qui servira plus tard :
une décision, un chiffre, un prix, un client ou un fournisseur, une préférence,
une règle de travail, une leçon tirée d'une erreur, une idée de projet.
Ne range pas les échanges banals, et **jamais de secret** (mot de passe, code de carte, clé API).

1. Cherche d'abord s'il existe déjà une fiche sur ce sujet. Si oui, **complète-la**
   (et mets `maj:` à la date du jour) plutôt que d'en créer une nouvelle.
2. Sinon, crée `fiches/<domaine>/<titre-en-minuscules-avec-tirets>.md` avec ce modèle :

```markdown
---
titre: Titre court et clair
domaine: ecommerce
tags: [mot-cle, autre]
resume: Une phrase qui dit ce que la fiche sait.
cree: AAAA-MM-JJ
maj: AAAA-MM-JJ
---
# Titre court et clair

Le contenu, en phrases simples. Les faits d'abord, la source ou la date si utile.

Lié à : [[nom-du-domaine]], [[autre-fiche]]
```

3. **Chaque fiche a au moins un lien** : vers la fiche du domaine (par exemple `[[ecommerce]]`)
   et vers toute fiche qui parle d'un sujet proche. Un lien vers une fiche qui n'existe pas
   encore est permis : il apparaîtra en orange sur la carte comme « fiche à créer ».
4. Une fiche = une idée. Si une fiche dépasse ~400 mots, découpe-la et relie les morceaux.
5. Termine ta réponse par une ligne discrète du type : `🧠 Rangé : Prix de vente (mise à jour), Fournisseur Alibaba (nouvelle)`.

La carte et `INDEX.md` sont reconstruits automatiquement à la fin de chaque réponse
(hook `Stop`). Pour le faire à la main : `python3 outils/construire.py`.

## Domaines

Un domaine = un sous-dossier de `fiches/` + une fiche « hub » du même nom (`type: hub`).
Domaines existants : `moi`, `ecommerce`, `reseaux-sociaux`, `projets`, `idees`, `apprentissage`, `cortex`.
Pour en ajouter un, crée le dossier et sa fiche hub, puis relie le hub à [[moi]].

## Fiches spéciales

- `toujours: oui` dans l'en-tête : la fiche est injectée avant **chaque** réponse
  (profil, règles de style). À garder courtes : il y en a peu.
- `type: hub` : fiche d'entrée d'un domaine, affichée avec un contour blanc sur la carte.

## Commandes

`/fiche`, `/ranger`, `/relier`, `/bilan`, `/carte` (voir `.claude/commands/`).
