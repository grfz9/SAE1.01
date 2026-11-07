#!/usr/bin/env python3
"""Reconstruit la carte (carte.html) et l'index (INDEX.md) à partir des fiches.

    python3 outils/construire.py              # carte.html + INDEX.md
    python3 outils/construire.py --ouvrir     # … puis ouvre la carte
    python3 outils/construire.py --demo 300   # carte-demo.html avec 300 fausses fiches
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import random
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cortex_lib import RACINE, aretes, charger_fiches, lire_config  # noqa: E402

MODELE = Path(__file__).resolve().parent / "carte_modele.html"


def ecrire_index(fiches: list[dict]) -> Path:
    par_domaine: dict[str, list[dict]] = {}
    for f in fiches:
        par_domaine.setdefault(f["domaine"], []).append(f)
    lignes = [
        "# Index du Cortex",
        "",
        "> Généré automatiquement par `outils/construire.py`. Ne pas modifier à la main.",
        "",
        f"{len(fiches)} fiches · {len(aretes(fiches))} liens · mis à jour le {_dt.date.today().isoformat()}",
        "",
    ]
    for domaine in sorted(par_domaine):
        lignes.append(f"## {domaine} ({len(par_domaine[domaine])})")
        lignes.append("")
        for f in sorted(par_domaine[domaine], key=lambda x: (x["type"] != "hub", x["titre"].lower())):
            resume = f" : {f['resume']}" if f["resume"] else ""
            lignes.append(f"- [{f['titre']}]({f['chemin']}){resume}")
        lignes.append("")
    manquants = [(f["titre"], m) for f in fiches for m in f["manquants"]]
    if manquants:
        lignes += ["## Liens vers des fiches qui n'existent pas encore", ""]
        lignes += [f"- {titre} → [[{m}]]" for titre, m in manquants]
        lignes.append("")
    chemin = RACINE / "INDEX.md"
    chemin.write_text("\n".join(lignes), encoding="utf-8")
    return chemin


def fausses_fiches(n: int) -> list[dict]:
    """Génère un faux cerveau pour voir à quoi ressemble une carte bien remplie."""
    rnd = random.Random(7)
    domaines = {
        "ecommerce": ["Fournisseur", "Fiche produit", "Marge", "Retour client", "Pub Meta", "Panier moyen", "Stock"],
        "reseaux-sociaux": ["Hook vidéo", "Calendrier posts", "Script Reel", "Analyse TikTok", "Bio Instagram"],
        "projets": ["Lancement", "Roadmap", "Réunion", "Tâche", "Décision"],
        "idees": ["Idée", "Concept", "Piste", "Inspiration"],
        "apprentissage": ["Cours", "Livre", "Notion clé", "Méthode"],
        "moi": ["Objectif", "Habitude", "Préférence", "Contact"],
    }
    noms = list(domaines)
    poids = [0.32, 0.22, 0.16, 0.12, 0.1, 0.08]
    debut = _dt.date.today() - _dt.timedelta(days=130)
    fiches = []
    for i in range(n):
        d = rnd.choices(noms, poids)[0]
        jour = debut + _dt.timedelta(days=int(130 * (i / max(n - 1, 1)) ** 0.8))
        titre = f"{rnd.choice(domaines[d])} {i + 1}"
        fiches.append({
            "id": f"f{i}", "titre": titre, "domaine": d, "tags": [], "type": "",
            "resume": "Fiche de démonstration.", "cree": jour.isoformat(), "maj": jour.isoformat(),
            "chemin": "", "mots": rnd.randint(40, 900), "toujours": False, "manquants": [],
            "contenu": f"# {titre}\n\nFiche de démonstration générée pour l'aperçu.", "liens": [],
        })
    for i, f in enumerate(fiches):
        if i == 0:
            continue
        meme = [g for g in fiches[:i] if g["domaine"] == f["domaine"]]
        for _ in range(rnd.choice([1, 1, 2, 2, 3])):
            pool = meme if (meme and rnd.random() < 0.8) else fiches[:i]
            cible = rnd.choice(pool[-25:] if rnd.random() < 0.5 else pool)["id"]
            if cible not in f["liens"]:
                f["liens"].append(cible)
    return fiches


def ecrire_carte(fiches: list[dict], sortie: Path, nom: str) -> Path:
    donnees = {
        "nom": nom,
        "genere": _dt.datetime.now().isoformat(timespec="minutes"),
        "fiches": [{k: v for k, v in f.items() if k != "cibles"} for f in fiches],
        "liens": aretes(fiches),
    }
    js = json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/")
    html = MODELE.read_text(encoding="utf-8").replace("/*__DONNEES__*/null", js, 1)
    sortie.write_text(html, encoding="utf-8")
    return sortie


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ouvrir", action="store_true", help="ouvre la carte dans le navigateur")
    p.add_argument("--silencieux", action="store_true", help="n'affiche rien (utilisé par le hook)")
    p.add_argument("--demo", type=int, metavar="N", help="génère carte-demo.html avec N fausses fiches")
    args = p.parse_args()
    config = lire_config()

    if args.demo:
        sortie = ecrire_carte(fausses_fiches(args.demo), RACINE / "carte-demo.html", config.get("nom", "moi"))
    else:
        fiches = charger_fiches()
        ecrire_index(fiches)
        sortie = ecrire_carte(fiches, RACINE / "carte.html", config.get("nom", "moi"))
        if not args.silencieux:
            print(f"✓ {len(fiches)} fiches, {len(aretes(fiches))} liens → {sortie.name} + INDEX.md")
            manquants = sum(len(f["manquants"]) for f in fiches)
            if manquants:
                print(f"  ⚠ {manquants} lien(s) vers des fiches inexistantes (voir INDEX.md)")
    if args.ouvrir:
        webbrowser.open(sortie.as_uri())


if __name__ == "__main__":
    main()
