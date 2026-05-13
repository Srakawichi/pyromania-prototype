import math
import pygame
from constants import (
    GRID_H, WIN_W, WIN_H, UI_H, FUEL_MAX, CELL_SIZE,
    DASH_COOLDOWN, SPARK_COOLDOWN, MATS, MAT_ORDER, WIND_NAMES,
)


def draw_bar(surf, x, y, w, h, val, maxv, col_ok, col_low, label, font):
    pct    = val / maxv
    filled = int(w * pct)
    col    = col_ok if pct > 0.25 else col_low
    pygame.draw.rect(surf, (35,35,35), (x, y, w, h))
    if filled > 0:
        pygame.draw.rect(surf, col, (x, y, filled, h))
    surf.blit(font.render(f"{label}  {val:.0f}", True, (215,215,215)), (x+5, y+1))


def draw_cooldown(surf, x, y, w, h, cd, max_cd, label, font):
    ready  = cd <= 0
    pct    = 1.0 - (cd / max_cd) if max_cd > 0 else 1.0
    filled = int(w * min(pct, 1.0))
    pygame.draw.rect(surf, (35,35,35), (x, y, w, h))
    col = (80,200,80) if ready else (180,100,30)
    if filled > 0:
        pygame.draw.rect(surf, col, (x, y, filled, h))
    txt = f"{label} {'READY' if ready else f'{cd:.1f}s'}"
    surf.blit(font.render(txt, True, (215,215,215)), (x+5, y+1))


def draw_arrow(surf, color, cx, cy, dx, dy, length=16):
    mag = math.hypot(dx, dy)
    if mag == 0:
        return
    nx, ny = dx/mag, dy/mag
    ex, ey = cx + nx*length, cy + ny*length
    pygame.draw.line(surf, color, (int(cx), int(cy)), (int(ex), int(ey)), 3)
    ang = math.atan2(ny, nx)
    for da in (0.5, -0.5):
        ax = ex - math.cos(ang+da)*7
        ay = ey - math.sin(ang+da)*7
        pygame.draw.line(surf, color, (int(ex), int(ey)), (int(ax), int(ay)), 2)


def draw_vignette(screen, cx, cy, ratio):
    """Dark vignette + shrinking spotlight circle as the current cell's burn time runs out.

    ratio: 1.0 = freshly burning (no effect), 0.0 = cell about to burn out (max effect).
    The gradient is quadratic so the effect stays subtle until the last ~30% of burn time.
    """
    t = max(0.0, 1.0 - ratio)
    t2 = t ** 0.75  # sub-linear: clearly visible from ~40% burn time remaining
    darkness = int(240 * t2)
    if darkness < 4:
        return

    # Visible circle: shrinks from 460 px to 2 cells wide
    max_r = 460
    min_r = CELL_SIZE * 2
    visible_r = max(min_r, int(max_r + (min_r - max_r) * t2))

    # Dark overlay covering the whole grid area
    dark = pygame.Surface((WIN_W, GRID_H), pygame.SRCALPHA)
    dark.fill((0, 0, 0, darkness))

    # Spotlight: gradient circle where alpha = darkness at centre → 0 at edge.
    # Drawing from outermost (alpha=0) to innermost (alpha=darkness) means each
    # subsequent circle overwrites the inner region with higher alpha, giving the
    # correct radial gradient: alpha(r) ≈ darkness * (1 − r / visible_r).
    # BLEND_RGBA_SUB then subtracts this from the dark overlay, making the centre
    # transparent and the outer ring fully dark.
    diam = visible_r * 2 + 1
    spot = pygame.Surface((diam, diam), pygame.SRCALPHA)
    spot.fill((0, 0, 0, 0))
    steps = 20
    for i in range(steps + 1):
        r = visible_r * (steps - i) // steps
        a = darkness * i // steps
        pygame.draw.circle(spot, (0, 0, 0, a), (visible_r, visible_r), r)
    dark.blit(spot, (cx - visible_r, cy - visible_r), special_flags=pygame.BLEND_RGBA_SUB)

    screen.blit(dark, (0, 0))


def draw_ui(screen, font, font_big, score, core, over, wind, wind_str, wind_timer, flash, chains, death_cause=""):
    top = GRID_H
    pygame.draw.rect(screen, (10,10,12), (0, top, WIN_W, UI_H))

    bar_w = WIN_W // 2 - 20
    draw_bar(screen, 10, top+4, bar_w, 17, core.fuel, FUEL_MAX,
             (255,130,0), (255,45,45), "FUEL", font)

    temp_col = (255, 75, 25) if core.temperature > 30 else (70, 70, 70)
    screen.blit(font.render(f"TEMP  {core.temperature:.0f}°C", True, temp_col), (10, top+25))

    cd_x = WIN_W // 2
    draw_cooldown(screen, cd_x,     top+4,  130, 17, core.dash_cd,  DASH_COOLDOWN,  "[SPC] DASH", font)
    draw_cooldown(screen, cd_x+140, top+4,  130, 17, core.spark_cd, SPARK_COOLDOWN, "[F]  SPARK", font)

    screen.blit(font.render("WASD: Bewegen  SHIFT: Sprint  SPC: Dash  F: Spark",
                            True, (90,90,90)), (cd_x, top+25))

    screen.blit(font.render(f"SCORE  {score:,}", True, (255,210,0)), (10, top+50))
    if chains > 0:
        screen.blit(font.render(f"CHAIN x{chains}", True, (255,100,50)), (165, top+50))

    wname = WIND_NAMES.get(wind, "?")
    screen.blit(font.render(f"WIND {wname} x{wind_str:.1f} ({wind_timer:.0f}s)",
                            True, (95,170,255)), (cd_x, top+50))
    draw_arrow(screen, (95,170,255), cd_x + 200, top+61, wind[1], wind[0])

    lx = 10
    for mat in MAT_ORDER:
        m        = MATS[mat]
        unlocked = core.temperature >= m["min_temp"]
        pygame.draw.rect(screen, m["color"] if unlocked else (45,45,45), (lx, top+76, 10, 10))
        lc = (168,168,168) if unlocked else (62,62,62)
        screen.blit(font.render(m["label"], True, lc), (lx+13, top+74))
        lx += 72

    if flash > 0:
        a  = int(90 * min(flash / 0.35, 1.0))
        fl = pygame.Surface((WIN_W, GRID_H), pygame.SRCALPHA)
        fl.fill((255, 140, 0, a))
        screen.blit(fl, (0, 0))

    if over:
        ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        ov.fill((0,0,0,165))
        screen.blit(ov, (0,0))
        cx = WIN_W // 2
        cy = WIN_H // 2
        t1 = font_big.render("FIRE CORE ERLOSCHEN", True, (255,50,50))
        t2 = font.render(death_cause,               True, (255,110,60))
        t3 = font_big.render(f"SCORE:  {score:,}", True, (255,210,0))
        t4 = font.render(f"MAX CHAIN  x{chains}" if chains > 0 else "", True, (255,140,40))
        t5 = font.render("[ R ]  Neues Spiel",    True, (195,195,195))
        screen.blit(t1, (cx - t1.get_width()//2, cy - 90))
        screen.blit(t2, (cx - t2.get_width()//2, cy - 44))
        screen.blit(t3, (cx - t3.get_width()//2, cy))
        screen.blit(t4, (cx - t4.get_width()//2, cy + 52))
        screen.blit(t5, (cx - t5.get_width()//2, cy + 80))
