# -*- coding: utf-8 -*-
"""
Regles speciales propres a l'armee : Orcs

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
    'Armor': {
        "has_param": True,
        "category": 'special_rule',
        "description": "Déjà pris en compte dans la fiche d'unité",
        "valid_for_IA": False,
    },
    'Ferocious': {
        "has_param": False,
        "category": 'special_rule',
        "description": "Si l'unité charge, un 6 en touche = une touche bonus --> Approximé à 6 = touche bonus",
        "valid_for_IA": True,
    },
    'Ferocious Boost Aura': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Approximé à : Donne Ferocious(5+)',
        "valid_for_IA": True,
    },
    'Hit & Run Fighter Aura': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Bouge après charger',
        "valid_for_IA": False,
    },
    'Hit & Run Fighter': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'Bouge après charger',
        "valid_for_IA": False,
    },
    'Melee Evasion': {
        "has_param": False,
        "category": 'special_rule',
        "description": "Malus pour toucher l'unité de -1 en mélée",
        "valid_for_IA": None,
    },
    'Melee Slayer': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'When this model charges, its weapons get AP(+2) if most models in the target have Tough(3) or higher --> Approximé à AP(+2) si Tough(3)',
        "valid_for_IA": True,
    },
    'Piercing Assault': {
        "has_param": False,
        "category": 'special_rule',
        "description": 'This model gets AP(+1) when charging',
        "valid_for_IA": True,
    },
    'Piercing Assault Aura': {
        "has_param": False,
        "category": 'special_rule',
        "description": "Aura : Donne à toute l'unité",
        "valid_for_IA": True,
    },
    'Speed Feat' : {
        "has_param": False,
        "category": 'special_rule',
        "description" : "Une fois par bataille M+2/ADV+4 --> Pour IA approx en M+1/ADV+2 tout le temps",
        "valid_for_IA": True,
    }
}
