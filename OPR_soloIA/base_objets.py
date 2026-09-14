import re
from dataclasses import dataclass, field
from typing import Optional, List

RULES_SEP = ";"        # separateur utilise par csv_writer.py
RULE_WITH_PARAM_RE = re.compile(r"^([A-Za-zÀ-ÿ&' \-]+?)\((.*)\)$")

@dataclass(frozen=True)
class Rule:
    """Une regle speciale telle que stockee dans les colonnes rules_*
    des CSV, ex: Rule("Tough", "6") ou Rule("Fearless", None)."""

    name: str
    param: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.name}({self.param})" if self.param is not None else self.name

    @property
    def is_aura(self) -> bool:
        return self.name.strip().endswith("Aura")

    @property
    def param_int(self) -> Optional[int]:
        """Convertit le parametre en entier quand c'est possible
        (ex: Tough(6) -> 6). Renvoie None si pas de parametre ou si
        celui-ci n'est pas numerique (ex: Caster(+1))."""
        if self.param is None:
            return None
        try:
            return int(self.param)
        except ValueError:
            return None


def parse_rule_token(token: str) -> Rule:
    token = token.strip()
    m = RULE_WITH_PARAM_RE.match(token)
    if m:
        return Rule(m.group(1).strip(), m.group(2).strip())
    return Rule(token)


def parse_rules_str(rules_str: str) -> List[Rule]:
    """Parse une colonne 'rules_all' / 'rules_core' / 'rules_army_specific'
    (ex: "Fearless;Hero;Tough(6);Warden") en liste de Rule."""
    if not rules_str:
        return []
    return [parse_rule_token(t) for t in rules_str.split(RULES_SEP) if t.strip()]


def rules_to_str(rules: List[Rule]) -> str:
    return RULES_SEP.join(str(r) for r in rules)


@dataclass
class Weapon:
    name: str
    wielders: int
    range: Optional[int]          # None => arme de melee
    attacks: int
    rules: List[Rule] = field(default_factory=list)

    @property
    def is_ranged(self) -> bool:
        return self.range is not None

    @property
    def is_melee(self) -> bool:
        return self.range is None

    def has_rule(self, name: str) -> bool:
        return any(r.name == name for r in self.rules)

    def rule_param(self, name: str) -> Optional[str]:
        for r in self.rules:
            if r.name == name:
                return r.param
        return None

    def __repr__(self) -> str:
        portee = f'{self.range}"' if self.is_ranged else "Mêlée"
        regles = ", ".join(str(r) for r in self.rules)
        suffixe = f", {regles}" if regles else ""
        return f"{self.name} ({portee}, A{self.attacks}{suffixe})"

    @classmethod
    def from_csv_row(cls, row: dict) -> "Weapon":
        range_in = (row.get("range_in") or "").strip()
        wielders_raw = (row.get("wielders") or "").strip()
        attacks_raw = (row.get("attacks") or "").strip()
        return cls(
            name=row["weapon_name"],
            wielders=int(wielders_raw) if wielders_raw else 1,
            range=int(range_in) if range_in else None,
            attacks=int(attacks_raw) if attacks_raw else 0,
            rules=parse_rules_str(row.get("rules_all", "")),
        )



