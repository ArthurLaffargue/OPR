# -*- coding: utf-8 -*-
"""
build_database.py
==================

Parcourt tous les fichiers .txt de army_forge_files/, les transforme
via OPR_reader, et :
  1. (re)ecrit units.csv / weapons.csv dans army_lists/ (en preservant
     la colonne "base_size_mm", saisie a la main, d'une execution a
     l'autre) ;
  2. cree/actualise army_lists/<Armee>/army_rules.py, en y ajoutant les
     nouvelles regles specifiques detectees (description a completer).

Usage :
    python build_database.py
"""

import os
import sys

from OPR_reader import parse_army_file, write_army_csvs, sync_army_rules

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "army_forge_files")
OUTPUT_DIR = os.path.join(ROOT, "army_lists")


def main():
    txt_files = sorted(
        f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".txt")
    )
    if not txt_files:
        print(f"Aucun fichier .txt trouve dans {INPUT_DIR}")
        return

    for filename in txt_files:
        filepath = os.path.join(INPUT_DIR, filename)
        print(f"--- Lecture de {filename} ---")
        try:
            army = parse_army_file(filepath)
        except Exception as exc:
            print(f"  ERREUR pendant le parsing : {exc}", file=sys.stderr)
            continue

        army_dir = write_army_csvs(army, OUTPUT_DIR)
        rules_report = sync_army_rules(army, army_dir)

        print(f"  Armee       : {army.army_name} (v{army.version})")
        print(f"  Unites      : {len(army.units)} / {army.unit_count} attendues")
        print(f"  Points      : {army.total_points} pts")
        print(f"  -> CSV ecrits dans : {army_dir}")

        if rules_report["created"]:
            print(f"  -> Nouveau fichier cree : {rules_report['path']}")

        if rules_report["newly_added"]:
            print(
                f"  -> {len(rules_report['newly_added'])} nouvelle(s) regle(s) "
                f"specifique(s) ajoutee(s) a army_rules.py (description a completer) :"
            )
            for name in rules_report["newly_added"]:
                used_by = ", ".join(rules_report["used_by"][name])
                print(f"       - {name}  (rencontree sur : {used_by})")

        if rules_report["incomplete_rule"]:
            print(
                f"  ATTENTION : {len(rules_report['incomplete_rule'])} regle(s) "
                f"specifique(s) non traitées dans army_rules.py -> "
                + ", ".join(rules_report["incomplete_rule"])
            )

        print()


if __name__ == "__main__":
    main()
