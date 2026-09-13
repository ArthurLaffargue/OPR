# -*- coding: utf-8 -*-
"""
OPR_reader.parser
==================

Lit un fichier d'export Army Forge (.txt) pour une armée AoF (One Page
Rules) et le transforme en structures de données Python propres :
liste d'unités, avec pour chacune ses caractéristiques, ses règles
spéciales (classées "core" / "armée") et ses armes (elles aussi avec
leurs propres règles classées).

Ce module ne fait QUE lire/structurer les données. L'écriture des CSV
est faite dans `csv_writer.py`.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .rules_data import CORE_RULES


# ----------------------------------------------------------------------
# Utilitaires bas niveau
# ----------------------------------------------------------------------

def split_top_level(text: str, sep: str = ",") -> List[str]:
    """
    Découpe `text` sur le séparateur `sep`, mais uniquement quand celui-ci
    n'est pas à l'intérieur d'une parenthèse.

    Exemple :
        "Dual Heavy Hand Weapons (A8, AP(2)), Rending Claws (A3, Rending)"
        -> ["Dual Heavy Hand Weapons (A8, AP(2))", "Rending Claws (A3, Rending)"]
    """
    parts = []
    depth = 0
    current = []
    for ch in text:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == sep and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return [p for p in parts if p]


NX_PREFIX_RE = re.compile(r"^(\d+)x\s+(.*)$")


def strip_count_prefix(token: str):
    """
    Sépare un éventuel préfixe "Nx " (ex: "5x Fearless") du reste du texte.
    Retourne (count_or_None, reste_du_texte).
    """
    m = NX_PREFIX_RE.match(token.strip())
    if m:
        return int(m.group(1)), m.group(2).strip()
    return None, token.strip()


RULE_WITH_PARAM_RE = re.compile(r"^([A-Za-zÀ-ÿ&' \-]+?)\((.*)\)$")


def classify_rule_token(token: str):
    """
    Analyse un token de règle spéciale du type "AP(2)", "Tough(12)",
    "Fearless", "Warden Boost Aura" (avec ou sans préfixe "Nx ").

    Retourne un dict :
        {
            "raw": texte original,
            "applies_to_count": N ou None,
            "name": nom de base (ex: "AP", "Tough", "Warden"),
            "param": paramètre X ou None,
            "source": "core" ou "army_specific",
        }
    """
    applies_to_count, rest = strip_count_prefix(token)
    m = RULE_WITH_PARAM_RE.match(rest)
    if m:
        name = m.group(1).strip()
        param = m.group(2).strip()
    else:
        name = rest.strip()
        param = None

    source = "core" if name in CORE_RULES else "army_specific"

    return {
        "raw": token.strip(),
        "applies_to_count": applies_to_count,
        "name": name,
        "param": param,
        "source": source,
    }


ATTACK_RE = re.compile(r"^A(\d+)$")
RANGE_RE = re.compile(r'^(\d+)"$')


def parse_weapon_token(token: str):
    """
    Analyse un token d'arme complet, ex :
        "5x Heavy Halberd (A1, AP(1), Rending)"
        "Snatching Hook (12\", A3, AP(1), Reliable, Takedown)"

    Retourne un dict avec nom, nombre de porteurs, portée, attaques,
    et liste des règles (classées core / armée).
    """
    count, rest = strip_count_prefix(token)
    if count is None : count = 1

    # Sépare "Nom" et "(contenu)" -- le contenu peut lui-même contenir
    # des parenthèses imbriquées (ex: AP(2)), donc on prend tout ce qui
    # se trouve entre la 1ere "(" et la derniere ")".
    first_paren = rest.find("(")
    if first_paren == -1 or not rest.endswith(")"):
        # Arme sans stats entre parentheses (cas degrade, ne devrait pas arriver)
        return {
            "raw": token.strip(),
            "wielders": count,
            "name": rest.strip(),
            "range": None,
            "attacks": None,
            "rules": [],
        }

    name = rest[:first_paren].strip()
    content = rest[first_paren + 1:-1]  # enleve la 1ere "(" et la derniere ")"

    stats = split_top_level(content, ",")

    range_ = None
    attacks = None
    rules = []
    for stat in stats:
        stat = stat.strip()
        m_range = RANGE_RE.match(stat)
        m_atk = ATTACK_RE.match(stat)
        if m_range:
            range_ = int(m_range.group(1))
        elif m_atk:
            attacks = int(m_atk.group(1))
        else:
            rules.append(classify_rule_token(stat))

    return {
        "raw": token.strip(),
        "wielders": count,  # None => 1 seule occurrence
        "name": name,
        "range": range_,
        "attacks": attacks,
        "rules": rules,
    }


# ----------------------------------------------------------------------
# Structures de donnees
# ----------------------------------------------------------------------

@dataclass
class Weapon:
    unit_id: str
    name: str
    wielders: Optional[int]
    range: Optional[int]
    attacks: Optional[int]
    rules: List[dict] = field(default_factory=list)
    raw: str = ""


@dataclass
class Unit:
    army: str
    unit_id: str
    name: str
    size: int
    quality: int
    defense: int
    points: int
    rules: List[dict] = field(default_factory=list)
    weapons: List[Weapon] = field(default_factory=list)
    raw_rules_text: str = ""
    raw_weapons_text: str = ""


@dataclass
class ArmyList:
    faction_code: str
    army_name: str
    version: str
    total_points: int
    unit_count: int
    units: List[Unit] = field(default_factory=list)


# ----------------------------------------------------------------------
# Parsing du fichier
# ----------------------------------------------------------------------

HEADER_RE = re.compile(
    r"^\+\+\s*(?P<faction_code>.+?)\s*-\s*(?P<army_name>.+?)\s*"
    r"\(v(?P<version>[\d.]+)\)\s*\[AOF\s*(?P<points>\d+)pts\]\s*"
    r"\[(?P<unit_count>\d+)\s*Units\]\s*\+\+$"
)

STAT_LINE_RE = re.compile(
    r"^(?P<name>.+?)\s*\[(?P<size>\d+)\]\s*"
    r"Q(?P<quality>\d+)\+\s*D(?P<defense>\d+)\+\s*\|\s*"
    r"(?P<points>\d+)pts\s*\|\s*(?P<rules>.*)$"
)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[àâä]", "a", text)
    text = re.sub(r"[éèêë]", "e", text)
    text = re.sub(r"[îï]", "i", text)
    text = re.sub(r"[ôö]", "o", text)
    text = re.sub(r"[ùûü]", "u", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def parse_army_file(filepath: str) -> ArmyList:
    with open(filepath, encoding="utf-8") as f:
        raw_lines = [line.rstrip("\n") for line in f]

    # Isole la ligne d'entete et le reste
    header_line = next(l for l in raw_lines if l.strip().startswith("++"))
    m = HEADER_RE.match(header_line.strip())
    if not m:
        raise ValueError(f"Ligne d'entete non reconnue : {header_line!r}")

    army = ArmyList(
        faction_code=m.group("faction_code").strip(),
        army_name=m.group("army_name").strip(),
        version=m.group("version").strip(),
        total_points=int(m.group("points")),
        unit_count=int(m.group("unit_count")),
    )

    # Regroupe les lignes restantes en blocs separes par des lignes vides
    body = raw_lines[raw_lines.index(header_line) + 1:]
    blocks = []
    current = []
    for line in body:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    used_ids = set()
    for block in blocks:
        if len(block) < 2:
            continue  # bloc incomplet, on ignore
        stat_line, weapon_line = block[0], block[1]

        m_stat = STAT_LINE_RE.match(stat_line.strip())
        if not m_stat:
            raise ValueError(f"Ligne d'unite non reconnue : {stat_line!r}")

        unit_name = m_stat.group("name").strip()

        # unit_id STABLE base sur le nom (et non sur la position dans le
        # fichier), pour pouvoir faire une jointure fiable avec une
        # version precedente du CSV (cf. base_size_mm) meme si des unites
        # sont ajoutees/supprimees/reordonnees entre deux exports.
        base_id = f"{slugify(army.army_name)}_{slugify(unit_name)}"
        unit_id = base_id
        suffix = 2
        while unit_id in used_ids:
            # deux unites du meme nom dans la meme armee (rare) -> on
            # differencie par un suffixe pour garder des ids uniques
            unit_id = f"{base_id}_{suffix}"
            suffix += 1
        used_ids.add(unit_id)

        unit = Unit(
            army=army.army_name,
            unit_id=unit_id,
            name=unit_name,
            size=int(m_stat.group("size")),
            quality=int(m_stat.group("quality")),
            defense=int(m_stat.group("defense")),
            points=int(m_stat.group("points")),
            raw_rules_text=m_stat.group("rules").strip(),
            raw_weapons_text=weapon_line.strip(),
        )

        # Regles de l'unite
        for token in split_top_level(unit.raw_rules_text, ","):
            unit.rules.append(classify_rule_token(token))

        # Armes de l'unite
        for token in split_top_level(unit.raw_weapons_text, ","):
            w = parse_weapon_token(token)
            unit.weapons.append(
                Weapon(
                    unit_id=unit.unit_id,
                    name=w["name"],
                    wielders=w["wielders"],
                    range=w["range"],
                    attacks=w["attacks"],
                    rules=w["rules"],
                    raw=w["raw"],
                )
            )

        army.units.append(unit)

    return army
