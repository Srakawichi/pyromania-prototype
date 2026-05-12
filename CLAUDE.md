# Projekt-Gedächtnis: Pyromania

## 🎭 Vision & Rolle
Du bist ein Senior Game Developer. Wir entwickeln "Pyromania", ein schnelles Action-Spiel, in dem der Spieler eine **Feuerkreatur (Fire Core)** steuert.
## 🛠 Coding-Prinzipien (Strikt)
Flache Hierarchie: Vermeide tiefe Verschachtelungen. Maximum: 3 Ebenen. Nutze stattdessen Early Returns und lagere Logik in kleine, spezialisierte Funktionen aus.
D.R.Y. (Don't Repeat Yourself): Logik (z.B. Brandausbreitung, Score-Berechnung) gehört in zentrale Methoden, nicht in Event-Handler.
Modularität: Halte Pygame-Events (Input), Spiellogik (Core) und Rendering (UI) strikt getrennt.
**Kern-Gefühl:** Aktives Jagen nach Brennstoff, Kettenreaktionen planen, Mobilität durch Dash/Sparks. 
**Wichtig:** Der Spieler agiert aktiv auf einem Grid, kein passives Zuschauen mehr.

## 🛠 Tech-Stack & Architektur
- **Engine:** Python + Pygame (im File pyromania/src)
- **Architektur:** Grid-basiertes System.
- **Key-Entity:** `Fire Core` (Zentrales Spieler-Objekt).

## 📍 Aktueller Status
- **Phase:** Milestone 2 (Combo-System)
- **Aktueller Fokus:** Chain-Meter & Multiplikator

---

## Materialien

Die Materialien sind nach Temperaturanforderung gestaffelt. Die Legende im UI zeigt live, was bei deiner aktuellen Temperatur erreichbar ist.

| Material    | Min-Temp | Energieeinheiten | Temperatureinheiten | Besonderheit |
|-------------|----------|------------------|---------------------|--------------|
| Gras        | 10       | 1                | 5                   | Schnell entflammbar |
| Öl          | 20       | 2                | 10                   | Explosion (Radius 4) |
| Baum        | 28       | 5                | 14                   | Brennt lange |
| Holz        | 35       | 6                | 17                   | Stabiler Midgame |
| Auto        | 42       | 10               | 21                   | Explosion (Radius 1) |
| Haus        | 55       | 15               | 30                   | Brennt sehr lange |
| Tankstelle  | 20       | 25               | 40                   | Explosion (Radius 8) |
| Schrott     | 90       | 18               | 32                   | Schwer entzündbar, High-Risk-High-Reward, Explosion (Radius 2) |

---

## Ressourcen-Formeln (sekündlicher Tick)

FUEL = Σ (burning_cells * energy[material]) * ENERGY_TO_FUEL
FUEL -= action_costs  # Dash, Sprint, Spark Shot
if FUEL <= 0 → Game Over

temp_total = Σ (burning_cells * energy[material]) * ENERGY_TO_TEMP

Beide 1x/Sekunde neu berechnet (AURA_INTERVAL).
FUEL: wird neu gesetzt (nicht aufaddiert), capped bei FUEL_MAX (100.0) — UI: Balken/Skala
TEMP: wird neu gesetzt, unlimitiert — UI: Zahl in Celsius (z.B. "4300°C")

burning_cells == 0 → FUEL = 0 → Game Over
FUEL_DECAY entfällt.

---

## Gameplay

Das Feuer hat zwei Ressourcen, die du im Blick behalten musst:

| Ressource | Beschreibung |
|-----------|--------------|
| **FUEL** | Energie des Feuers. Läuft konstant ab – brennende Materialien füllen es auf. Sinkt auf 0 → Game Over. |
| **TEMP** | Temperatur des Feuers. Bestimmt, welche Materialien entzündbar sind. Je heißer, desto mehr ist zugänglich. |

Das Feuer breitet sich nicht automatisch aus. Du musst es aktiv lenken und mit neuem Brennmaterial versorgen.

---

## 🚀 Entwicklungsplan (Milestones)

### ✅ Milestone 1: Feuer als Creature (ABGESCHLOSSEN)
- [x] **Fire Core Klasse:** `position`, `fuel`, `temperature`, `heat_radius`, `FUEL_MAX`, `FUEL_DECAY`.
- [x] **Movement:** WASD + Shift (Sprint, kostet `SPRINT_FUEL_PS`). Spawn auf `dry_grass`. Fire Core bewegt sich nur auf BURNING-Feldern.
- [x] **Game Over:** Wenn Fire Core nicht auf einem brennenden Feld steht.
- [x] **Spark = Teleport:** Trifft BURNING → teleportiert Core dorthin. Kostet `SPARK_FUEL=25`. Trifft BURNABLE → entzündet, kein Teleport.
- [x] **Heat Aura:** Jede Sekunde Prüfung umliegender Zellen (`HEAT_RADIUS=3`, distanzabhängige Chance).
- [x] **Ressourcen-Tick (1x/Sekunde):**
  - `fuel_regen = Σ (burning_cells * energy[material]) * ENERGY_TO_FUEL`
  - `temp_total = Σ (burning_cells * heat[material]) * ENERGY_TO_TEMP`
  - FUEL capped bei `FUEL_MAX`, TEMP stateless & unlimitiert
- [x] **Flame Dash (Space):** `DASH_DIST=3` Felder, `DASH_COOLDOWN=2s`, kostet `DASH_FUEL=5`.
- [x] **Spark Shot (F):** kostet `SPARK_FUEL=25`, Reichweite `SPARK_RANGE=10`, `SPARK_COOLDOWN=0.5s`.
- [x] **Explosion Jump:** Nur auf BURNING-Felder, Bonus `EXPLJUMP_BONUS=8` Fuel.

### ✅ Milestone 2: Stadt & Puzzle (ABGESCHLOSSEN)
- [x] **Zonen:** 5 Biome mit strukturierten Layouts (2026-05-11):
  - **Park**: Betonwege (Kreuz), Baum-Cluster in Ecken, Graswiesen
  - **Wohnen (dicht)**: Haus+Garten-Pärchen (NW/SE=Haus, NE/SW=Garten), Holzzaun als Trennung — ~26% Hausdichte
  - **Wohnen (locker)**: Kleine Haus-Cluster in den 4 Block-Ecken, Rest Wiese/Bäume — ~16% Hausdichte (2026-05-12)
  - **Industrie**: Ölbecken (3×3), Schrott-Depots, Holzrahmen, Tankstelle bevorzugt hier
  - **Downtown**: Dichte Hausbebauung, kein Garten, Straßenbäume/-holz als Rand
  - Map-Gewichtung: 28% dicht / 22% locker / 20% Park / 15% Industrie / 15% Downtown
- [x] **Neues Material: Schrott** — min_temp=90, hohes Reward (200 Punkte), kaum Spread (2026-05-11)
- [x] **Öllachen auf Straßen** — Brücken zwischen Blöcken, häufiger in Industriegebieten (2026-05-11)
- [x] **Interaktive Straßen** — Autos ohne nahes Öl bekommen mit 50% Chance eine Öllache direkt daneben platziert. Ergibt planbare Ketten: Öl entflammt (280°C) → heizt auf → Auto (650°C) → Auto-Explosion → nächste Öllache (2026-05-12)

### Milestone 3: Gegner & Druck

#### 🚒 Feuerwehr — Designplan (Stand 2026-05-12)

**Datei:** `src/firefighter.py` — Klasse `FireTruck`
*(Jede Gegner-/Event-Entität bekommt eine eigene Datei, kein gemeinsames entity.py)*

**Darstellung**
- Belegt 2 aufeinanderfolgende Straßenzellen: `cells = [(r_front, c_front), (r_back, c_back)]`
- Back-Zelle: fest rot `(220, 30, 30)`
- Front-Zelle: wechselt alle `0.4s` zwischen rot `(220, 30, 30)` und blau `(50, 120, 255)` (Blaulicht)

**Spawning**
- Alle `5s` ein neues Feuerwehrauto, erstes erscheint `5s` nach Spielstart
- Spawn-Position: zufällige Straßenzelle am Kartenrand, Richtung Kartenmitte
- Max. gleichzeitig aktive Trucks: `10`

**Bewegung**
- Ausschließlich auf Straßenzellen (`is_street(r, c) == True`)
- Geschwindigkeit: `4 Zellen/s`
- Pfadfindung: BFS auf Straßenzellen zum nächsten Straßenfeld des Zielblocks
- Truck fährt immer erst vollständig an, bevor er löscht (aktuelle Position wird aus dem Ziel-Set ausgeschlossen)

**Ziel-Auswahl**
- Ziel: Block mit den meisten `BURNING`-Zellen
- Neuberechnung: sofort wenn Zielblock keine `BURNING`-Zellen mehr hat
- Kein Ziel gefunden: `state = "idle"`, Retry alle 2s

**States**
| State | Beschreibung |
|---|---|
| `moving` | Navigiert über Straßen zum Zielblock |
| `extinguishing` | Steht an, löscht 1 Zelle pro Tick |
| `idle` | Kein brennender Block, wartet 2s dann erneuter Versuch |
| `retreating` | Fährt zum Kartenrand und despawnt |

**Löschmechanismus**
- 1 Zelle pro Tick, Zelle mit geringster Manhattan-Distanz zur Front zuerst
- `≤ 8` BURNING im Block → `1 Zelle / 0.5s`
- `> 8` BURNING im Block → `1 Zelle / 0.25s` (Großbrand wird schneller gelöscht)
- Ergebnis: `BURNING → BURNABLE` (Material bleibt, kann wieder entzündet werden)

**Integration `main.py`**
- `fire_trucks: list[FireTruck]`, `truck_spawn_cd: float`
- Pro Frame: `truck.update(dt, grid)` + `truck.draw(screen)` für jeden Truck
- Kein Eingriff in `simulation.py` — Trucks manipulieren Grid-Zellen direkt

**Despawn-Logik**
- Truck fährt nach jedem gelöschten Block immer zum nächsten brennenden Block
- Rückzug (alle aktiven Trucks despawnen zur nächsten Kartenrand-Straßenzelle): wenn `burning_block_count ≤ 2` (weniger als 3 Blöcke mit mind. 1 BURNING-Zelle) — verhindert, dass Trucks das Feuer bei kleinen Resten komplett auslöschen
- Wenn `burning_cell_count == 0`: Game Over (unabhängig von Trucks, bereits bestehende Logik)

**Zerstörbarkeit**
- `hp = 3` — drei Spark-Treffer zerstören den Truck
- Kollisionserkennung: `spark.py` prüft zusätzlich ob die Spark-Position eine der beiden Truck-Zellen trifft → `truck.hit()` aufrufen
- Bei `hp == 0`: Explosion wie Auto (`exp_r = 1`) an der Front-Zelle, Truck wird aus der Liste entfernt

---

- [x] **Feuerwehr:** Implementiert (2026-05-12) — `src/firefighter.py`, integriert in `spark.py` + `main.py`
- [x] **Game-Over-Screen:** Todesursache (`KRAFTSTOFF LEER` / `FEUER ERLOSCHEN`) + `MAX CHAIN xN` auf dem Endscreen (2026-05-12)
- [ ] **Regen-Event:** Globaler Debuff für Temperatur und Spread (noch nicht geplant)

---

## 📜 Coding-Regeln (Guidelines)
1. **Kein freies Klicken:** Neues Feuer nur durch den Fire Core oder Spark Shots (kostet Fuel).
2. **Fuel = Leben:** Wenn `fuel == 0`, ist der Run vorbei.
3. **Konventionen:** [Hier bevorzugten Stil eintragen, z.B. PEP8 für Python oder C# PascalCase].
4. **Scannability:** Halte Funktionen kurz und modular.

---

## 🔥 Feuerausbreitung (Pull-based Spread)

**Problem:** Push-basierter Ansatz führte zu exponentiellem Compounding — jede brennende Zelle rollte unabhängig für jeden Nachbarn, was ganze Blöcke in Sekunden vernichtete.

**Lösung (seit 2026-05-11):** Pull-basierter Ansatz in `simulation.update()`:
- Jede BURNABLE-Zelle prüft selbst ihre brennenden Nachbarn und **rollt einmal**.
- `heat_factor = min(burning_neighbors / 2.0, 1.0)` — 1 Nachbar = 50% Basis, ab 2 Nachbarn = 100%.
- Spread-Wert kommt vom **stärksten** brennenden Nachbarn (+ Wind-Multiplikator).
- Formel: `chance = best_spread * heat_factor * dt`

**Effekt:**
- Einzelne brennende Zelle: ~halbe Ausbreitungsrate
- 2+ Nachbarn: normale Rate (keine Beschleunigung durch Compounding)
- Tankstelle bleibt High-Value-Target (Radius 8), Auto-Explosion reduziert (Radius 1)

---

## ✅ Erledigt
- [x] Architekturplan finalisiert.
- [x] Milestone 1: Feuer als Creature (abgeschlossen 2026-05-11)
- [x] Feuerausbreitung: Pull-based Spread + Auto-Explosionsradius reduziert (2026-05-11)
- [x] Milestone 2 (teilweise): 4 strukturierte Zonen + Schrott-Material + Öllachen (2026-05-11)
- [x] Milestone 2 (abgeschlossen): Variable Wohndichte (dicht/locker) + Interaktive Straßen Auto+Öl-Cluster (2026-05-12)
- [x] Milestone 3 (teilweise): Feuerwehr-KI — BFS-Navigation, Blaulicht, Löschmechanismus, Rückzug bei ≤2 brennenden Blöcken, 3 Spark-Treffer → Explosion (2026-05-12)
- [x] Game-Over-Screen: Todesursache + Max Chain (2026-05-12)
