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
        "valid_for_IA": False,
    },
    "AP": {
        "has_param": True,
        "category": "special_rule",
        "description": "Réduit la Défense de la cible de X lorsqu'elle encaisse une touche de cette arme.",
        "valid_for_IA": True,
    },
    "Artillery": {
        "has_param": False,
        "category": "special_rule",
        "description": "COMPLEXE : approx +1 touche distance",
        "valid_for_IA": True,
    },
    "Bane": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ignore la Régénération et force la cible à relancer ses jets de Défense naturels de 6.",
        "valid_for_IA": True,
    },
    "Blast": {
        "has_param": True,
        "category": "special_rule",
        "description": "Ignore les couverts ; chaque touche est multipliée par X (plafonné au nombre de figurines de l'unité ciblée).",
        "valid_for_IA": True,
    },
    "Caster": {
        "has_param": True,
        "category": "special_rule",
        "description": "Génère X jetons de sort par round (max 6). Permet de tenter de lancer des sorts en dépensant des jetons avant d'attaquer.",
        "valid_for_IA": False,
    },
    "Counter": {
        "has_param": False,
        "category": "special_rule",
        "description": "Frappe en premier si chargée avec cette arme ; réduit les jets d'Impact de l'unité qui charge.",
        "valid_for_IA": False,
    },
    "Deadly": {
        "has_param": True,
        "category": "special_rule",
        "description": "Chaque touche est assignée à une seule figurine et vaut X blessures ; résolu avant les autres armes.",
        "valid_for_IA": True,
    },
    "Fast": {
        "has_param": False,
        "category": "special_rule",
        "description": "+2\" en Avance, +4\" en Rush/Charge.",
        "valid_for_IA": True,
    },
    "Fear": {
        "has_param": True,
        "category": "special_rule",
        "description": "Compte comme ayant infligé X blessures supplémentaires pour déterminer le vainqueur d'un combat.",
        "valid_for_IA": True,
    },
    "Fearless": {
        "has_param": False,
        "category": "special_rule",
        "description": "En cas d'échec à un test de Moral, un jet de 4+ permet de le considérer comme réussi quand même.",
        "valid_for_IA": False,
    },
    "Flying": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut se déplacer à travers unités et terrain, ignore les effets de terrain en mouvement.",
        "valid_for_IA": False, # Prise en compte dans le moteur de déplacement
    },
    "Furious": {
        "has_param": False,
        "category": "special_rule",
        "description": "En chargeant, les jets naturels de 6 pour toucher en mêlée infligent une touche supplémentaire.",
        "valid_for_IA": True,
    },
    "Hero": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut rejoindre une unité à plusieurs figurines (jusqu'à Tough(6)) ; utilise la Défense de l'unité tant que d'autres figurines sont vivantes.",
        "valid_for_IA": False,
    },
    "Immobile": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ne peut utiliser que des actions Hold (tenir position).",
        "valid_for_IA": True, # Donne M = 0 et ADV = 0
    },
    "Impact": {
        "has_param": True,
        "category": "special_rule",
        "description": "Après une charge (si non fatiguée), lance X dés ; chaque résultat 2+ inflige une touche.",
        "valid_for_IA": True,
    },
    "Indirect": {
        "has_param": False,
        "category": "special_rule",
        "description": "-1 pour toucher en tirant après un mouvement ; peut cibler hors ligne de vue et ignore les couverts liés à l'obstruction.",
        "valid_for_IA": False,
    },
    "Limited": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ne peut être utilisée qu'une seule fois par partie.",
        "valid_for_IA": False,
    },
    "Regeneration": {
        "has_param": False,
        "category": "special_rule",
        "description": "Chaque blessure subie est ignorée sur un jet de 5+.",
        "valid_for_IA": True,
    },
    "Relentless": {
        "has_param": False,
        "category": "special_rule",
        "description": "En tirant sur une cible à plus de 9\", un jet naturel de 6 pour toucher inflige une touche supplémentaire.",
        "valid_for_IA": True,
    },
    "Reliable": {
        "has_param": False,
        "category": "special_rule",
        "description": "Attaque à Qualité 2+.",
        "valid_for_IA": True,
    },
    "Rending": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ignore la Régénération ; les jets naturels de 6 pour toucher obtiennent AP(+4).",
        "valid_for_IA": True,
    },
    "Scout": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut être mise de côté avant le déploiement puis déployée à 12\" max de sa zone, après le déploiement des autres unités.",
        "valid_for_IA": False,
    },
    "Slow": {
        "has_param": False,
        "category": "special_rule",
        "description": "-2\" en Avance, -4\" en Rush/Charge.",
        "valid_for_IA": True,
    },
    "Stealth": {
        "has_param": False,
        "category": "special_rule",
        "description": "Quand l'unité entière est tirée dessus à plus de 9\", les tireurs ont -1 pour toucher.",
        "valid_for_IA": True,
    },
    "Strider": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut ignorer les effets du terrain difficile en se déplaçant.",
        "valid_for_IA": False, # Directement dans le moteur du jeu
    },
    "Surge": {
        "has_param": False,
        "category": "special_rule",
        "description": "Sur un jet naturel de 6 pour toucher avec cette arme, inflige une touche supplémentaire.",
        "valid_for_IA": True,
    },
    "Takedown": {
        "has_param": False,
        "category": "special_rule",
        "description": "Peut cibler une figurine précise dans l'unité ciblée (traitée comme une unité de 1) ; résolu avant les autres armes.",
        "valid_for_IA": False,
    },
    "Thrust": {
        "has_param": False,
        "category": "special_rule",
        "description": "En chargeant : +1 pour toucher et AP(+1) en mêlée.",
        "valid_for_IA": True,
    },
    "Tough": {
        "has_param": True,
        "category": "special_rule",
        "description": "La figurine doit subir X blessures avant d'être retirée.",
        "valid_for_IA": False,
    },
    "Unstoppable": {
        "has_param": False,
        "category": "special_rule",
        "description": "Ignore la Régénération et tous les modificateurs négatifs appliqués à cette arme.",
        "valid_for_IA": True,
    },
    "Sergeant": {
        "has_param": False,
        "category": "command_group",
        "description": "Sur un jet naturel de 6 pour toucher en attaquant, inflige une touche supplémentaire.",
        "valid_for_IA": False,
    },
    "Musician": {
        "has_param": False,
        "category": "command_group",
        "description": "La figurine et son unité se déplacent +1\" avec les actions de mouvement.",
        "valid_for_IA": True,
    },
    "Banner": {
        "has_param": False,
        "category": "command_group",
        "description": "La figurine et son unité obtiennent +1 aux jets de test de Moral.",
        "valid_for_IA": False,
    },
}



if __name__ == "__main__":

    for name,rule in CORE_RULES.items() :
        if rule["valid_for_IA"]:
            print(name + ("(X)" if rule["has_param"] else ""),
                  " : ", rule["description"])