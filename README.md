Contexte du projet OPR_Battlegame : développement d'une interface graphique Python pour jouer à One Page Rules (Age of Fantasy) en mode solo.

1— le module OPR_reader — lit les exports texte d'Army Forge et les transforme en base de données CSV/Python (units.csv, weapons.csv, army_rules.py) 
en séparant automatiquement les règles spéciales "de base" des règles propres à chaque armée. 
Le système gère la persistance des données saisies manuellement par l'utilisateur d'une régénération à l'autre via jointure sur un identifiant 
d'unité stable, sans jamais écraser ce qui a déjà été renseigné 

