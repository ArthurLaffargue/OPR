# -*- coding: utf-8 -*-
"""
Regles speciales propres a l'armee : Eternal Wardens

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
    'Breath Attack': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Sur 2+ : 1 atk 6" Blast(3) AP(1)',
        "valid_for_IA": False,
    },
    'Lacerate': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Reroll défense D=6',
        "valid_for_IA": None,
    },
    'Re-Deployment': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Redéploie 3 unités',
        "valid_for_IA": False,
    },
    'Stealth Aura': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Donne Stealth',
        "valid_for_IA": None,
    },
    'Unpredictable Fighter': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Roll - 1-3 : AP+1 / 4-6 : Q+1',
        "valid_for_IA": None,
    },
    'Unstoppable in Melee Aura': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Unstoppable en Mélée pour unité',
        "valid_for_IA": None,
    },
    'Vanguard': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Equivalent de Scout à 9"',
        "valid_for_IA": False,
    },
    'Warden': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'AP(-1) si charge ou tire > 9"',
        "valid_for_IA": None,
    },
    'Warden Boost Aura': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'AP(-1) pur',
        "valid_for_IA": None,
    },
}
