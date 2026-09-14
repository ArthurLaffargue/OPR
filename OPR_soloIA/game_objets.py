# -*- coding: utf-8 -*-
"""
OPR_reader.game_objects
========================

Reconstruit, a partir des CSV produits par `csv_writer.py` (units.csv /
weapons.csv), des objets Python directement utilisables pour jouer :
statistiques (PV, M, ADV, Q, D, nrb, socle), regles, armes de tir et de
melee.

Ce module ne relit PAS les fichiers .txt d'Army Forge (c'est le role de
`parser.py`) : il part des CSV deja generes, qui sont la "base de
donnees" stable du projet.

Contenu :
    - Rule            : une regle speciale (nom + parametre eventuel)
    - Weapon          : une arme (tir ou melee), avec ses regles
    - Unit            : une unite jouable, avec stats + regles + armes
    - load_army_units : charge units.csv + weapons.csv d'un dossier
                         d'armee en dict {unit_id: Unit}
    - combine_units   : fusionne deux Unit (ex: heros + unite) en une
                         seule Unit "composite", equivalent moderne de
                         l'ancienne fonction `composed_unit`.

Hypothese sur le mouvement (absent des CSV, cf. Objectifs) : toutes les
unites ont par defaut Avance M=6" / Charge-Rush ADV=12", modifie par les
regles core "Fast" (+2"/+4") et "Slow" (-2"/-4") -- cf. les descriptions
dans OPR_reader/rules_data.py. ADV est toujours egal a 2 x M.
"""

import csv
import os
from typing import Dict, List, Optional

from OPR_soloIA.base_objets import Rule, parse_rules_str, rules_to_str, Weapon

# ----------------------------------------------------------------------
# Reglages par defaut
# ----------------------------------------------------------------------

BASE_MOVE = 6          # Avance de base (") si aucune regle ne la modifie
DEFAULT_PV = 1         # PV par defaut si la figurine n'a pas Tough(X)


def _parse_plus_value(text: str) -> int:
    """'3+' -> 3"""
    return int(text.strip().rstrip("+"))


class Unit:
    """Unite jouable, reconstruite a partir d'une ligne de units.csv et
    des lignes de weapons.csv qui lui correspondent (meme unit_id)."""

    def __init__(
        self,
        *,
        army: str,
        unit_id: str,
        name: str,
        nrb: int,
        socle: Optional[float],
        Q: int,
        D: int,
        PV: int,
        M: int,
        ADV: int,
        points: int,
        rules: List[Rule],
        weapons: List[Weapon],
    ):
        self.army = army
        self.unit_id = unit_id
        self.name = name
        self.nrb = nrb           # nombre de figurines
        self.socle = socle       # taille de socle (mm)
        self.Q = Q               # qualite (X+)
        self.D = D               # defense (X+)
        self.PV = PV             # points de vie (Tough(X), sinon 1)
        self.M = M               # mouvement "Avance"
        self.ADV = ADV           # mouvement "Rush"/"Charge"
        self.points = points
        self.rules = rules
        self.weapons = weapons

    # -- armes ------------------------------------------------------
    @property
    def tirs(self) -> List[Weapon]:
        return [w for w in self.weapons if w.is_ranged]

    @property
    def melee(self) -> List[Weapon]:
        return [w for w in self.weapons if w.is_melee]

    # -- regles -------------------------------------------------------
    def has_rule(self, name: str) -> bool:
        return any(r.name == name for r in self.rules)

    def rule_param(self, name: str) -> Optional[str]:
        for r in self.rules:
            if r.name == name:
                return r.param
        return None

    # -- affichage ------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Unit {self.name!r} nrb={self.nrb} PV={self.PV} "
            f"Q={self.Q}+ D={self.D}+ M={self.M}\" ADV={self.ADV}\" "
            f"socle={self.socle} pts={self.points}>"
        )

    def summary(self) -> str:
        lignes = [
            f"{self.name}  [{self.nrb}]  Q{self.Q}+ D{self.D}+  "
            f"PV(Tough)={self.PV}  M={self.M}\" ADV={self.ADV}\"  "
            f"socle={self.socle}mm  {self.points}pts",
            "  Regles : " + rules_to_str(self.rules),
        ]
        if self.melee:
            lignes.append("  Melee  : " + " | ".join(repr(w) for w in self.melee))
        if self.tirs:
            lignes.append("  Tir    : " + " | ".join(repr(w) for w in self.tirs))
        return "\n".join(lignes)

    # -- construction depuis les CSV -----------------------------------
    @classmethod
    def from_csv_rows(cls, unit_row: dict, weapon_rows: List[dict]) -> "Unit":
        rules = parse_rules_str(unit_row.get("rules_all", ""))
        weapons = [Weapon.from_csv_row(w) for w in weapon_rows]

        # PV = Tough(X), sinon 1 par defaut
        tough = next((r for r in rules if r.name == "Tough"), None)
        PV = tough.param_int if (tough is not None and tough.param_int is not None) else DEFAULT_PV

        # Mouvement : base 6", modifie par Fast (+2/+4) et Slow (-2/-4).
        # ADV = 2 x M dans tous les cas (voir docstring du module).
        M = BASE_MOVE
        if any(r.name == "Fast" for r in rules):
            M += 2
        if any(r.name == "Slow" for r in rules):
            M -= 2
        ADV = M * 2

        socle_raw = (unit_row.get("base_size_mm") or "").strip()
        socle = float(socle_raw) if socle_raw else None

        return cls(
            army=unit_row["army"],
            unit_id=unit_row["unit_id"],
            name=unit_row["unit_name"],
            nrb=int(unit_row["size"]),
            socle=socle,
            Q=_parse_plus_value(unit_row["quality"]),
            D=_parse_plus_value(unit_row["defense"]),
            PV=PV,
            M=M,
            ADV=ADV,
            points=int(unit_row["points"]),
            rules=rules,
            weapons=weapons,
        )


# ----------------------------------------------------------------------
# Chargement d'une armee complete depuis army_lists/<Armee>/
# ----------------------------------------------------------------------

def load_army_units(army_dir: str) -> Dict[str, Unit]:
    """Lit units.csv + weapons.csv dans `army_dir` et retourne
    {unit_id: Unit}."""
    units_csv = os.path.join(army_dir, "units.csv")
    weapons_csv = os.path.join(army_dir, "weapons.csv")

    weapons_by_unit: Dict[str, List[dict]] = {}
    with open(weapons_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            weapons_by_unit.setdefault(row["unit_id"], []).append(row)

    units: Dict[str, Unit] = {}
    with open(units_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            uid = row["unit_id"]
            units[uid] = Unit.from_csv_rows(row, weapons_by_unit.get(uid, []))

    return units


# ----------------------------------------------------------------------
# Fusion de deux unites (ex: heros rejoignant une unite)
# ----------------------------------------------------------------------

def combine_units(unit1: Unit, unit2: Unit, name: str) -> Unit:
    """Equivalent moderne de l'ancienne fonction `composed_unit` :
    fusionne deux Unit (typiquement un heros + une unite de troupe) en
    une seule Unit "composite".

    Regles de fusion (identiques a l'ancien code) :
        - nrb   : somme des figurines
        - PV    : le plus petit des deux (le maillon le plus faible)
        - M/ADV : le plus lent des deux
        - Q/D   : le pire des deux (le plus grand X dans "X+")
        - socle : moyenne ponderee par le nombre de figurines
        - armes : simple reunion des listes de tir / melee
        - regles: intersection des deux jeux de regles, PLUS, pour
          toute regle en "...Aura" presente chez l'un des deux membres,
          l'ajout de la regle sans le mot "Aura" (elle s'applique
          desormais a l'unite entiere).
    """
    nrb = unit1.nrb + unit2.nrb
    PV = min(unit1.PV, unit2.PV)
    M = min(unit1.M, unit2.M)
    ADV = min(unit1.ADV, unit2.ADV)
    Q = max(unit1.Q, unit2.Q)
    D = max(unit1.D, unit2.D)

    weapons = list(unit1.weapons) + list(unit2.weapons)

    if unit1.socle is not None and unit2.socle is not None:
        socle = (unit1.socle * unit1.nrb + unit2.socle * unit2.nrb) / nrb
    else:
        socle = unit1.socle if unit1.socle is not None else unit2.socle
        if socle is None : socle = 32.0

    rules1, rules2 = set(unit1.rules), set(unit2.rules)
    union_rules = rules1 | rules2
    rules = list(rules1 & rules2)

    for r in union_rules:
        if r.is_aura:
            nom_sans_aura = r.name.replace("Aura", "").strip()
            if nom_sans_aura:
                nouvelle_regle = Rule(nom_sans_aura, r.param)
                if nouvelle_regle not in rules:
                    rules.append(nouvelle_regle)

    return Unit(
        army=unit1.army,
        unit_id=f"{unit1.unit_id}+{unit2.unit_id}",
        name=name,
        nrb=nrb,
        socle=socle,
        Q=Q,
        D=D,
        PV=PV,
        M=M,
        ADV=ADV,
        points=unit1.points + unit2.points,
        rules=rules,
        weapons=weapons,
    )


# ----------------------------------------------------------------------
# Petit auto-test manuel (python -m OPR_reader.game_objects)
# ----------------------------------------------------------------------

if __name__ == "__main__":

    army_dir = "../army_lists/Orcs/"
    units = load_army_units(army_dir)

    print(f"{len(units)} unites chargees depuis {army_dir}\n")

    hero = units["orcs_chef_de_guerre"]
    troups = units["orcs_archers_orcs"]

    print(hero.summary())
    print()
    print(troups.summary())
    print()

    combo = combine_units(hero, troups, f"{hero.name} + {troups.name}")
    print(combo.summary())

    print(hero.melee)