
Space Aces Companion – Damage Calculator (Lasers + Drones + Rockets + Booster)
==============================================================================

Dieses Paket enthält:

- damage_page.py
- models.py

Features:

- Laser-Gruppen (LW-3, LW-4, LW-4U, PR-L) mit Count + Upgrade-Level
- Ammunition inkl. L-FR4C (Piraten-Flagge im UI)
- Dronen (Iris, Apis, Zeus) mit Count, Level, Design, Lasers / Drone
- Aggregierte Verteilung der Laser auf den Dronen:
    - LW-3 / LW-4 / LW-4U / PR-L "on drones"
- Formationen (Turtle, Heart, Barrier, Arrow, Star, Double Arrow, Chevron)
- Drone-Designs (Havoc, Haunt-Voc, Vandal)
- Skilltree:
    - Saturn Conqueror
    - Bounty Hunter
    - Rocket Engineering
    - Missile Targeting
- Rockets:
    - SIM-311, S2S-2026, S2S-2021, S2S-3030
- Rocketlauncher:
    - HST-1, HST-2
- Launcher-Rockets:
    - ECO-10, HRP-01, ERS-100 (+100 % vs Saturn)
- Global Damage-Booster:
    - 0 %, 10 %, 20 %, 25 %
    - wirkt auf Laser + Rockets
- Ausgabe:
    - Laser DPS
    - Rocket DPS
    - Total DPS
    - Estimated TTK (NPC HP einstellbar)
    - Details (Multiplikator, Dronenanzahl, Booster etc.)

Integration:

1. Backup deiner aktuellen Dateien:
   - app/sac_pages/damage_page.py -> damage_page_old.py
   - app/sac_pages/models.py      -> models_old.py

2. Dateien aus diesem ZIP nach app/sac_pages/ kopieren:
   - damage_page.py
   - models.py

3. In app/main.py sollte weiterhin stehen:
   from sac_pages.damage_page import DamagePage

4. Im venv starten:
   - cd app
   - ..\venv\Scripts\activate
   - py main.py
