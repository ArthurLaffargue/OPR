

import re
from typing import List
from random import randint

from base_objets import Weapon, parse_rules_str



class RuleApplier :

    def __init__(self, parameter_value : int | None = None) -> None:
        self.parameter_value = parameter_value

    def mouvement(self, M, ADV):
        return M, ADV

    def atk_quality_replacer(self, tir : bool, melee : bool) -> int | None:
        return None

    def atk_quality_modifier(self, tir : bool, melee : bool) -> int:
        return 0

    def def_quality_modifier(self, tir : bool, melee : bool) -> int:
        return 0

    def atk_defense_modifier(self, tir : bool, melee : bool) -> int:
        return 0

    def def_defense_modifier(self, tir : bool, melee : bool) -> int:
        return 0

    def def_AP_modifier(self, tir : bool, melee : bool) -> int:
        return 0

    def atk_AP_modifier(self, tir : bool, melee : bool) -> int:
        return 0

    def bonus_hits(self, tir : bool, melee : bool) -> float:
        return 0

    def regeneration_ignored(self, tir : bool, melee : bool) -> bool:
        return False

    def atk_defense_reroll(self, tir : bool, melee : bool) -> float:
        return 0

    def def_defense_reroll(self, tir : bool, melee : bool) -> float:
        return 0

    def cover_ignored(self, tir : bool, melee : bool) -> bool:
        return False

    def atk_hit_multiplier(self, tir : bool, melee : bool) -> float:
        return 1

    def def_hit_multiplier(self, tir : bool, melee : bool) -> float:
        return 1

    def atk_wound_multiplier(self, tir : bool, melee : bool) -> float:
        return 1

    def def_atk_wound_multiplier(self, tir : bool, melee : bool) -> float:
        return 1

    def atk_wound_bonus(self, tir : bool, melee : bool) -> float:
        return 0

    def def_wound_reduction(self, tir : bool, melee : bool) -> float:
        return 0

    def damage_bonus(self, tir : bool, melee : bool) -> float:
        return 0

    def bonus_attacks(self,tir : bool, melee : bool) -> Weapon|None:
        return None
        return Weapon(name, nbr, dist_range, attacks, parse_rules_str(rules))

    def touch_malus_ignored(self, tir : bool, melee : bool) -> bool:
        return False



class AP(RuleApplier):
    def atk_defense_modifier(self, tir : bool, melee : bool) -> int:
        return -self.parameter_value

class Artillery(RuleApplier):
    def atk_quality_modifier(self, tir : bool, melee : bool) -> int:
        if tir : return 1
        else : return 0

class Bane(RuleApplier) :
    def regeneration_ignored(self, tir : bool, melee : bool) -> bool:
        return True

    def atk_defense_reroll(self, tir : bool, melee : bool) -> float:
        return 1/6


class Blast(RuleApplier):
    def cover_ignored(self, tir : bool, melee : bool) -> bool:
        if tir : return True
        else : return False

    def atk_hit_multiplier(self, tir : bool, melee : bool) -> float:
        if tir : return self.parameter_value
        else : return 1.0


class Deadly(RuleApplier):
    def damage_bonus(self, tir : bool, melee : bool) -> float:
        return self.parameter_value

class Fast(RuleApplier):
    def mouvement(self, M, ADV):
        return M+2, ADV+4

class Fear(RuleApplier):
    def atk_wound_multiplier(self, tir : bool, melee : bool) -> int:
        return self.parameter_value


class Furious(RuleApplier):
    def bonus_hits(self, tir : bool, melee : bool) -> float:
        if melee : return 1/6
        else : return 0

class Immobile(RuleApplier):
    def mouvement(self, M, ADV):
        return 0, 0

class Impact(RuleApplier):
    def bonus_attacks(self, tir : bool, melee : bool) -> Weapon:
        if tir : return 0
        else :
            return Weapon("Impact", 1, None, 1, parse_rules_str("Reliable"))

class Regeneration(RuleApplier):
    def def_wound_reduction(self, tir : bool, melee : bool) -> float:
        return 1/6

class Relentless(RuleApplier):
    def atk_hit_multiplier(self, tir : bool, melee : bool) -> float:
        if tir : return 1/6
        else : return 0

class Reliable(RuleApplier):
    def atk_quality_modifier(self, tir : bool, melee : bool) -> int:
        return 2

class Rending(RuleApplier):
    def regeneration_ignored(self, tir : bool, melee : bool) -> bool:
        return True

    def atk_AP_modifier(self, tir : bool, melee : bool) -> int:
        if randint(1,6) == 6 : return 4
        else : return 0

class Slow(RuleApplier):
    def mouvement(self, M, ADV):
        return max(M-2,1), max(ADV-4,2)


class Stealth(RuleApplier):

    def def_quality_modifier(self, tir : bool, melee : bool) -> int:
        if tir : return -1
        else : return 0


class Surge(RuleApplier):
    def bonus_hits(self, tir : bool, melee : bool) -> int:
        return 1/6

class Thrust(RuleApplier):
    def quality_modifier(self, tir : bool, melee : bool) -> int:
        if melee : return 1
        else : return 0

    def atk_AP_modifier(self, tir : bool, melee : bool) -> int:
        if melee : return 1
        else : return 0

class Musician(RuleApplier):
    def mouvement(self, M, ADV):
        return M+1, ADV+1