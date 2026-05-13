import math
import random
import pygame
from constants import (
    ROWS, COLS, CELL_SIZE, MATS, BURNABLE, BURNING, BURNT,
    FUEL_START, TEMP_BASE, HEAT_RADIUS, FUEL_MAX,
    MOVE_INTERVAL, SPRINT_INTERVAL, SPRINT_FUEL_PS,
    AURA_INTERVAL, DASH_DIST, DASH_COOLDOWN, DASH_FUEL,
    SPARK_FUEL, SPARK_COOLDOWN, EXPLJUMP_RADIUS, EXPLJUMP_DIST, EXPLJUMP_BONUS,
)
from cell import ignite
from spark import Spark


class FireCore:
    def __init__(self, r, c):
        self.r           = r
        self.c           = c
        self.fuel        = FUEL_START
        self.temperature = TEMP_BASE
        self.heat_radius = HEAT_RADIUS
        self.last_dr     = 0
        self.last_dc     = 1
        self.move_timer  = 0.0
        self.dash_cd     = 0.0
        self.spark_cd    = 0.0
        self.aura_timer  = 0.0
        self.anim        = 0.0

    def update(self, dt, grid, held, sparks):
        score      = 0
        explosions = []

        self.dash_cd    = max(0.0, self.dash_cd  - dt)
        self.spark_cd   = max(0.0, self.spark_cd - dt)
        self.move_timer = max(0.0, self.move_timer - dt)
        self.aura_timer = max(0.0, self.aura_timer - dt)
        self.anim      += dt * 3.0

        sprinting = held.get(pygame.K_LSHIFT) or held.get(pygame.K_RSHIFT)
        if sprinting:
            self.fuel = max(0.0, self.fuel - SPRINT_FUEL_PS * dt)
        interval = SPRINT_INTERVAL if sprinting else MOVE_INTERVAL

        if self.move_timer <= 0:
            dr = dc = 0
            if held.get(pygame.K_w): dr -= 1
            if held.get(pygame.K_s): dr += 1
            if held.get(pygame.K_a): dc -= 1
            if held.get(pygame.K_d): dc += 1
            if dr != 0 or dc != 0:
                self.last_dr, self.last_dc = dr, dc
                nr = max(0, min(ROWS-1, self.r + dr))
                nc = max(0, min(COLS-1, self.c + dc))
                pts, expl = self._enter(nr, nc, grid)
                score += pts
                explosions.extend(expl)
                self.move_timer = interval

        if self.aura_timer <= 0:
            self.aura_timer = AURA_INTERVAL
            s, ex = self._heat_aura(grid)
            score += s
            explosions.extend(ex)

        return score, explosions

    def _enter(self, nr, nc, grid):
        """Normal movement: only BURNING cells are passable."""
        if grid[nr][nc].state != BURNING:
            return 0, []
        self.r, self.c = nr, nc
        return 0, []

    def _force_enter(self, nr, nc, grid):
        """Forced movement (dash/explosion): ignites BURNABLE, passes through anything."""
        self.r, self.c = nr, nc
        cell = grid[nr][nc]
        if cell.state == BURNABLE:
            m     = MATS.get(cell.material, {})
            ignite(cell)
            exp_r = m.get("exp_r", 0)
            expl  = [(nr, nc, exp_r)] if exp_r > 0 else []
            return m.get("points", 0), expl
        return 0, []

    def _heat_aura(self, grid):
        score      = 0
        explosions = []
        for dr in range(-self.heat_radius, self.heat_radius + 1):
            for dc in range(-self.heat_radius, self.heat_radius + 1):
                nr, nc = self.r + dr, self.c + dc
                if not (0 <= nr < ROWS and 0 <= nc < COLS):
                    continue
                dist = math.hypot(dr, dc)
                if dist == 0 or dist > self.heat_radius:
                    continue
                cell = grid[nr][nc]
                if cell.state != BURNABLE:
                    continue
                m = MATS.get(cell.material, {})
                if self.temperature < m.get("min_temp", 0):
                    continue
                chance = 0.65 * (1.0 - dist / (self.heat_radius + 1))
                if random.random() < chance:
                    ignite(cell)
                    score += m.get("points", 0)
                    exp_r  = m.get("exp_r", 0)
                    if exp_r > 0:
                        explosions.append((nr, nc, exp_r))
        return score, explosions

    def flame_dash(self, grid):
        if self.dash_cd > 0 or self.fuel < DASH_FUEL:
            return 0, []
        self.fuel -= DASH_FUEL
        score      = 0
        explosions = []
        for _ in range(DASH_DIST):
            nr = max(0, min(ROWS-1, self.r + self.last_dr))
            nc = max(0, min(COLS-1, self.c + self.last_dc))
            if grid[nr][nc].state not in (BURNING, BURNABLE):
                break
            pts, expl = self._force_enter(nr, nc, grid)
            score += pts
            explosions.extend(expl)
        self.dash_cd = DASH_COOLDOWN
        return score, explosions

    def spark_shot(self, sparks, dr, dc):
        if self.spark_cd > 0 or self.fuel < SPARK_FUEL:
            return
        if dr == 0 and dc == 0:
            return
        self.fuel -= SPARK_FUEL
        sparks.append(Spark(self.r, self.c, dr, dc))
        self.spark_cd = SPARK_COOLDOWN

    def explosion_jump(self, er, ec, grid):
        dist = math.hypot(self.r - er, self.c - ec)
        if dist == 0 or dist > EXPLJUMP_RADIUS:
            return 0
        dr  = self.r - er
        dc  = self.c - ec
        mag = math.hypot(dr, dc)
        ndr = round(dr / mag)
        ndc = round(dc / mag)
        for _ in range(EXPLJUMP_DIST):
            nr = max(0, min(ROWS-1, self.r + ndr))
            nc = max(0, min(COLS-1, self.c + ndc))
            if grid[nr][nc].state != BURNING:
                break
            self.r, self.c = nr, nc
        self.fuel        = min(FUEL_MAX, self.fuel + EXPLJUMP_BONUS)
        self.temperature += EXPLJUMP_BONUS * 0.5
        return 0

    def draw(self, screen):
        cx = self.c * CELL_SIZE + CELL_SIZE // 2
        cy = self.r * CELL_SIZE + CELL_SIZE // 2
        pulse = 0.5 + 0.5 * math.sin(self.anim)

        ap = self.heat_radius * CELL_SIZE
        aura_surf = pygame.Surface((ap*2+2, ap*2+2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (255, 60, 0, 18), (ap+1, ap+1), ap)
        screen.blit(aura_surf, (cx - ap - 1, cy - ap - 1))

        rg = int(CELL_SIZE * 1.8 + pulse * 4)
        glow = pygame.Surface((rg*2+1, rg*2+1), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 80, 0, 50), (rg, rg), rg)
        screen.blit(glow, (cx - rg, cy - rg))

        rb = int(CELL_SIZE * 0.75 + pulse * 2)
        pygame.draw.circle(screen, (255, 55,  0),   (cx, cy), rb)
        pygame.draw.circle(screen, (255, 185, 20),  (cx, cy), max(2, rb - 3))
        pygame.draw.circle(screen, (255, 245, 180), (cx, cy), max(1, rb - 6))

        ax = int(cx + self.last_dc * (rb + 3))
        ay = int(cy + self.last_dr * (rb + 3))
        pygame.draw.circle(screen, (255, 230, 0), (ax, ay), 2)
