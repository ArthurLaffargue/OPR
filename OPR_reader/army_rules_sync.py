# -*- coding: utf-8 -*-
"""
OPR_reader.army_rules_sync
============================

Gere le fichier `army_rules.py` de chaque armee (equivalent, pour les
regles specifiques a une faction, du `rules_data.py` generique) :

- s'il n'existe pas encore, il est cree a partir du template
  `army_rules_template.py` (dictionnaire ARMY_RULES vide) ;
- a chaque mise a jour, on verifie que toutes les regles "army_specific"
  detectees dans le fichier Army Forge (celles absentes de CORE_RULES)
  sont bien presentes dans ce fichier ; celles qui manquent sont
  ajoutees automatiquement avec une description vide ;
- les entrees deja renseignees par l'utilisateur ne sont jamais
  modifiees ni supprimees, meme si la regle n'est plus utilisee dans la
  version courante de la liste (on privilegie ne rien perdre de ce qui
  a ete tape a la main).
"""

import importlib.util
import os

from .parser import ArmyList

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "army_rules_template.py")


def collect_army_specific_rules(army: ArmyList) -> dict:
    """
    Parcourt toutes les unites/armes de l'armee et retourne un dict :
        { nom_regle: {"has_param": bool, "used_by": set(str)} }
    pour toutes les regles classees "army_specific" (i.e. absentes du
    corps de regles de base).
    """
    result = {}

    def register(rule, used_by_label):
        if rule["source"] != "army_specific":
            return
        name = rule["name"]
        entry = result.setdefault(name, {"has_param": False, "used_by": set()})
        if rule["param"] is not None:
            entry["has_param"] = True
        entry["used_by"].add(used_by_label)

    for u in army.units:
        for r in u.rules:
            register(r, u.name)
        for w in u.weapons:
            for r in w.rules:
                register(r, f"{u.name} ({w.name})")

    return result


def load_army_rules(py_path: str) -> dict:
    """Importe dynamiquement le fichier army_rules.py et retourne son
    dictionnaire ARMY_RULES (copie), ou {} si le fichier n'existe pas."""
    if not os.path.exists(py_path):
        return {}
    spec = importlib.util.spec_from_file_location("army_rules_module", py_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return dict(getattr(module, "ARMY_RULES", {}))


def _load_template_text() -> str:
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        return f.read()


def render_army_rules_module(army_name: str, rules: dict) -> str:
    """Genere le texte complet du fichier army_rules.py : en-tete issue
    du template (avec le nom de l'armee substitue), suivie du
    dictionnaire ARMY_RULES serialise a partir de `rules`."""
    template = _load_template_text()
    header, _, _ = template.partition("ARMY_RULES = {")
    header = header.replace("{{ARMY_NAME}}", army_name).rstrip("\n")

    lines = [header, "", "ARMY_RULES = {"]
    for name, entry in rules.items():
        lines.append(f"    {name!r}: {{")
        lines.append(f'        "has_param": {bool(entry.get("has_param", False))},')
        lines.append(f'        "category": {entry.get("category", "special_rule")!r},')
        lines.append(f'        "description": {entry.get("description", "")!r},')
        lines.append(f'        "valid_for_IA": {entry.get("valid_for_IA", None)},')
        lines.append("    },")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def sync_army_rules(army: ArmyList, army_dir: str) -> dict:
    """
    Cree/actualise army_lists/<Armee>/army_rules.py.

    Retourne un rapport :
        {
            "path": chemin du fichier,
            "created": True si le fichier vient d'etre cree,
            "newly_added": [noms des regles ajoutees lors de cette execution],
            "incomplete_rule": [noms des regles sans description, au total],
        }
    """
    py_path = os.path.join(army_dir, "army_rules.py")
    created = not os.path.exists(py_path)

    existing = {} if created else load_army_rules(py_path)
    detected = collect_army_specific_rules(army)

    newly_added = []
    for name in sorted(detected.keys()):
        if name not in existing:
            existing[name] = {
                "has_param": detected[name]["has_param"],
                "category": "special_rule",
                "description": "",
                "valid_for_IA": None,
            }
            newly_added.append(name)

    incomplete_rule = sorted(
        name for name, entry in existing.items() if entry.get("valid_for_IA") is None
    )

    content = render_army_rules_module(army.army_name, existing)
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "path": py_path,
        "created": created,
        "newly_added": newly_added,
        "incomplete_rule": incomplete_rule,
        "used_by": {name: sorted(detected[name]["used_by"]) for name in newly_added},
    }
