"""Lecture des fiches du Cortex (Python standard, aucune dépendance).

Une fiche = un fichier Markdown dans fiches/ avec un en-tête optionnel :

    ---
    titre: Mon titre
    domaine: ecommerce
    tags: [prix, fournisseur]
    resume: Une phrase qui dit ce que la fiche sait.
    cree: 2026-11-07
    maj: 2026-11-07
    toujours: oui        # optionnel : relue avant CHAQUE réponse
    ---
    Contenu… avec des liens [[autre-fiche]] ou [[autre-fiche|texte affiché]].
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_FICHES = RACINE / "fiches"
FICHIER_CONFIG = RACINE / "cortex.json"

LIEN_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")


def slug(texte: str) -> str:
    """'Prix & Marges' -> 'prix-marges'"""
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t.lower()).strip("-")
    return t or "sans-titre"


def sans_accents(texte: str) -> str:
    return unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()


def lire_config() -> dict:
    config = {"nom": "moi"}
    try:
        config.update(json.loads(FICHIER_CONFIG.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        pass
    return config


def _valeur(brut: str):
    brut = brut.strip()
    if brut.startswith("[") and brut.endswith("]"):
        return [v.strip().strip("'\"") for v in brut[1:-1].split(",") if v.strip()]
    return brut.strip("'\"")


def _entete(texte: str) -> tuple[dict, str]:
    if not texte.startswith("---"):
        return {}, texte
    fin = texte.find("\n---", 3)
    if fin == -1:
        return {}, texte
    meta = {}
    for ligne in texte[3:fin].splitlines():
        if ":" in ligne and not ligne.lstrip().startswith("#"):
            cle, _, val = ligne.partition(":")
            meta[cle.strip().lower()] = _valeur(val)
    corps = texte[fin + 4:]
    return meta, corps.lstrip("\n")


def _date(valeur, defaut: str) -> str:
    if isinstance(valeur, str) and re.match(r"^\d{4}-\d{2}-\d{2}", valeur):
        return valeur[:10]
    return defaut


def charger_fiches() -> list[dict]:
    """Renvoie toutes les fiches, avec leurs liens résolus (liste d'ids)."""
    fiches = []
    if not DOSSIER_FICHES.exists():
        return fiches
    for chemin in sorted(DOSSIER_FICHES.rglob("*.md")):
        if any(part.startswith(".") for part in chemin.relative_to(DOSSIER_FICHES).parts):
            continue
        try:
            texte = chemin.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        meta, corps = _entete(texte)
        relatif = chemin.relative_to(DOSSIER_FICHES)
        mtime = _dt.date.fromtimestamp(chemin.stat().st_mtime).isoformat()
        titre = meta.get("titre") or _premier_titre(corps) or chemin.stem.replace("-", " ").capitalize()
        domaine = meta.get("domaine") or (relatif.parts[0] if len(relatif.parts) > 1 else "general")
        tags = meta.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        cree = _date(meta.get("cree"), mtime)
        fiches.append({
            "id": slug(chemin.stem),
            "titre": titre,
            "domaine": slug(domaine),
            "tags": tags,
            "resume": meta.get("resume") or _premiere_phrase(corps),
            "cree": cree,
            "maj": _date(meta.get("maj"), max(cree, mtime)),
            "toujours": str(meta.get("toujours", "")).lower() in {"oui", "true", "yes", "1"},
            "type": meta.get("type", ""),
            "chemin": str(Path("fiches") / relatif).replace(os.sep, "/"),
            "contenu": corps,
            "mots": len(re.findall(r"\w+", corps)),
            "cibles": [m.group(1).strip() for m in LIEN_RE.finditer(corps)],
        })
    _resoudre_liens(fiches)
    return fiches


def _premier_titre(corps: str) -> str:
    m = re.search(r"^#\s+(.+)$", corps, re.M)
    return m.group(1).strip() if m else ""


def _premiere_phrase(corps: str) -> str:
    for ligne in corps.splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith(("#", "---", ">", "-", "*", "|")):
            ligne = LIEN_RE.sub(lambda m: m.group(2) or m.group(1), ligne)
            return (ligne[:157] + "…") if len(ligne) > 160 else ligne
    return ""


def _resoudre_liens(fiches: list[dict]) -> None:
    index = {}
    for f in fiches:
        index.setdefault(f["id"], f["id"])
        index.setdefault(slug(f["titre"]), f["id"])
    for f in fiches:
        liens, manquants = [], []
        for cible in f.pop("cibles"):
            cle = slug(Path(cible).stem if "/" in cible else cible)
            if cle in index and index[cle] != f["id"]:
                if index[cle] not in liens:
                    liens.append(index[cle])
            elif cle not in index:
                manquants.append(cible)
        f["liens"] = liens
        f["manquants"] = manquants


def aretes(fiches: list[dict]) -> list[list[str]]:
    vues, resultat = set(), []
    for f in fiches:
        for cible in f["liens"]:
            cle = tuple(sorted((f["id"], cible)))
            if cle not in vues:
                vues.add(cle)
                resultat.append([f["id"], cible])
    return resultat
