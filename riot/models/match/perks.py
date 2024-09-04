from typing import Dict, List


class PerkSelection:
    def __init__(self, perk: int, var1: int, var2: int, var3: int):
        self.perk: int = perk
        self.var1: int = var1
        self.var2: int = var2
        self.var3: int = var3

    def __repr__(self) -> str:
        return f"<PerkSelection Perk={self.perk}, Var1={self.var1}, Var2={self.var2}, Var3={self.var3}>"


class PerkStyle:
    def __init__(self, description: str, selections: List[PerkSelection], style: int):
        self.description: str = description
        self.selections: List[PerkSelection] = selections
        self.style: int = style

    def __repr__(self) -> str:
        return f"<PerkStyle Description={self.description}, Style={self.style}>"


class Perks:
    def __init__(self, stat_perks: Dict[str, int], styles: List[PerkStyle]):
        self.stat_perks: Dict[str, int] = stat_perks
        self.styles: List[PerkStyle] = styles

    def __repr__(self) -> str:
        return f"<Perks StatPerks={self.stat_perks}>"
