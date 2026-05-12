# ── Window ────────────────────────────────────────────────────────────────────
CELL_SIZE = 14
COLS, ROWS = 60, 45
GRID_W = COLS * CELL_SIZE
GRID_H = ROWS * CELL_SIZE
UI_H   = 120
WIN_W  = GRID_W
WIN_H  = GRID_H + UI_H

# ── Cell states ───────────────────────────────────────────────────────────────
EMPTY, BURNABLE, BURNING, BURNT = 0, 1, 2, 3

# ── Fire Core ─────────────────────────────────────────────────────────────────
FUEL_MAX   = 100.0
FUEL_START =  80.0
TEMP_BASE  =  30.0   # Eigenwärme des Fire Core — erlaubt Gras/Öl/Baum ohne externe Feuer

FUEL_DECAY = 2.0     # Flat drain per second

ENERGY_TO_FUEL = 0.025  # Per energy unit, per burning cell, per second
ENERGY_TO_TEMP = 36.0   # Per heat unit, per burning cell — TEMP ist stateless, kein Decay

MOVE_INTERVAL    = 0.13
SPRINT_INTERVAL  = 0.065
SPRINT_FUEL_PS   = 8.0
HEAT_RADIUS      = 3
AURA_INTERVAL    = 1.0
DASH_DIST        = 8
DASH_COOLDOWN    = 2.0
DASH_FUEL        = 5.0
SPARK_FUEL       = 25.0
SPARK_RANGE      = 10
SPARK_SPEED      = 12.0
SPARK_COOLDOWN   = 0.5
EXPLJUMP_RADIUS  = 5
EXPLJUMP_DIST    = 2
EXPLJUMP_BONUS   = 8.0

# ── Wind ──────────────────────────────────────────────────────────────────────
WIND_INTERVAL = 20.0
WIND_DIRS  = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
WIND_STRS  = [1.2, 1.5, 2.0, 2.5]
WIND_NAMES = {(-1,0):"N",(1,0):"S",(0,-1):"W",(0,1):"O",
              (-1,-1):"NW",(-1,1):"NO",(1,-1):"SW",(1,1):"SO"}

# ── Materials ─────────────────────────────────────────────────────────────────
# energy → FUEL gain (Energieeinheiten), heat → TEMP gain (Temperatureinheiten)
# Ordered least → most per column as per game design doc.
MATS = {
    "dry_grass":  dict(color=(230,230,73), min_temp=14, energy=1,  heat=0.9,  burn_time=7.0,  spread=0.18, points=5,   exp_r=0, label="Gras"),
    "oil":        dict(color=(122,91,6),   min_temp=280, energy=2,  heat=1.8,  burn_time=8.0,  spread=0.75, points=50,  exp_r=4, label="Oel"),
    "tree":       dict(color=(8,141,8),    min_temp=400, energy=5,  heat=2.4, burn_time=16.0, spread=0.12, points=15,  exp_r=0, label="Baum"),
    "wood":       dict(color=(162,132,14), min_temp=480, energy=6,  heat=3.0, burn_time=13.0, spread=0.18, points=20,  exp_r=0, label="Holz"),
    "car":        dict(color=(255,0,0),    min_temp=650, energy=10, heat=4.0, burn_time=10.0, spread=0.22, points=60,  exp_r=1, label="Auto"),
    "house":      dict(color=(0,0,255),    min_temp=850, energy=15, heat=5.6, burn_time=26.0, spread=0.08, points=100, exp_r=0, label="Haus"),
    "gas_station":dict(color=(255,0,255),  min_temp=350, energy=25, heat=9.0, burn_time=8.0,  spread=1.0,  points=500, exp_r=8, label="Gasp."),
    "scrap":      dict(color=(135,115,95), min_temp=900, energy=18, heat=6.4, burn_time=22.0, spread=0.04, points=200, exp_r=2, label="Schrott"),
}
MAT_ORDER = ["dry_grass", "oil", "tree", "wood", "car", "house", "scrap", "gas_station"]

BLOCK    = 12
STREET_W = 2
