# 🧠 Cortex : ton second cerveau pour Claude

Des **fiches reliées entre elles comme des neurones**. Claude y range ce qui compte
et **les relit avant chaque réponse**. Tout reste sur ton ordinateur, en fichiers Markdown.
Gratuit, sans abonnement, sans dépendance à installer.

## Ce qu'il fait

| | |
|---|---|
| 📥 **Il retient** | Claude range tout seul dans des fiches tes décisions, prix, clients, préférences et idées (règles dans `CLAUDE.md`). |
| 🔁 **Il relit** | Avant chaque message, un hook injecte tes fiches « toujours relues », les fiches proches de ta question et le sommaire de tout le cerveau. |
| 🕸️ **Il relie** | Chaque fiche pointe vers d'autres avec `[[liens]]`. `/relier` ajoute les liens qui manquent. |
| 🗺️ **Il se montre** | `carte.html` affiche ton cerveau en graphe : clique sur un point pour lire la fiche et voir à quoi elle est reliée. On y trouve aussi une recherche, une frise du temps, des stats, un score de vitalité et un export PNG. |

## Installation (5 minutes)

Il te faut **Claude Code** (sur ordinateur) et **Python 3**. Sur Mac, Python est souvent déjà installé.
Pour vérifier : tape `python3 --version` dans le Terminal.

1. **Récupère le dossier `cortex/`**. Sur GitHub, clique sur *Code → Download ZIP*, puis dézippe
   et place le dossier `cortex` où tu veux, par exemple dans `Documents`.
2. **Mets ton prénom** dans `cortex.json` :
   ```json
   { "nom": "Sam" }
   ```
3. **Lance Claude dans le dossier** :
   ```bash
   cd ~/Documents/cortex
   claude
   ```
   Au premier lancement, Claude Code demande si tu fais confiance au dossier : réponds oui
   (c'est ce qui active les hooks de `.claude/settings.json`).
4. **Remplis ton profil**. Dis à Claude : *« Pose-moi des questions pour remplir mes fiches Moi et Objectifs. »*
5. **Ouvre ta carte** : tape `/carte`, ou double-clique sur `carte.html`.

> **Windows** : si `python3` n'existe pas, remplace `python3` par `python` dans `.claude/settings.json`.

## Au quotidien

Parle normalement à Claude. À la fin de chaque réponse, il indique ce qu'il a rangé
(`🧠 Rangé : …`) et la carte se met à jour toute seule.

| Commande | Effet |
|---|---|
| `/fiche <texte>` | Range une info précise (crée ou complète la bonne fiche) |
| `/ranger` | Relit toute la conversation et range ce qui compte |
| `/relier` | Trouve et ajoute les liens manquants entre les fiches |
| `/bilan` | Fait le point : orphelines, doublons, infos peut-être obsolètes |
| `/carte` | Reconstruit et ouvre la carte |

Tu peux aussi écrire ou modifier des fiches toi-même, dans n'importe quel éditeur.
Les fiches sont compatibles avec **Obsidian** : ouvre le dossier `fiches/` comme coffre.

## Comment c'est rangé

```
cortex/
├── CLAUDE.md              ← les règles que Claude suit (relire, ranger, relier)
├── cortex.json            ← ton prénom
├── fiches/                ← TON CERVEAU : un dossier par domaine, une fiche .md par idée
│   ├── moi/  ecommerce/  reseaux-sociaux/  projets/  idees/  apprentissage/  cortex/
├── INDEX.md               ← sommaire généré automatiquement
├── carte.html             ← la carte interactive, générée automatiquement
├── .claude/
│   ├── settings.json      ← hooks : relire avant chaque réponse, reconstruire la carte après
│   └── commands/          ← /fiche, /ranger, /relier, /bilan, /carte
└── outils/
    ├── contexte.py        ← choisit les fiches à faire relire à Claude
    ├── construire.py      ← génère carte.html et INDEX.md
    ├── cortex_lib.py      ← lecture des fiches
    └── carte_modele.html  ← le design de la carte
```

**Une fiche** ressemble à ça :

```markdown
---
titre: Fournisseur coques iPhone
domaine: ecommerce
tags: [fournisseur, coques]
resume: Mon fournisseur principal de coques, ses prix et délais.
cree: 2026-11-07
maj: 2026-11-07
---
# Fournisseur coques iPhone

Prix unitaire 1,20 € à partir de 500 pièces, délai 9 jours.

Lié à : [[ecommerce]], [[ma-boutique]], [[marge-cible]]
```

Ajoute `toujours: oui` dans l'en-tête d'une fiche pour qu'elle soit relue avant **chaque** réponse
(c'est le cas de *Moi* et *Style de réponse*).

## Voir une carte bien remplie

```bash
python3 outils/construire.py --demo 300   # crée carte-demo.html avec 300 fausses fiches
```

## Confidentialité

Tout est local : les fiches restent sur ton ordinateur. Seules les fiches utiles à ta question
sont envoyées à Claude, au même titre que ton message. Ne mets jamais de mot de passe ni de
code bancaire dans une fiche.
