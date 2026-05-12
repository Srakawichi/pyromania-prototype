import random
import pygame
from collections import deque
from constants import ROWS, COLS, CELL_SIZE, BLOCK, BURNABLE, BURNING, MATS
from worldgen import is_street

_RED       = (220,  30,  30)
_BLUE      = ( 50, 120, 255)
_SPEED     = 4.0   # cells / second
_FLASH_INT = 0.4   # seconds per Blaulicht toggle
_EXT_SLOW  = 1.0   # s per cell when ≤ HEAT_THR burning cells in block
_EXT_FAST  = 0.5   # s per cell when >  HEAT_THR burning cells in block
_HEAT_THR  = 8

SPAWN_INTERVAL = 5.0
MAX_TRUCKS     = 5
RETREAT_THR    = 2   # retreat when burning-block count falls to this or below


# ── helpers ───────────────────────────────────────────────────────────────────

def count_burning_blocks(grid):
    seen = set()
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c].state == BURNING:
                seen.add((r // BLOCK, c // BLOCK))
    return len(seen)


def _bfs(start, goals):
    """BFS on street cells. Returns path list (excl. start), or [] if already there / unreachable."""
    if start in goals:
        return []
    visited = {start}
    queue   = deque([(start, [])])
    while queue:
        (r, c), path = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            nxt    = (nr, nc)
            if nxt in visited or not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            if not is_street(nr, nc):
                continue
            new_path = path + [nxt]
            if nxt in goals:
                return new_path
            visited.add(nxt)
            queue.append((nxt, new_path))
    return []


def _block_streets(br, bc):
    return {
        (r, c)
        for r in range(br * BLOCK, min((br + 1) * BLOCK, ROWS))
        for c in range(bc * BLOCK, min((bc + 1) * BLOCK, COLS))
        if is_street(r, c)
    }


def _burning_in_block(grid, br, bc):
    return [
        (r, c)
        for r in range(br * BLOCK, min((br + 1) * BLOCK, ROWS))
        for c in range(bc * BLOCK, min((bc + 1) * BLOCK, COLS))
        if grid[r][c].state == BURNING
    ]


def _edge_streets():
    goals = set()
    for c in range(COLS):
        if is_street(0,        c): goals.add((0,        c))
        if is_street(ROWS - 1, c): goals.add((ROWS - 1, c))
    for r in range(ROWS):
        if is_street(r, 0):        goals.add((r, 0))
        if is_street(r, COLS - 1): goals.add((r, COLS - 1))
    return goals


def spawn_truck(rng):
    """Return a FireTruck entering from a random map-edge street, or None."""
    choices = []
    for c in range(COLS):
        if is_street(1,        c) and is_street(0,        c): choices.append(((1,        c), (0,        c), ( 1, 0)))
        if is_street(ROWS - 2, c) and is_street(ROWS - 1, c): choices.append(((ROWS - 2, c), (ROWS - 1, c), (-1, 0)))
    for r in range(ROWS):
        if is_street(r, 1)        and is_street(r, 0):        choices.append(((r, 1),        (r, 0),        (0,  1)))
        if is_street(r, COLS - 2) and is_street(r, COLS - 1): choices.append(((r, COLS - 2), (r, COLS - 1), (0, -1)))
    if not choices:
        return None
    front, back, direction = rng.choice(choices)
    return FireTruck(front, back, direction)


# ── FireTruck ─────────────────────────────────────────────────────────────────

class FireTruck:
    def __init__(self, front, back, direction):
        self.cells       = [front, back]  # [0]=front, [1]=back
        self.dr, self.dc = direction
        self.path        = []
        self.state       = "moving"       # moving | extinguishing | idle | retreating
        self.target      = None           # (br, bc)
        self.ext_timer   = 0.0
        self.ext_rate    = _EXT_SLOW
        self.move_timer  = 0.0
        self.flash_timer = 0.0
        self.flash_blue  = False
        self.hp          = 3
        self.dead        = False

    def hit(self):
        """Spark impact. Returns True if truck is destroyed."""
        self.hp -= 1
        if self.hp <= 0:
            self.dead = True
            return True
        return False

    def retreat(self):
        self.state = "retreating"
        self.path  = []

    def update(self, dt, grid):
        if self.dead:
            return
        self.flash_timer += dt
        if self.flash_timer >= _FLASH_INT:
            self.flash_timer -= _FLASH_INT
            self.flash_blue  = not self.flash_blue
        if   self.state == "moving":        self._step_move(dt, grid)
        elif self.state == "retreating":    self._step_move(dt, grid)
        elif self.state == "extinguishing": self._step_ext(dt, grid)
        elif self.state == "idle":          self._step_idle(dt, grid)

    def draw(self, screen):
        front_col = _BLUE if self.flash_blue else _RED
        for i, (r, c) in enumerate(self.cells):
            pygame.draw.rect(screen, front_col if i == 0 else _RED,
                             (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))
        fr, fc = self.cells[0]
        for i in range(3):
            dot = (255, 220, 0) if i < self.hp else (55, 55, 55)
            pygame.draw.circle(screen, dot,
                               (fc * CELL_SIZE + 3 + i * 4, fr * CELL_SIZE + 3), 2)

    # ── movement ──────────────────────────────────────────────────────────────

    def _step_move(self, dt, grid):
        self.move_timer += dt
        step = 1.0 / _SPEED
        while self.move_timer >= step and self.path:
            self.move_timer -= step
            nr, nc         = self.path.pop(0)
            self.cells[1]  = self.cells[0]
            self.cells[0]  = (nr, nc)
            self.dr        = nr - self.cells[1][0]
            self.dc        = nc - self.cells[1][1]
        if not self.path:
            if self.state == "retreating":
                self.dead = True
                return
            self._on_arrived(grid)

    def _on_arrived(self, grid):
        if not self.target:
            self._plan(grid)
            return
        br, bc  = self.target
        burning = _burning_in_block(grid, br, bc)
        if not burning:
            self.target = None
            self._plan(grid)
            return
        self.ext_rate  = _EXT_FAST if len(burning) > _HEAT_THR else _EXT_SLOW
        self.ext_timer = self.ext_rate
        self.state     = "extinguishing"

    def _plan(self, grid):
        if self.state == "retreating":
            self.path = _bfs(self.cells[0], _edge_streets())
            if not self.path:
                self.dead = True
            return
        br_bc = self._best_target(grid)
        if br_bc is None:
            self.state = "idle"
            return
        self.target = br_bc
        goals       = _block_streets(*br_bc)
        goals.discard(self.cells[0])  # Force at least 1 step — never extinguish from spawn pos
        self.path   = _bfs(self.cells[0], goals)
        if not self.path:
            self.state = "idle"

    def _step_idle(self, dt, grid):
        self.move_timer += dt
        if self.move_timer >= 2.0:
            self.move_timer = 0.0
            self.state      = "moving"
            self._plan(grid)

    # ── extinguishing ─────────────────────────────────────────────────────────

    def _step_ext(self, dt, grid):
        if not self.target:
            self.state = "moving"
            return
        br, bc  = self.target
        burning = _burning_in_block(grid, br, bc)
        if not burning:
            self.target = None
            self.state  = "moving"
            self._plan(grid)
            return
        self.ext_timer -= dt
        if self.ext_timer > 0:
            return
        fr, fc = self.cells[0]
        tr, tc = min(burning, key=lambda rc: abs(rc[0] - fr) + abs(rc[1] - fc))
        mat = grid[tr][tc].material
        grid[tr][tc].state  = BURNABLE
        grid[tr][tc].burn_t = MATS.get(mat, {}).get("burn_time", 5.0)
        self.ext_rate  = _EXT_FAST if len(burning) > _HEAT_THR else _EXT_SLOW
        self.ext_timer = self.ext_rate

    def _best_target(self, grid):
        best, best_n = None, 0
        for br in range(ROWS // BLOCK + 1):
            for bc in range(COLS // BLOCK + 1):
                n = len(_burning_in_block(grid, br, bc))
                if n > best_n:
                    best_n, best = n, (br, bc)
        return best
