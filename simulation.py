import random
import math
from constants import ROWS, COLS, MATS, BURNING, BURNABLE, BURNT
from cell import ignite


def neighbors(r, c):
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            if dr == dc == 0:
                continue
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                yield nr, nc, dr, dc


def wind_mult(dr, dc, wind, wind_str):
    wdot = dr*wind[0] + dc*wind[1]
    if wdot > 0:  return wind_str
    if wdot < 0:  return 1.0 / wind_str
    return 1.0


def apply_explosion(grid, er, ec, radius):
    earned = 250
    for r in range(max(0, er-radius), min(ROWS, er+radius+1)):
        for c in range(max(0, ec-radius), min(COLS, ec+radius+1)):
            if math.hypot(r-er, c-ec) <= radius:
                nb = grid[r][c]
                if nb.state == BURNABLE and random.random() < 0.72:
                    nm = MATS.get(nb.material, {})
                    ignite(nb)
                    earned += nm.get("points", 0) * 2
    return earned


def calc_core_gains(grid):
    """Sum energy and heat of all burning cells → feeds FUEL and TEMP respectively."""
    fuel_e = 0.0
    heat_e = 0.0
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c].state == BURNING:
                m = MATS.get(grid[r][c].material, {})
                fuel_e += m.get("energy", 0)
                heat_e += m.get("heat", 0)
    return fuel_e, heat_e


def update(grid, dt, wind, wind_str, temperature):
    to_ignite  = []
    to_burnt   = []
    explosions = []
    earned     = 0

    # Pass 1: age burning cells
    for r in range(ROWS):
        for c in range(COLS):
            cell = grid[r][c]
            if cell.state != BURNING:
                continue
            cell.burn_t -= dt
            if cell.burn_t <= 0:
                to_burnt.append((r, c))

    # Pass 2: pull-based spread — each burnable cell rolls once against its burning neighbors.
    # heat_factor scales with neighbor count: 1 neighbor = 0.5, 2+ = 1.0.
    # This prevents exponential compounding when many cells burn simultaneously.
    for r in range(ROWS):
        for c in range(COLS):
            cell = grid[r][c]
            if cell.state != BURNABLE:
                continue
            if temperature < MATS.get(cell.material, {}).get("min_temp", 0):
                continue

            hot = [(nr, nc, dr, dc) for nr, nc, dr, dc in neighbors(r, c)
                   if grid[nr][nc].state == BURNING]
            if not hot:
                continue

            heat_factor = min(len(hot) / 2.0, 1.0)
            best = max(
                MATS.get(grid[nr][nc].material, {}).get("spread", 0.5)
                * wind_mult(dr, dc, wind, wind_str)
                for nr, nc, dr, dc in hot
            )
            if random.random() < best * heat_factor * dt:
                to_ignite.append((r, c))

    for r, c in to_ignite:
        if grid[r][c].state == BURNABLE:
            m = MATS.get(grid[r][c].material, {})
            ignite(grid[r][c])
            earned += m.get("points", 0)
            if m.get("exp_r", 0) > 0:
                explosions.append((r, c, m["exp_r"]))

    for er, ec, radius in explosions:
        earned += apply_explosion(grid, er, ec, radius)

    for r, c in to_burnt:
        grid[r][c].state = BURNT

    return earned, explosions
