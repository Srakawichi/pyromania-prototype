import random
from constants import EMPTY, BURNABLE, BURNING, BURNT, MATS


class Cell:
    __slots__ = ("state", "material", "burn_t")

    def __init__(self, state=EMPTY, material=None):
        self.state    = state
        self.material = material
        self.burn_t   = 0.0

    def color(self):
        if self.state == BURNING:
            m = self.material
            if m in ("oil", "gas_station"):
                return (random.randint(200,255), random.randint(175,255), random.randint(40,120))
            if m == "dry_grass":
                return (random.randint(220,255), random.randint(185,230), 5)
            return (random.randint(205,255), random.randint(50,145), 0)
        if self.state == BURNABLE:
            d = MATS.get(self.material)
            return d["color"] if d else (145,145,145)
        if self.state == BURNT:
            return (28, 26, 24)
        return (105,108,118) if self.material == "concrete" else (54,54,56)


def ignite(cell):
    cell.state  = BURNING
    cell.burn_t = MATS.get(cell.material, {}).get("burn_time", 3.0)
