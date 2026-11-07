#!/usr/bin/env python3
"""Hook « UserPromptSubmit » : avant chaque réponse, Claude reçoit
1. les fiches marquées `toujours: oui` (ton profil, tes règles) ;
2. les fiches les plus proches de ta question (mots en commun) ;
3. la liste des titres de toutes les fiches, pour qu'il sache quoi aller lire.

Claude Code envoie la question en JSON sur l'entrée standard ; tout ce que ce
script affiche est ajouté au contexte de Claude. En cas d'erreur il ne dit rien,
pour ne jamais bloquer une conversation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cortex_lib import charger_fiches, sans_accents  # noqa: E402

MAX_FICHES = 5          # fiches complètes injectées par question
MAX_CARACTERES = 9000   # budget total pour le contenu des fiches
MAX_TITRES = 150        # titres listés dans le sommaire

MOTS_VIDES = set("""
avec avoir bien cela cette comme dans des elle elles est etre fait faire faut
leur leurs mais mes moi mon nous pas peux peut plus pour pourquoi quand que quel
quelle quelles quels qui quoi sans ses son sont sur tes toi ton tous tout toute
une vers vos votre veux voila aussi alors encore donc ici the and for with this
that what how comment combien quoi est-ce faire fais fait peux veux dois
""".split())


def mots(texte: str) -> set[str]:
    return {m for m in re.findall(r"[a-z0-9]{3,}", sans_accents(texte)) if m not in MOTS_VIDES}


def score(fiche: dict, question: set[str]) -> float:
    if not question:
        return 0.0
    titre = mots(fiche["titre"]) | mots(" ".join(fiche["tags"]))
    corps = mots(fiche["contenu"])
    s = 3 * len(question & titre) + len(question & corps)
    # correspondances partielles (« fournisseurs » ~ « fournisseur »)
    for q in question - titre:
        if len(q) >= 5 and any(t.startswith(q[:5]) for t in titre):
            s += 1.5
    return s


def main() -> None:
    try:
        entree = json.load(sys.stdin)
    except ValueError:
        entree = {}
    question = mots(entree.get("prompt", ""))
    fiches = charger_fiches()
    if not fiches:
        return
    par_id = {f["id"]: f for f in fiches}

    choisies = [f for f in fiches if f["toujours"]]
    classement = sorted(
        ((score(f, question), f) for f in fiches if not f["toujours"]),
        key=lambda x: x[0], reverse=True,
    )
    pertinentes = [f for s, f in classement if s >= 2][:MAX_FICHES]
    # une fiche très pertinente fait aussi remonter ses voisines directes (titres seulement)
    voisines = []
    for f in pertinentes[:2]:
        for v in f["liens"]:
            if v in par_id and par_id[v] not in pertinentes and par_id[v] not in voisines:
                voisines.append(par_id[v])

    sortie = ["<cortex>", "Fiches de la mémoire de l'utilisateur (dossier fiches/). "
              "Appuie-toi dessus ; si une fiche listée semble utile, lis-la avec Read. "
              "Range ensuite ce qui mérite d'être retenu (voir CLAUDE.md)."]
    budget = MAX_CARACTERES
    for titre_bloc, groupe in (("Toujours en tête", choisies), ("Liées à la question", pertinentes)):
        if not groupe:
            continue
        sortie.append(f"\n## {titre_bloc}")
        for f in groupe:
            contenu = f["contenu"].strip()
            if len(contenu) > budget:
                contenu = contenu[:max(budget, 0)] + "\n[…tronqué, lire le fichier]"
            budget -= len(contenu)
            sortie.append(f"\n### {f['titre']} ({f['chemin']}, maj {f['maj']})\n{contenu}")
            if budget <= 0:
                break
    if voisines:
        sortie.append("\n## Reliées à ces fiches")
        sortie += [f"- {v['titre']} ({v['chemin']}) : {v['resume']}" for v in voisines[:8]]

    sortie.append(f"\n## Sommaire ({len(fiches)} fiches)")
    recentes = sorted(fiches, key=lambda f: f["maj"], reverse=True)[:MAX_TITRES]
    sortie += [f"- [{f['domaine']}] {f['titre']} ({f['chemin']})" for f in recentes]
    if len(fiches) > MAX_TITRES:
        sortie.append(f"- … et {len(fiches) - MAX_TITRES} autres : voir INDEX.md")
    sortie.append("</cortex>")
    print("\n".join(sortie))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # ne jamais bloquer la conversation
        pass
