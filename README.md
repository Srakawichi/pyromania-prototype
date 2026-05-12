# 🔥 PYROMANIA

**Resource management · Chain reaction · Destruction sandbox**

Du startest als winzige Glut – eine Zigarette, ein Funke – mitten in einer prozedurale generierten Stadt. Dein Ziel: das Feuer am Leben halten, Temperatur aufbauen und eine endlose Kettenreaktion auslösen.

---

## Gameplay

Das Feuer hat zwei Ressourcen, die du im Blick behalten musst:

| Ressource | Beschreibung |
|-----------|--------------|
| **FUEL** | Energie des Feuers. Läuft konstant ab – brennende Materialien füllen es auf. Sinkt auf 0 → Game Over. |
| **TEMP** | Temperatur des Feuers. Bestimmt, welche Materialien entzündbar sind. Je heißer, desto mehr ist zugänglich. |

Das Feuer breitet sich nicht automatisch aus. Du musst es aktiv lenken und mit neuem Brennmaterial versorgen.

---

## Steuerung

| Taste | Aktion |
|-------|--------|
| **WASD / Pfeiltasten** | Feuer in eine Richtung lenken (Push) |
| **R** | Neues Spiel |

Der **Push** verstärkt die Ausbreitungswahrscheinlichkeit in die gedrückte Richtung stark und reduziert sie in die entgegengesetzte Richtung.

---

## Materialien

Die Materialien sind nach Temperaturanforderung gestaffelt. Die Legende im UI zeigt live, was bei deiner aktuellen Temperatur erreichbar ist.

| Material | Min-Temp | Besonderheit |
|----------|----------|--------------|
| Gras | 10 | Schnell entflammbar, wenig Temp-Boost – gut zum Überleben am Anfang |
| Öl | 20 | Explosion (Radius 4), starker Temp-Boost |
| Baum | 28 | Brennt lange, solider Fuel-Lieferant |
| Holz | 35 | Stabiler Midgame-Brennstoff |
| Auto | 42 | Explosion (Radius 3) |
| Haus | 55 | Brennt sehr lange, hohe Punktzahl |
| Tankstelle | 20 | Explosion (Radius 8) – massiver Boost, hohe Punktzahl |

**Explosionen** zünden alle brennbaren Zellen im Radius sofort und geben Bonus-Punkte.

---

## Externe Faktoren

- **Wind**: Zufällige Richtung und Stärke, wechselt alle 20 Sekunden. Im UI als Pfeil und Countdown sichtbar. Kombiniert mit Push für maximale Reichweite.
- **Stadtlayout**: Jeder Run generiert eine neue Stadt mit Wohngebieten, Parks und Industrieblöcken – unterschiedliche Materialdichten erzwingen unterschiedliche Strategien.

---

## Strategie-Tipps

1. **Starte auf Gras** – niedrige Temp-Anforderung, schnell entflammbar, gibt dir Zeit zum Aufbauen.
2. **Baue Temp auf** – erst mit genug Hitze brennen Holz und Häuser.
3. **Nutze Öl früh** – Öl ist schon bei Starttemperatur zugänglich und katapultiert deine Temp nach oben.
4. **Plane Kettenreaktionen** – Auto → Tankstelle → ganzer Block.
5. **Beobachte den Wind** – mit Wind im Rücken breitet sich das Feuer viel schneller aus.
6. **FUEL zuerst** – eine brennende Hausreihe kann das Feuer minutenlang am Leben halten.

---

## Installation

```bash
pip install pygame
python pyromania.py
```

Erfordert Python 3.8+ und pygame 2.x.
