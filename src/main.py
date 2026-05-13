import pygame
import random
import sys

from constants import (
    WIN_W, WIN_H, GRID_H, CELL_SIZE, ROWS, COLS,
    WIND_INTERVAL, WIND_DIRS, WIND_STRS,
    FUEL_MAX, FUEL_DECAY, TEMP_BASE,
    ENERGY_TO_FUEL, ENERGY_TO_TEMP, BURNING, MATS, SPARK_FUEL,
)
from worldgen import generate_city, find_start
from fire_core import FireCore
from simulation import update, apply_explosion, calc_core_gains
from cell import ignite
from ui import draw_ui, draw_vignette
from firefighter import (
    FireTruck, spawn_truck, count_burning_blocks,
    MAX_TRUCKS, SPAWN_INTERVAL, RETREAT_THR,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def new_wind():
    return random.choice(WIND_DIRS), random.choice(WIND_STRS)


def reset_game():
    grid     = generate_city()
    r, c     = find_start(grid)
    ignite(grid[r][c])
    core     = FireCore(r, c)
    wind, ws = new_wind()
    return grid, core, 0, False, wind, ws, WIND_INTERVAL, 0.0, 0, [], [], SPAWN_INTERVAL, ""


def _explode(expl, grid, core):
    """Player-triggered explosions: area damage + jump. Returns (score, chain_count)."""
    score = 0
    for er, ec, radius in expl:
        score += apply_explosion(grid, er, ec, radius)
        score += core.explosion_jump(er, ec, grid)
    return score, len(expl)


def _grid_explode(expl, grid, core):
    """Grid-spread explosions: area damage already done, only handle jump."""
    score = 0
    for er, ec, _ in expl:
        score += core.explosion_jump(er, ec, grid)
    return score, len(expl)


# ── input ─────────────────────────────────────────────────────────────────────

def _on_keydown(key, over, core, grid):
    """Returns (reset, score, chains, flash)."""
    if key == pygame.K_r:
        return True, 0, 0, 0.0
    if over:
        return False, 0, 0, 0.0
    if key == pygame.K_SPACE:
        s, expl = core.flame_dash(grid)
        bonus, c = _explode(expl, grid, core)
        return False, s + bonus, c, 0.4 if c else 0.0
    return False, 0, 0, 0.0


def handle_events(held, over, core, grid, sparks):
    """Returns (quit, reset, score, chains, flash)."""
    quit_game = reset = False
    score = chains = 0
    flash = 0.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game = True
        elif event.type == pygame.KEYDOWN:
            held[event.key] = True
            r, s, c, f = _on_keydown(event.key, over, core, grid)
            reset  |= r
            score  += s
            chains += c
            flash   = max(flash, f)
        elif event.type == pygame.KEYUP:
            held[event.key] = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not over:
            mx, my = event.pos
            core_px = core.c * CELL_SIZE + CELL_SIZE // 2
            core_py = core.r * CELL_SIZE + CELL_SIZE // 2
            core.spark_shot(sparks, my - core_py, mx - core_px)
    return quit_game, reset, score, chains, flash


# ── update ────────────────────────────────────────────────────────────────────

def update_logic(dt, grid, core, held, sparks, wind, wind_str, fire_trucks):
    """One frame of game logic. Returns (score, chains, flash, fuel_e)."""
    score = chains = 0
    flash = 0.0

    cs, cex = core.update(dt, grid, held, sparks)
    score += cs
    bonus, c = _explode(cex, grid, core)
    score += bonus; chains += c; flash = max(flash, 0.4 if c else 0.0)

    earned, grid_expl = update(grid, dt, wind, wind_str, core.temperature)
    score += earned
    bonus, c = _grid_explode(grid_expl, grid, core)
    score += bonus; chains += c; flash = max(flash, 0.4 if c else 0.0)

    fuel_e, heat_e   = calc_core_gains(grid)
    core.fuel        = min(FUEL_MAX, max(0.0,
        core.fuel - FUEL_DECAY * dt + fuel_e * ENERGY_TO_FUEL * dt))
    core.temperature = TEMP_BASE + heat_e * ENERGY_TO_TEMP

    for sp in sparks:
        s, expl, teleport_pos, hit_truck = sp.update(dt, grid, fire_trucks)
        score += s
        if teleport_pos:
            core.r, core.c = teleport_pos
        if hit_truck and not hit_truck.dead:
            if hit_truck.hit():
                score += apply_explosion(grid, hit_truck.cells[0][0], hit_truck.cells[0][1], 6)
        bonus, c = _explode(expl, grid, core)
        score += bonus; chains += c; flash = max(flash, 0.4 if c else 0.0)
    sparks[:] = [sp for sp in sparks if not sp.dead]

    for truck in fire_trucks:
        truck.update(dt, grid)
    fire_trucks[:] = [t for t in fire_trucks if not t.dead]

    return score, chains, flash, fuel_e


# ── render ────────────────────────────────────────────────────────────────────

def draw_frame(screen, font, font_big, grid, sparks, core, fire_trucks, score, over,
               wind, wind_str, wind_timer, flash, chains, death_cause=""):
    screen.fill((54, 54, 56))
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen, grid[r][c].color(),
                             (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))
    for truck in fire_trucks:
        truck.draw(screen)
    for sp in sparks:
        sp.draw(screen)
    core.draw(screen)

    cell = grid[core.r][core.c]
    if cell.state == BURNING:
        max_bt = MATS.get(cell.material, {}).get("burn_time", 3.0)
        vignette_ratio = min(1.0, cell.burn_t / max_bt) if max_bt > 0 else 1.0
    else:
        vignette_ratio = 0.0
    cx_px = core.c * CELL_SIZE + CELL_SIZE // 2
    cy_px = core.r * CELL_SIZE + CELL_SIZE // 2
    draw_vignette(screen, cx_px, cy_px, vignette_ratio)

    if not over:
        mx, my = pygame.mouse.get_pos()
        if 0 <= my < GRID_H:
            ready = core.spark_cd <= 0 and core.fuel >= SPARK_FUEL
            col   = (255, 230, 60) if ready else (130, 110, 40)
            pygame.draw.line(screen, col, (mx - 6, my), (mx + 6, my), 1)
            pygame.draw.line(screen, col, (mx, my - 6), (mx, my + 6), 1)

    draw_ui(screen, font, font_big, score, core, over,
            wind, wind_str, wind_timer, flash, chains, death_cause)
    pygame.display.flip()


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen   = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("PYROMANIA")
    clock    = pygame.time.Clock()
    font     = pygame.font.SysFont("Consolas", 16)
    font_big = pygame.font.SysFont("Consolas", 44, bold=True)

    grid, core, score, over, wind, wind_str, wind_timer, flash, chains, sparks, fire_trucks, truck_spawn_cd, death_cause = reset_game()
    held      = {}
    fire_lit  = False   # True once the first cell starts burning

    while True:
        dt = min(clock.tick(60) / 1000.0, 0.05)

        quit_game, reset, s, c, f = handle_events(held, over, core, grid, sparks)
        if quit_game:
            pygame.quit(); sys.exit()
        if reset:
            grid, core, score, over, wind, wind_str, wind_timer, flash, chains, sparks, fire_trucks, truck_spawn_cd, death_cause = reset_game()
            held     = {}
            fire_lit = False

        score += s; chains += c; flash = max(flash, f)

        if not over:
            wind_timer -= dt
            if wind_timer <= 0:
                wind, wind_str = new_wind()
                wind_timer = WIND_INTERVAL

            flash = max(0.0, flash - dt)
            s, c, f, fuel_e = update_logic(dt, grid, core, held, sparks, wind, wind_str, fire_trucks)
            score += s; chains += c; flash = max(flash, f)

            burning_blocks = count_burning_blocks(grid)
            if burning_blocks <= RETREAT_THR:
                for truck in fire_trucks:
                    if truck.state not in ("retreating",):
                        truck.retreat()
            else:
                truck_spawn_cd -= dt
                if truck_spawn_cd <= 0:
                    if len(fire_trucks) < MAX_TRUCKS:
                        t = spawn_truck(random)
                        if t:
                            fire_trucks.append(t)
                    truck_spawn_cd = SPAWN_INTERVAL

            if fuel_e > 0:
                fire_lit = True
            standing_on_fire = grid[core.r][core.c].state == BURNING
            if not over:
                if core.fuel <= 0:
                    over = True
                    death_cause = "KRAFTSTOFF LEER"
                elif fire_lit and not standing_on_fire:
                    over = True
                    death_cause = "FEUER ERLOSCHEN"

        draw_frame(screen, font, font_big, grid, sparks, core, fire_trucks, score, over,
                   wind, wind_str, wind_timer, flash, chains, death_cause)


if __name__ == "__main__":
    main()
