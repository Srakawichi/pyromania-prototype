import random
from constants import ROWS, COLS, BURNABLE, EMPTY, BLOCK, STREET_W
from cell import Cell


def is_street(r, c):
    return (r % BLOCK < STREET_W) or (c % BLOCK < STREET_W)


# ── Zone cell generators ───────────────────────────────────────────────────────
# Each function receives inner-block coordinates (ir, ic): 0..(inner-1)
# and returns the appropriate Cell for that position.

def _park_cell(ir, ic, rng, inner):
    if ir == inner // 2 or ic == inner // 2:
        return Cell(EMPTY, "concrete")
    in_corner = (ir <= 2 and ic <= 2) or (ir <= 2 and ic >= inner - 3) or \
                (ir >= inner - 3 and ic <= 2) or (ir >= inner - 3 and ic >= inner - 3)
    if in_corner and rng.random() < 0.85:
        return Cell(BURNABLE, "tree")
    return Cell(BURNABLE, "dry_grass") if rng.random() < 0.80 else Cell()


def _residential_cell(ir, ic, rng, inner):
    half = inner // 2
    # NW and SE quadrants are house plots; NE and SW are gardens.
    in_house_zone = (ir < half and ic < half) or (ir >= half and ic >= half)
    local_r = ir if ir < half else ir - half
    local_c = ic if ic < half else ic - half
    if in_house_zone:
        if local_r == 0 or local_c == 0:
            return Cell(BURNABLE, "wood") if rng.random() < 0.65 else Cell()
        x = rng.random()
        if x < 0.82:
            return Cell(BURNABLE, "house")
        if x < 0.92:
            return Cell(EMPTY, "concrete")
        return Cell()
    x = rng.random()
    if x < 0.55:
        return Cell(BURNABLE, "dry_grass")
    if x < 0.75:
        return Cell(BURNABLE, "tree")
    if x < 0.82:
        return Cell(BURNABLE, "wood")
    return Cell()


def _industrial_cell(ir, ic, rng, inner):
    in_oil = (3 <= ir <= 5 and 1 <= ic <= 3) or (3 <= ir <= 5 and 6 <= ic <= 8)
    in_scrap = (ir <= 2 and ic >= inner - 3) or (ir >= inner - 3 and ic <= 2)
    is_edge = ir == 0 or ir == inner - 1 or ic == 0 or ic == inner - 1
    if in_oil and rng.random() < 0.82:
        return Cell(BURNABLE, "oil")
    if in_scrap and rng.random() < 0.72:
        return Cell(BURNABLE, "scrap")
    if is_edge and rng.random() < 0.28:
        return Cell(BURNABLE, "wood")
    return Cell(EMPTY, "concrete") if rng.random() < 0.45 else Cell()


def _downtown_cell(ir, ic, rng, inner):
    is_edge = ir == 0 or ir == inner - 1 or ic == 0 or ic == inner - 1
    if is_edge:
        x = rng.random()
        if x < 0.18:
            return Cell(BURNABLE, "tree")
        if x < 0.38:
            return Cell(BURNABLE, "wood")
        return Cell()
    x = rng.random()
    if x < 0.72:
        return Cell(BURNABLE, "house")
    if x < 0.88:
        return Cell(EMPTY, "concrete")
    return Cell()


def _residential_low_cell(ir, ic, rng, inner):
    # Sparse suburban layout: small house clusters in corners, wide green areas in between.
    in_corner = (
        (ir <= 2 and ic <= 2) or (ir <= 2 and ic >= inner - 3) or
        (ir >= inner - 3 and ic <= 2) or (ir >= inner - 3 and ic >= inner - 3)
    )
    if in_corner:
        x = rng.random()
        if x < 0.45:
            return Cell(BURNABLE, "house")
        if x < 0.65:
            return Cell(BURNABLE, "wood")
        return Cell()
    x = rng.random()
    if x < 0.52:
        return Cell(BURNABLE, "dry_grass")
    if x < 0.76:
        return Cell(BURNABLE, "tree")
    if x < 0.82:
        return Cell(BURNABLE, "wood")
    return Cell()


_ZONE_FN = {
    "park":             _park_cell,
    "residential":      _residential_cell,
    "residential_low":  _residential_low_cell,
    "industrial":       _industrial_cell,
    "downtown":         _downtown_cell,
}


# ── City generation ────────────────────────────────────────────────────────────

def generate_city():
    rng  = random.Random()
    grid = [[Cell() for _ in range(COLS)] for _ in range(ROWS)]
    inner = BLOCK - STREET_W

    btype_map = {}
    for br in range(ROWS // BLOCK + 1):
        for bc in range(COLS // BLOCK + 1):
            btype_map[(br, bc)] = rng.choices(
                ["residential", "residential_low", "park", "industrial", "downtown"],
                weights=[28, 22, 20, 15, 15]
            )[0]

    for r in range(ROWS):
        for c in range(COLS):
            if is_street(r, c):
                continue
            btype = btype_map.get((r // BLOCK, c // BLOCK), "residential")
            ir = r % BLOCK - STREET_W
            ic = c % BLOCK - STREET_W
            grid[r][c] = _ZONE_FN[btype](ir, ic, rng, inner)

    # Parked cars on streets
    for _ in range(65):
        r = rng.randint(0, ROWS - 1)
        c = rng.randint(0, COLS - 1)
        if is_street(r, c) and grid[r][c].state == EMPTY and grid[r][c].material is None:
            grid[r][c] = Cell(BURNABLE, "car")

    # Oil puddles on streets — denser near industrial zones, sparse elsewhere
    for _ in range(120):
        r = rng.randint(0, ROWS - 1)
        c = rng.randint(0, COLS - 1)
        if not (is_street(r, c) and grid[r][c].state == EMPTY and grid[r][c].material is None):
            continue
        btype = btype_map.get((r // BLOCK, c // BLOCK), "residential")
        threshold = 0.40 if btype == "industrial" else 0.08
        if rng.random() < threshold:
            grid[r][c] = Cell(BURNABLE, "oil")

    # Interactive streets: pair isolated cars with nearby oil for chain-reaction setups
    for r in range(ROWS):
        for c in range(COLS):
            if not is_street(r, c) or grid[r][c].material != "car":
                continue
            has_nearby_oil = any(
                0 <= r + dr < ROWS and 0 <= c + dc < COLS and
                is_street(r + dr, c + dc) and grid[r + dr][c + dc].material == "oil"
                for dr in range(-3, 4) for dc in range(-3, 4)
            )
            if has_nearby_oil or rng.random() > 0.50:
                continue
            candidates = [
                (r + dr, c + dc)
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]
                if 0 <= r + dr < ROWS and 0 <= c + dc < COLS
                and is_street(r + dr, c + dc)
                and grid[r + dr][c + dc].state == EMPTY
                and grid[r + dr][c + dc].material is None
            ]
            if candidates:
                nr, nc = rng.choice(candidates)
                grid[nr][nc] = Cell(BURNABLE, "oil")

    # Gas stations — prefer industrial blocks
    for _ in range(rng.randint(1, 2)):
        for _ in range(60):
            r = rng.randint(STREET_W, ROWS - 6)
            c = rng.randint(STREET_W, COLS - 7)
            btype = btype_map.get((r // BLOCK, c // BLOCK), "residential")
            if btype != "industrial" and rng.random() < 0.65:
                continue
            if any(is_street(r + dr, c + dc) for dr in range(3) for dc in range(4)):
                continue
            for dr in range(3):
                for dc in range(4):
                    if r + dr < ROWS and c + dc < COLS:
                        grid[r + dr][c + dc] = Cell(BURNABLE, "gas_station")
            break

    return grid


def find_start(grid):
    candidates = [
        (r, c)
        for r in range(ROWS)
        for c in range(COLS)
        if grid[r][c].material == "dry_grass" and grid[r][c].state == BURNABLE
    ]
    if candidates:
        return random.choice(candidates)
    streets = [(r, c) for r in range(ROWS) for c in range(COLS)
               if is_street(r, c) and grid[r][c].state == EMPTY]
    return random.choice(streets) if streets else (ROWS // 2, COLS // 2)
