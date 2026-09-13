# -*- coding: utf-8 -*-
"""
OPR_reader.csv_writer
======================

Ecrit les structures produites par `parser.py` sous forme de fichiers
CSV, utilisables comme mini base de donnees par le reste du projet
(OPR_soloIA, interface graphique, etc).

Pour chaque armee, on genere 2 fichiers dans army_lists/<NomArmee>/ :

    units.csv    -> 1 ligne par unite (stats + liste de regles + base_size_mm)
    weapons.csv  -> 1 ligne par arme (rattachee a une unite)

`units.csv` contient une colonne `base_size_mm` renseignee MANUELLEMENT
par l'utilisateur (taille de socle en mm). Comme cette information
n'existe pas dans les fichiers Army Forge, elle est preservee d'une
regeneration a l'autre : avant de reecrire le fichier, on relit
l'ancienne version (si elle existe) et on recupere la valeur
`base_size_mm` de chaque unite par son `unit_id`. Les unites qui
n'existent plus dans le fichier .txt courant disparaissent simplement
du nouveau fichier (elles ne sont pas reportees).

La documentation des regles specifiques a l'armee (auparavant
special_rules.csv) est desormais geree par `army_rules_sync.py`, sous
forme d'un fichier .py (`army_rules.py`), pas d'un CSV.
"""

import csv
import os

from .parser import ArmyList

RULES_SEP = ";"

custom_prop = [("base_size_mm", ""),
               ("max_selection", 1),
               ("selectable_options", ""),]
custom_prop_default_dict = {prop : value for prop, value in custom_prop}
def _rules_to_str(rules) -> str:
    """Represente une liste de regles classifiees sous forme de texte
    lisible et re-parsable, ex: 'Fearless;Hero;Tough(12);Warden'."""
    parts = []
    for r in rules:
        if r["param"] is not None:
            parts.append(f"{r['name']}({r['param']})")
        else:
            parts.append(r["name"])
    return RULES_SEP.join(parts)


def _load_existing_custom_properties(units_csv_path: str) -> dict:
    """Relit un units.csv precedent (s'il existe) et retourne
    {unit_id: base_size_mm} pour pouvoir reporter cette info
    "utilisateur" lors de la regeneration."""
    if not os.path.exists(units_csv_path):
        return {}
    result = {}

    with open(units_csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            uid = row.get("unit_id")
            if uid:
                result[uid] = {prop : row.get(prop, "")
                                  for prop, default in custom_prop}

    return result


def write_units_csv(army: ArmyList, out_path: str):
    existing_custom_properties = _load_existing_custom_properties(out_path)

    fieldnames = [
        "army", "unit_id", "unit_name", ]
    fieldnames += list(custom_prop_default_dict.keys())
    fieldnames += ["size", "quality", "defense", "points",
        "rules_all", "rules_core", "rules_army_specific", "weapon_names",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for u in army.units:
            core_rules = [r for r in u.rules if r["source"] == "core"]
            army_rules = [r for r in u.rules if r["source"] == "army_specific"]
            row_dict = {
                "army": u.army,
                "unit_id": u.unit_id,
                "unit_name": u.name,
                "size": u.size,
                "quality": f"{u.quality}+",
                "defense": f"{u.defense}+",
                "points": u.points,
                "rules_all": _rules_to_str(u.rules),
                "rules_core": _rules_to_str(core_rules),
                "rules_army_specific": _rules_to_str(army_rules),
                "weapon_names": RULES_SEP.join(w.name for w in u.weapons),
            }

            row_dict.update(existing_custom_properties.get(u.unit_id, custom_prop_default_dict))
            writer.writerow(row_dict)


def write_weapons_csv(army: ArmyList, out_path: str):
    fieldnames = [
        "army", "unit_id", "unit_name", "weapon_name", "wielders",
        "range_in", "attacks", "rules_all", "rules_core", "rules_army_specific",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for u in army.units:
            for w in u.weapons:
                core_rules = [r for r in w.rules if r["source"] == "core"]
                army_rules = [r for r in w.rules if r["source"] == "army_specific"]
                writer.writerow({
                    "army": u.army,
                    "unit_id": u.unit_id,
                    "unit_name": u.name,
                    "weapon_name": w.name,
                    # None => arme portee par l'ensemble des figurines restantes
                    "wielders": w.wielders if w.wielders is not None else "",
                    "range_in": w.range if w.range is not None else "",
                    "attacks": w.attacks if w.attacks is not None else "",
                    "rules_all": _rules_to_str(w.rules),
                    "rules_core": _rules_to_str(core_rules),
                    "rules_army_specific": _rules_to_str(army_rules),
                })


def write_army_csvs(army: ArmyList, base_output_dir: str) -> str:
    """Cree/actualise army_lists/<NomArmee>/{units,weapons}.csv et
    retourne le chemin du dossier de l'armee."""
    army_dir = os.path.join(base_output_dir, army.army_name.replace(" ", "_"))
    os.makedirs(army_dir, exist_ok=True)

    write_units_csv(army, os.path.join(army_dir, "units.csv"))
    write_weapons_csv(army, os.path.join(army_dir, "weapons.csv"))

    return army_dir
