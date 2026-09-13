# -*- coding: utf-8 -*-
"""
Regles speciales propres a l'armee : {{ARMY_NAME}}

Ce fichier est gere automatiquement par build_database.py :
- a chaque execution, les regles specifiques a cette armee detectees
  dans le fichier Army Forge (celles qui ne font pas partie des regles
  de base -> voir OPR_reader/rules_data.py) sont comparees a celles
  deja listees ici ;
- toute regle utilisee dans l'armee mais absente de ce fichier est
  ajoutee automatiquement avec une description vide ;
- les regles deja renseignees (et leurs champs "has_param"/"category")
  ne sont JAMAIS modifiees ni supprimees par le script, meme si elles
  ne sont plus utilisees par aucune unite dans le fichier courant.

A vous de completer manuellement le champ "description" de chaque
regle (et de corriger "has_param"/"category" si besoin).

Structure identique a OPR_reader/rules_data.py (CORE_RULES) :
    "NomDeLaRegle": {
        "has_param": True/False,       # ex: True pour "Warden Boost Aura(2)"
        "category": "special_rule",
        "description": "texte de la regle, ecrit par vous",
        "valid_for_IA": True / False / None --> None = erreur
    },
"""

ARMY_RULES = {
}
