import math
import pygame
from constants import ROWS, COLS, MATS, BURNING, BURNABLE, SPARK_SPEED, SPARK_RANGE, CELL_SIZE
from cell import ignite


class Spark:
    def __init__(self, r, c, dr, dc):
        self.fr   = float(r) + 0.5
        self.fc   = float(c) + 0.5
        mag       = math.hypot(dr, dc) or 1.0
        self.vr   = dr / mag
        self.vc   = dc / mag
        self.dist = 0.0
        self.dead = False

    def update(self, dt, grid, fire_trucks=()):
        """Returns (score, explosions, teleport_pos, hit_truck).
        hit_truck is the FireTruck instance that was struck, or None."""
        if self.dead:
            return 0, [], None, None
        move       = SPARK_SPEED * dt
        self.fr   += self.vr * move
        self.fc   += self.vc * move
        self.dist += move
        if self.dist >= SPARK_RANGE:
            self.dead = True
            return 0, [], None, None
        if self.dist < 1.0:
            return 0, [], None, None
        r, c = int(self.fr), int(self.fc)
        if not (0 <= r < ROWS and 0 <= c < COLS):
            self.dead = True
            return 0, [], None, None
        for truck in fire_trucks:
            if not truck.dead and (r, c) in truck.cells:
                self.dead = True
                return 0, [], None, truck
        cell = grid[r][c]
        if cell.state == BURNING:
            self.dead = True
            return 0, [], (r, c), None
        if cell.state == BURNABLE:
            ignite(cell)
            self.dead = True
            m    = MATS.get(cell.material, {})
            expl = [(r, c, m["exp_r"])] if m.get("exp_r", 0) > 0 else []
            return m.get("points", 0), expl, None, None
        return 0, [], None, None

    def draw(self, screen):
        if self.dead:
            return
        px = int(self.fc * CELL_SIZE)
        py = int(self.fr * CELL_SIZE)
        pygame.draw.circle(screen, (255, 230, 60), (px, py), 4)
        pygame.draw.circle(screen, (255, 255, 200), (px, py), 2)
