# PYROMANIA

Du bist eine Feuerkreatur. Friss dich durch eine prozedurale Stadt, halte dein Feuer am Leben und löse Kettenreaktionen aus — bevor die Feuerwehr dich löscht. (Es handelt sich hierbei um dem Prototypen)

---

## Ziel

Bleib auf brennenden Zellen, sonst erlischt dein Feuer. Zwei Ressourcen halten dich am Leben:

- **FUEL** — brennende Materialien füllen es auf. Fällt es auf 0: Game Over.
- **TEMP** — bestimmt, welche Materialien du entzünden kannst. Je heißer, desto mehr Targets.

---

## Steuerung

| Taste | Aktion |
|-------|--------|
| `WASD` | Bewegen (nur auf brennenden Zellen) |
| `SHIFT` | Sprint (kostet FUEL) |
| `SPACE` | Flame Dash — 3 Felder vorwärts, zündet BURNABLE (2s Cooldown) |
| `F` | Spark Shot — Funke in Blickrichtung, zündet oder teleportiert (kostet 25 FUEL) |
| `R` | Neues Spiel |

---

## Targets & Materialien

Die Legende unten im UI zeigt live, welche Materialien bei deiner aktuellen Temperatur erreichbar sind.

| Material | Besonderheit |
|----------|--------------|
| **Gras** | Leicht entflammbar, schnell verbrannt — gut zum Starten |
| **Öl** | Explosion (Radius 4), auch auf Straßen zu finden |
| **Baum** | Brennt lang, solider Fuel-Lieferant |
| **Holz** | Stabiler Midgame-Brennstoff |
| **Auto** | Explosion (Radius 1) — oft neben Öl platziert |
| **Haus** | Brennt sehr lange, hohe Punktzahl |
| **Schrott** | Braucht extreme Hitze (900°C), hohe Punktzahl, Explosion (Radius 2) |
| **Tankstelle** | Massivste Explosion (Radius 8) — High-Risk-High-Reward |

Explosionen zünden sofort alle brennbaren Zellen im Radius und geben Bonus-Punkte.

---

## Features

- **Prozedurales Stadtlayout** — Parks, Wohngebiete (dicht/locker), Industrie, Downtown
- **Wind** — wechselt alle 20 Sekunden, beeinflusst Ausbreitungsrichtung
- **Feuerwehr** — spawnt alle 5s, löscht brennende Blöcke. 3 Spark-Treffer zerstören einen Truck (Explosion)
- **Vignetten-Effekt** — Bildschirm verdunkelt sich und der Sichtkreis zieht sich zusammen, je näher die aktuelle Zelle dem Abbrennen ist
- **Chain-System** — Kettenexplosionen bauen einen Multiplikator auf

---

## Installation

```bash
# Repo klonen
git clone https://github.com/Srakawichi/pyromania-prototype
cd pyromania-prototype

# Virtual Environment erstellen und aktivieren
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Abhängigkeiten installieren
pip install -r requirements.txt

# Spiel starten
python src/main.py
```

Erfordert Python 3.10+
