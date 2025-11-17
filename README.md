# Space Aces Companion

A modern, user-friendly desktop companion app for **Space Aces**, built with Python and PySide6.  
The tool provides quick access to game information, calculators, and utilities — all in one clean interface.

---

## 🚀 Features (Work in Progress)

### ✔️ Dashboards & Navigation
A modern, space-themed interface with:
- Clickable navigation panel
- Modular page system (`Wiki`, `Damage Calculator`, `Quest Helper`, `Farming Guide`, `Settings`)
- Optional RGB UI elements

---

## 📘 Current Modules

### 1. **Wiki (WIP)**
Provides structured information about:
- Ships  
- NPCs  
- Items  
- Lasers  
- Maps  
- Drones & formations  

Data is designed to come from configurable JSON files for easy editing.

---

### 2. **Damage Calculator (In Development)**
Advanced damage simulation based on:
- Equipped lasers (mixed setups supported)  
- Ammo types  
- Rocket & rocket launcher damage  
- Drone formations  
- Skill tree levels  
- Upgrade levels  

Also includes support for MOD mode:
- `LW-3 = LF-3`
- `LW-4 = LF-4`
- `LW-4U = LF-4U`
- `PR-L = Prometheus`
- Ammo equivalences are also supported.

---

### 3. **Quest Helper (WIP)**
Displays:
- Quest descriptions  
- Objectives  
- Maps  
- Rewards  

Designed for quick lookup without switching to the browser.

---

### 4. **NPC Farming Guide (Planned)**
Will allow players to input their:
- Ship loadout  
- Skilltree  
- Boosters  
- Formation  
- Damage

The tool calculates:
- The most efficient NPC to farm  
- Uri per damage  
- Time-to-kill estimations  

---

### 5. **Settings**
Includes:
- Language selection (EN/DE)
- MOD mode toggle (changes weapon names)
- RGB UI toggle

---

## 🛠️ Tech Stack

- **Python 3.12**
- **PySide6 (Qt for Python)**
- Modular folder structure for scalable development
- Single-file executable export via PyInstaller

---
## 💬 Credits

**Developer:** SunDiegoBBM  
**Project:** Space Aces unofficial companion tool  
Not affiliated with the official Space Aces developers.

---

## ⚠️ Disclaimer

This is a **non-commercial fan project**.  
Before distributing advanced features (automated parsing, in-game overlays), permission from the game owner is required.

The tool does not modify the game client and does not interact with game memory.

---

## ⭐ Future Goals

- Auto-updating system  
- More calculators (shield, speed, cooldown)  
- Full NPC + map wiki
- Theme customization  
- Better TTK simulations and DPS graphs  

---

If you like the project, feel free to ⭐ star the repository!
