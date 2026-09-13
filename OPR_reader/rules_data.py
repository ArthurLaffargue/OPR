# -*- coding: utf-8 -*-
"""
Base de référence des règles spéciales "de base" du corps de règles AoF
(Age of Fantasy - OPR), telles que listées dans le Core Rulebook
("SPECIAL RULES REFERENCE" + "Command Groups").

Ces règles sont valables pour TOUTES les armées : si un mot-clé rencontré
dans un fichier Army Forge correspond (par son nom de base, sans le
paramètre (X)) à une entrée de ce dictionnaire, on le considère comme une
règle "core". Sinon, elle est considérée comme spécifique à l'armée (règle
maison / faction), et devra être documentée manuellement par l'utilisateur.

NB : les descriptions ci-dessous sont des reformulations synthétiques
(paraphrase) du texte du livre de règles, pas une copie littérale.
"""

CORE_RULES = {
    "Ambush": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut être mise de côté avant le déploiement et déployée après le 1er round, à plus de 9\" des ennemis. Ne peut pas prendre d'objectif le round où elle arrive.",
    },
    "AP": {
        "has_param": True,
        "category": "special_rule",
        "description": "Réduit la Défense de la cible de X lorsqu'elle encaisse une touche de cette arme.",
    },
    "Artillery": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ne peut que tenir position (Hold). Bonus pour tirer loin (+1 à plus de 9\"), mais moins facile à toucher à distance (-2 pour l'ennemi à plus de 9\").",
    },
    "Bane": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ignore la Régénération et force la cible à relancer ses jets de Défense naturels de 6.",
    },
    "Blast": {
        "has_param": True,
        "category": "special_rule",
        "description": "Ignore les couverts ; chaque touche est multipliée par X (plafonné au nombre de figurines de l'unité ciblée).",
    },
    "Caster": {
        "has_param": True,
        "category": "special_rule",
        "description": "Génère X jetons de sort par round (max 6). Permet de tenter de lancer des sorts en dépensant des jetons avant d'attaquer.",
    },
    "Counter": {
        "has_param": False,
        "category": "special_rule",
        "description": "Frappe en premier si chargée avec cette arme ; réduit les jets d'Impact de l'unité qui charge.",
    },
    "Deadly": {
        "has_param": True,
        "category": "special_rule",
        "description": "Chaque touche est assignée à une seule figurine et vaut X blessures ; résolu avant les autres armes.",
    },
    "Fast": {
        "has_param": False,
        "category": "special_rule",
        "description": "+2\" en Avance, +4\" en Rush/Charge.",
    },
    "Fear": {
        "has_param": True,
        "category": "special_rule",
        "description": "Compte comme ayant infligé X blessures supplémentaires pour déterminer le vainqueur d'un combat.",
    },
    "Fearless": {
        "has_param": False,
        "category": "special_rule",
        "description": "En cas d'échec à un test de Moral, un jet de 4+ permet de le considérer comme réussi quand même.",
    },
    "Flying": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut se déplacer à travers unités et terrain, ignore les effets de terrain en mouvement.",
    },
    "Furious": {
        "has_param": False,
        "category": "special_rule",
        "description": "En chargeant, les jets naturels de 6 pour toucher en mêlée infligent une touche supplémentaire.",
    },
    "Hero": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut rejoindre une unité à plusieurs figurines (jusqu'à Tough(6)) ; utilise la Défense de l'unité tant que d'autres figurines sont vivantes.",
    },
    "Immobile": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ne peut utiliser que des actions Hold (tenir position).",
    },
    "Impact": {
        "has_param": True,
        "category": "special_rule",
        "description": "Après une charge (si non fatiguée), lance X dés ; chaque résultat 2+ inflige une touche.",
    },
    "Indirect": {
        "has_param": False,
        "category": "special_rule",
        "description": "-1 pour toucher en tirant après un mouvement ; peut cibler hors ligne de vue et ignore les couverts liés à l'obstruction.",
    },
    "Limited": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ne peut être utilisée qu'une seule fois par partie.",
    },
    "Regeneration": {
        "has_param": False,
        "category": "special_rule",
        "description": "Chaque blessure subie est ignorée sur un jet de 5+.",
    },
    "Relentless": {
        "has_param": False,
        "category": "special_rule",
        "description": "En tirant sur une cible à plus de 9\", un jet naturel de 6 pour toucher inflige une touche supplémentaire.",
    },
    "Reliable": {
        "has_param": False,
        "category": "special_rule",
        "description": "Attaque à Qualité 2+.",
    },
    "Rending": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ignore la Régénération ; les jets naturels de 6 pour toucher obtiennent AP(+4).",
    },
    "Scout": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut être mise de côté avant le déploiement puis déployée à 12\" max de sa zone, après le déploiement des autres unités.",
    },
    "Slow": {
        "has_param": False,
        "category": "special_rule",
        "description": "-2\" en Avance, -4\" en Rush/Charge.",
    },
    "Stealth": {
        "has_param": False,
        "category": "special_rule",
        "description": "Quand l'unité entière est tirée dessus à plus de 9\", les tireurs ont -1 pour toucher.",
    },
    "Strider": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut ignorer les effets du terrain difficile en se déplaçant.",
    },
    "Surge": {
        "has_param": False,
        "category": "special_rule",
        "description": "Sur un jet naturel de 6 pour toucher avec cette arme, inflige une touche supplémentaire.",
    },
    "Takedown": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut cibler une figurine précise dans l'unité ciblée (traitée comme une unité de 1) ; résolu avant les autres armes.",
    },
    "Thrust": {
        "has_param": False,
        "category": "special_rule",
        "description": "En chargeant : +1 pour toucher et AP(+1) en mêlée.",
    },
    "Tough": {
        "has_param": True,
        "category": "special_rule",
        "description": "La figurine doit subir X blessures avant d'être retirée.",
    },
    "Unstoppable": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ignore la Régénération et tous les modificateurs négatifs appliqués à cette arme.",
    },
    "Sergeant": {
        "has_param": False,
        "category": "command_group",
        "description": "Sur un jet naturel de 6 pour toucher en attaquant, inflige une touche supplémentaire.",
    },
    "Musician": {
        "has_param": False,
        "category": "command_group",
        "description": "La figurine et son unité se déplacent +1\" avec les actions de mouvement.",
    },
    "Banner": {
        "has_param": False,
        "category": "command_group",
        "description": "La figurine et son unité obtiennent +1 aux jets de test de Moral.",
    },
}
