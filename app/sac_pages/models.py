
"""
Data model and damage calculation logic for the Space Aces Damage Calculator.

Drop this into app/sac_pages/models.py and import it as:

    from sac_pages import models
"""

import math
import json
import os
import sys

# ------------------------------------------------------------------
# Laser definitions
# ------------------------------------------------------------------

LASERS = {
    "LW3": {
        "name_en": "LW-3 (LF-3)",
        "base_damage": 240,
        "base_damage_lvl16": 258.5,
        "shots_per_second": 1.0,
        "accuracy": 0.70,
        "hidden_60": True,  # all except PR-L
    },
    "LW4": {
        "name_en": "LW-4 (LF-4)",
        "base_damage": 320,
        "base_damage_lvl16": 344,
        "shots_per_second": 1.0,
        "accuracy": 0.70,
        "hidden_60": True,
    },
    "LW4U": {
        "name_en": "LW-4U (LF-4U)",
        "base_damage": 160,
        "base_damage_lvl16": 172,
        "shots_per_second": 2.0,  # 2 shots per second
        "accuracy": 0.70,
        "hidden_60": True,
    },
    "PRL": {
        "name_en": "PR-L (Prometheus)",
        "base_damage": 600,
        "base_damage_lvl16": 645,
        "shots_per_second": 1.0 / 2.5,  # one shot every 2.5 s
        "accuracy": 0.75,
        "hidden_60": False,
    },
}

# ------------------------------------------------------------------
# Ammo definitions
# ------------------------------------------------------------------

AMMO = {
    "LPC11": {
        "name_en": "LPC-11 (x1 / LCB-10)",
        "mult_normal": 1.0,
        "mult_pirate": 1.0,
    },
    "PCC25": {
        "name_en": "PCC-25 (x2 / MCB-25)",
        "mult_normal": 2.0,
        "mult_pirate": 2.0,
    },
    "PCC50": {
        "name_en": "PCC-50 (x3 / MCB-50)",
        "mult_normal": 3.0,
        "mult_pirate": 3.0,
    },
    "QRB101": {
        "name_en": "QRB-101 (x4 / UCB-100)",
        "mult_normal": 4.0,
        "mult_pirate": 4.0,
    },
    "LSA50": {
        "name_en": "LSA-50 (x2 leech / SAB-50)",
        "mult_normal": 2.0,
        "mult_pirate": 2.0,
    },
    "RLPC75": {
        "name_en": "RLPC-75 (x6 / RSB-75)",
        "mult_normal": 6.0,
        "mult_pirate": 6.0,
    },
    "HSAX": {
        "name_en": "HSA-X (x3 + leech / CBO-100)",
        "mult_normal": 3.0,
        "mult_pirate": 3.0,
    },
    "LFR4C": {
        "name_en": "L-FR4C (x6 vs Pirates, x4 vs others)",
        "mult_normal": 4.0,
        "mult_pirate": 6.0,
    },
}

# ------------------------------------------------------------------
# Drone definitions
# ------------------------------------------------------------------

DRONES = {
    "IRIS": {
        "name_en": "Iris (Iova)",
        "max_count": 8,
        "max_lasers": 2,
    },
    "APIS": {
        "name_en": "Apis (Atlas)",
        "max_count": 1,
        "max_lasers": 2,
    },
    "ZEUS": {
        "name_en": "Zeus (Zagreus)",
        "max_count": 1,
        "max_lasers": 2,
    },
}

DRONE_DESIGNS = {
    "NONE": {
        "name_en": "None",
        "type": "none",
    },
    "HAVOC": {
        "name_en": "Havoc (+10% laser dmg per drone)",
        "type": "laser",
        "laser_bonus": 0.10,
    },
    "HAUNTVOC": {
        "name_en": "Haunt-Voc (+1.5% rocket dmg per drone)",
        "type": "rocket",
        "rocket_bonus": 0.015,
    },
    "VANDAL": {
        "name_en": "Vandal (+4% total dmg per drone)",
        "type": "total",
        "total_bonus": 0.04,
    },
}

# ------------------------------------------------------------------
# Formations
# ------------------------------------------------------------------

FORMATIONS = {
    "NONE": {
        "name_en": "None",
        "laser_global_mult": 1.0,
        "npc_laser_mult": 1.0,
        "rocket_mult": 1.0,
    },
    "TURTLE": {
        "name_en": "Turtle (-7.5% dmg)",
        "laser_global_mult": 0.925,
        "npc_laser_mult": 1.0,
        "rocket_mult": 0.925,
    },
    "HEART": {
        "name_en": "Heart (-5% dmg)",
        "laser_global_mult": 0.95,
        "npc_laser_mult": 1.0,
        "rocket_mult": 0.95,
    },
    "BARRIER": {
        "name_en": "Barrier (+5% NPC dmg)",
        "laser_global_mult": 1.0,
        "npc_laser_mult": 1.05,
        "rocket_mult": 1.0,
    },
    "ARROW": {
        "name_en": "Arrow (+20% rocket dmg)",
        "laser_global_mult": 1.0,
        "npc_laser_mult": 1.0,
        "rocket_mult": 1.20,
    },
    "STAR": {
        "name_en": "Star (+25% rocket dmg)",
        "laser_global_mult": 1.0,
        "npc_laser_mult": 1.0,
        "rocket_mult": 1.25,
    },
    "DOUBLE_ARROW": {
        "name_en": "Double Arrow (+30% rocket dmg)",
        "laser_global_mult": 1.0,
        "npc_laser_mult": 1.0,
        "rocket_mult": 1.30,
    },
    "CHEVRON": {
        "name_en": "Chevron (+65% rocket dmg)",
        "laser_global_mult": 1.0,
        "npc_laser_mult": 1.0,
        "rocket_mult": 1.65,
    },
}

# ------------------------------------------------------------------
# Rockets
# ------------------------------------------------------------------

ROCKETS = {
    "NONE": {
        "name_en": "None",
        "base_damage": 0,
        "accuracy": 1.0,
        "shots_per_second": 0.0,
    },
    "SIM311": {
        "name_en": "SIM-311 (R-310)",
        "base_damage": 3000,
        "accuracy": 0.95,
        "shots_per_second": 1.0,  # approximation: one rocket per second
    },
    "S2S2026": {
        "name_en": "S2S-2026 (PLT-2026)",
        "base_damage": 5000,
        "accuracy": 0.80,
        "shots_per_second": 1.0,
    },
    "S2S2021": {
        "name_en": "S2S-2021 (PLT-2021)",
        "base_damage": 7000,
        "accuracy": 0.85,
        "shots_per_second": 1.0,
    },
    "S2S3030": {
        "name_en": "S2S-3030 (PLT-3030)",
        "base_damage": 10000,
        "accuracy": 0.70,
        "shots_per_second": 1.0,
    },
}

ROCKET_LAUNCHERS = {
    "NONE": {
        "name_en": "None",
        "rockets_per_burst": 0,
        "reload_seconds": 1.0,
    },
    "HST1": {
        "name_en": "HST-1 (3 rockets / 3 s)",
        "rockets_per_burst": 3,
        "reload_seconds": 3.0,
    },
    "HST2": {
        "name_en": "HST-2 (5 rockets / 5 s)",
        "rockets_per_burst": 5,
        "reload_seconds": 5.0,
    },
}

RL_ROCKETS = {
    "ECO10": {
        "name_en": "ECO-10",
        "base_damage": 3500,
        "accuracy": 1.0,
        "bonus_vs_saturn": 0.0,
        "bonus_vs_players": 0.0,
    },
    "HRP01": {
        "name_en": "HRP-01 (HSTRM-01, +5% vs players)",
        "base_damage": 5000,
        "accuracy": 1.0,
        "bonus_vs_saturn": 0.0,
        "bonus_vs_players": 0.05,
    },
    "ERS100": {
        "name_en": "ERS-100 (UBR-10, +100% vs Saturn faction)",
        "base_damage": 4000,
        "accuracy": 1.0,
        "bonus_vs_saturn": 1.0,
        "bonus_vs_players": 0.0,
    },
}

# ------------------------------------------------------------------
# Skill tree helpers
# ------------------------------------------------------------------

def get_saturn_conqueror_mult(level: int) -> float:
    table = [0.0, 0.02, 0.04, 0.08, 0.16, 0.25]
    return 1.0 + table[min(max(level, 0), 5)]


def get_bounty_hunter_mult(level: int) -> float:
    # currently only placeholder for PvP
    table = [0.0, 0.02, 0.04, 0.04, 0.08, 0.12]
    return 1.0 + table[min(max(level, 0), 5)]


def get_rocket_engineering_mult(level: int) -> float:
    table = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10]
    return 1.0 + table[min(max(level, 0), 5)]


def get_missile_targeting_accuracy_bonus(level: int) -> float:
    # 0, 2, 4, 6, 8, 10 % accuracy
    table = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10]
    return table[min(max(level, 0), 5)]

# ------------------------------------------------------------------
# Laser DPS core
# ------------------------------------------------------------------

def _laser_damage_per_second(state: dict) -> dict:
    """
    Laser DPS including:
    - ship lasers (laser_groups)
    - drone lasers (lasers_on_drones_by_type)
    - hidden 60 %% (except PR-L)
    - upgrade level (0.5 %% per level)
    - ammo multiplier
    - accuracy
    - drone level bonus (up to 10 %% at level 16)
    - Havoc drone designs
    - formation (Turtle, Heart, Barrier etc.)
    - Saturn Conqueror (NPC laser skill)
    - Vandal as global damage bonus
    """
    groups = state.get("laser_groups", [])
    ammo_id = state.get("ammo", "LPC11")
    ammo = AMMO.get(ammo_id, AMMO["LPC11"])
    mult = ammo["mult_pirate"] if state.get("target_is_pirate") else ammo["mult_normal"]

    # --- Ship lasers (on the ship only) ---
    ship_raw_dps = 0.0
    ship_laser_count = 0
    upgrade_by_type: dict[str, list[int]] = {}

    for g in groups:
        try:
            count = int(g.get("count", 0))
        except AttributeError:
            continue
        if count <= 0:
            continue
        laser_type = g.get("type", "LW3")
        laser_def = LASERS.get(laser_type)
        if not laser_def:
            continue
        lvl = int(g.get("upgrade", 0))

        upgrade_by_type.setdefault(laser_type, []).append(lvl)

        base = laser_def["base_damage"]
        base *= 1.0 + 0.005 * lvl  # 0.5 % per level

        if laser_def.get("hidden_60", False):
            base *= 1.6

        base *= mult
        base *= laser_def.get("accuracy", 1.0)

        dps_group = base * laser_def.get("shots_per_second", 1.0) * count
        ship_raw_dps += dps_group
        ship_laser_count += count

    # --- Drone lasers (total, across all drones) ---
    lasers_on_drones_by_type = state.get("lasers_on_drones_by_type", {})
    drone_raw_dps = 0.0
    drone_laser_count = 0

    for laser_type, value in lasers_on_drones_by_type.items():
        try:
            count = int(value or 0)
        except (TypeError, ValueError):
            continue
        if count <= 0:
            continue

        laser_def = LASERS.get(laser_type)
        if not laser_def:
            continue

        # Use the highest upgrade level defined for this laser type on the ship,
        # otherwise assume level 16 (common endgame case).
        lvls = upgrade_by_type.get(laser_type, [])
        lvl = max(lvls) if lvls else 16

        base = laser_def["base_damage"]
        base *= 1.0 + 0.005 * lvl

        if laser_def.get("hidden_60", False):
            base *= 1.6

        base *= mult
        base *= laser_def.get("accuracy", 1.0)

        dps_group = base * laser_def.get("shots_per_second", 1.0) * count
        drone_raw_dps += dps_group
        drone_laser_count += count

    raw_dps = ship_raw_dps + drone_raw_dps
    total_lasers = ship_laser_count + drone_laser_count

    # --- Drone bonuses (levels + Havoc) ---
    drones_cfg = state.get("drones", {})
    drone_count = 0
    laser_bonus_from_drones = 0.0
    vandal_drone_count = 0
    total_possible_slots = 0

    for drone_id, drone_state in drones_cfg.items():
        try:
            count = int(drone_state.get("count", 0))
        except AttributeError:
            continue
        if count <= 0:
            continue

        drone_def = DRONES.get(drone_id)
        if not drone_def:
            continue

        drone_count += count
        level = int(drone_state.get("level", 1))
        level_bonus = 0.10 * (level / 16.0)  # linear approximation

        design_id = drone_state.get("design", "NONE")
        design_def = DRONE_DESIGNS.get(design_id, DRONE_DESIGNS["NONE"])
        havoc_bonus = 0.0
        if design_def.get("type") == "laser":
            havoc_bonus = design_def.get("laser_bonus", 0.0)
        if design_def.get("type") == "total":
            vandal_drone_count += count

        laser_bonus_from_drones += (level_bonus + havoc_bonus) * count

        total_possible_slots += count * int(drone_def.get("max_lasers", 0) or 0)

    # How many lasers are actually treated as "on drones" for the multiplier:
    lasers_on_drones = min(drone_laser_count, total_lasers, total_possible_slots)

    if total_lasers > 0:
        frac_on_drones = lasers_on_drones / total_lasers
    else:
        frac_on_drones = 0.0

    if drone_count > 0:
        avg_bonus_per_drone = laser_bonus_from_drones / drone_count
    else:
        avg_bonus_per_drone = 0.0

    drone_mult = 1.0 + frac_on_drones * avg_bonus_per_drone

    # --- Formation + skills + Vandal ---
    formation_id = state.get("formation", "NONE")
    formation = FORMATIONS.get(formation_id, FORMATIONS["NONE"])
    skills = state.get("skills", {})

    saturn_mult = get_saturn_conqueror_mult(int(skills.get("saturn_conqueror", 0)))
    formation_laser_global = formation.get("laser_global_mult", 1.0)
    formation_npc_mult = formation.get("npc_laser_mult", 1.0)

    vandal_mult = 1.0
    if vandal_drone_count > 0:
        vandal_mult *= 1.0 + vandal_drone_count * DRONE_DESIGNS["VANDAL"]["total_bonus"]

    total_laser_mult = drone_mult * formation_laser_global * formation_npc_mult * saturn_mult * vandal_mult
    final_dps = raw_dps * total_laser_mult

    return {
        "dps": final_dps,
        "raw_dps_no_mult": raw_dps,
        "total_lasers": total_lasers,
        "lasers_on_drones": lasers_on_drones,
        "laser_multiplier": total_laser_mult,
        "drone_count": drone_count,
    }

# ------------------------------------------------------------------
# Rocket DPS core
# ------------------------------------------------------------------

def _standard_rocket_dps(state: dict) -> float:
    rockets_cfg = state.get("rockets", {})
    rocket_id = rockets_cfg.get("type", "NONE")
    rocket_def = ROCKETS.get(rocket_id, ROCKETS["NONE"])

    if rocket_def["base_damage"] <= 0 or rocket_def["shots_per_second"] <= 0:
        return 0.0

    skills = state["skills"]
    rocket_eng_mult = get_rocket_engineering_mult(skills.get("rocket_engineering", 0))
    acc_bonus = get_missile_targeting_accuracy_bonus(skills.get("missile_targeting", 0))

    base = rocket_def["base_damage"]
    accuracy = min(1.0, rocket_def["accuracy"] + acc_bonus)

    dps = base * accuracy * rocket_def["shots_per_second"]

    # formation rocket bonus
    formation = FORMATIONS[state["formation"]]
    dps *= formation["rocket_mult"]

    # rocket engineering
    dps *= rocket_eng_mult

    # Haunt-Voc drones bonus (+1.5 % per drone)
    drones_cfg = state["drones"]
    haunt_count = 0
    vandal_count = 0
    for _drone_id, drone_state in drones_cfg.items():
        if drone_state["count"] <= 0:
            continue
        design_id = drone_state["design"]
        design_def = DRONE_DESIGNS.get(design_id, DRONE_DESIGNS["NONE"])
        if design_def["type"] == "rocket":
            haunt_count += drone_state["count"]
        if design_def["type"] == "total":
            vandal_count += drone_state["count"]

    if haunt_count > 0:
        dps *= 1.0 + haunt_count * DRONE_DESIGNS["HAUNTVOC"]["rocket_bonus"]
    if vandal_count > 0:
        dps *= 1.0 + vandal_count * DRONE_DESIGNS["VANDAL"]["total_bonus"]

    return dps


def _rocket_launcher_dps(state: dict) -> float:
    rl_cfg = state.get("rocket_launcher", {})
    launcher_id = rl_cfg.get("launcher_type", "NONE")
    rocket_id = rl_cfg.get("rocket_type", "ECO10")

    launcher_def = ROCKET_LAUNCHERS.get(launcher_id, ROCKET_LAUNCHERS["NONE"])
    rocket_def = RL_ROCKETS.get(rocket_id, RL_ROCKETS["ECO10"])

    if launcher_def["rockets_per_burst"] <= 0 or launcher_def["reload_seconds"] <= 0:
        return 0.0

    skills = state["skills"]
    rocket_eng_mult = get_rocket_engineering_mult(skills.get("rocket_engineering", 0))

    rockets_per_second = launcher_def["rockets_per_burst"] / launcher_def["reload_seconds"]

    base = rocket_def["base_damage"]
    accuracy = rocket_def["accuracy"]  # assumed 1.0

    # special bonus vs Saturn faction
    target_is_saturn = rl_cfg.get("target_is_saturn", False)
    if target_is_saturn:
        base *= (1.0 + rocket_def.get("bonus_vs_saturn", 0.0))

    dps = base * accuracy * rockets_per_second

    # formation
    formation = FORMATIONS[state["formation"]]
    dps *= formation["rocket_mult"]

    # rocket engineering
    dps *= rocket_eng_mult

    # Haunt-Voc + Vandal
    drones_cfg = state["drones"]
    haunt_count = 0
    vandal_count = 0
    for _drone_id, drone_state in drones_cfg.items():
        if drone_state["count"] <= 0:
            continue
        design_id = drone_state["design"]
        design_def = DRONE_DESIGNS.get(design_id, DRONE_DESIGNS["NONE"])
        if design_def["type"] == "rocket":
            haunt_count += drone_state["count"]
        if design_def["type"] == "total":
            vandal_count += drone_state["count"]

    if haunt_count > 0:
        dps *= 1.0 + haunt_count * DRONE_DESIGNS["HAUNTVOC"]["rocket_bonus"]
    if vandal_count > 0:
        dps *= 1.0 + vandal_count * DRONE_DESIGNS["VANDAL"]["total_bonus"]

    return dps


def _rocket_damage_per_second(state: dict) -> float:
    return _standard_rocket_dps(state) + _rocket_launcher_dps(state)

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def calculate_damage_overview(state: dict) -> dict:
    laser_info = _laser_damage_per_second(state)
    rocket_dps = _rocket_damage_per_second(state)

    total_dps = laser_info["dps"] + rocket_dps
    npc_hp = max(1, int(state.get("npc_hp", 0)))
    if total_dps > 0:
        ttk_seconds = npc_hp / total_dps
    else:
        ttk_seconds = 0.0

    return {
        "laser_dps": laser_info["dps"],
        "rocket_dps": rocket_dps,
        "total_dps": total_dps,
        "ttk_seconds": ttk_seconds,
        "laser_multiplier": laser_info["laser_multiplier"],
        "lasers_on_drones": laser_info["lasers_on_drones"],
        "total_lasers": laser_info["total_lasers"],
        "drone_count": laser_info["drone_count"],
    }


# ------------------------------------------------------------------
# NPC data + Farming Guide helpers
# ------------------------------------------------------------------


class NPC:
    def __init__(self, npc_id, name, map_id, health, shields, reward_uri, reward_credits):
        self.id = npc_id
        self.name = name
        self.map = map_id
        self.health = int(health)
        self.shields = int(shields)
        self.reward_uri = reward_uri
        self.reward_credits = reward_credits

    @property
    def total_hp(self) -> int:
        return int(self.health) + int(self.shields)


def _get_data_dir() -> str:
    """
    Returns the path to the 'data' folder next to sac_pages (where npcs.json should live).
    """
    here = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(here), "data")
    return data_dir


def load_npcs() -> list:
    """
    Load NPC definitions from npcs.json.

    - Dev mode (python main.py in app/):
        app/data/npcs.json
    - EXE mode (SpaceAcesCompanion.exe im dist-Ordner):
        npcs.json im gleichen Ordner wie die EXE
    """
    if getattr(sys, "frozen", False):
        # Running as bundled EXE -> use folder of the .exe
        base_dir = os.path.dirname(sys.executable)
        npc_file = os.path.join(base_dir, "npcs.json")
        mode = "EXE"
    else:
        # Dev mode -> use app/data
        data_dir = _get_data_dir()  # das zeigt bei dir auf app/data
        npc_file = os.path.join(data_dir, "npcs.json")
        mode = "DEV"

    print(f"[load_npcs] mode={mode}, npc_file={npc_file}, exists={os.path.exists(npc_file)}")

    if not os.path.exists(npc_file):
        return []

    try:
        with open(npc_file, "r", encoding="utf-8") as f:
            txt = f.read()
    except Exception as e:
        print("[load_npcs] ERROR reading file:", repr(e))
        return []

    print("[load_npcs] file length (chars):", len(txt))

    try:
        raw = json.loads(txt)
    except Exception as e:
        print("[load_npcs] ERROR parsing JSON:", repr(e))
        return []

    if isinstance(raw, list):
        print("[load_npcs] raw is list, len:", len(raw))
    else:
        print("[load_npcs] raw type is:", type(raw))

    npcs = []
    for entry in raw:
        try:
            npc = NPC(
                npc_id=entry["id"],
                name=entry["name"],
                map_id=entry.get("map", ""),
                health=entry.get("health", 0),
                shields=entry.get("shields", 0),
                reward_uri=entry.get("reward_uri", 0),
                reward_credits=entry.get("reward_credits", 0),
            )
            npcs.append(npc)
        except KeyError as e:
            print("[load_npcs] Skipping entry due to KeyError:", e, "entry:", entry)
            continue

    print("[load_npcs] final NPC count:", len(npcs))
    return npcs


NPC_MOD_NAME_MAP = {
    "Streuner": "Streuner",
    "Boss Streuner": "BossStreuner",
    "Uber Streuner": "Uber Streuner",
    "Luminid": "Lordakia",
    "Boss Luminid": "Boss Lordakia",
    "Uber Luminid": "Uber Lordakia",
    "Sylox": "Saimon",
    "Boss Sylox": "Boss Saimon",
    "Uber Sylox": "Uber Saimon",
    "Morlok": "Mordon",
    "Boss Morlok": "Boss Mordon",
    "Uber Morlok": "Uber Mordon",
    "Dreadnex": "Devolarium",
    "Boss Dreadnex": "Boss Devolarium",
    "Uber Dreadnex": "Uber Devolarium",
    "Sirelon": "Sibelon",
    "Boss Sirelon": "Boss Sibelon",
    "Uber Sirelon": "Uber Sibelon",
    "Sirelonit": "Sibelonit",
    "Boss Sirelonit": "Boss Sirelonit",
    "Uber Sirelonit": "Uber Sirelonit",
    "Luminar": "Lordakium",
    "Boss Luminar": "Boss Lordakium",
    "Uber Luminar": "Uber Lordakium",
    "Crylith": "Kristallin",
    "Boss Crylith": "Boss Kristallin",
    "Uber Crylith": "Uber Kristallin",
    "Crylox": "Kristallon",
    "Boss Crylox": "Boss Kristallon",
    "Uber Crylox": "Uber Kristallon",
    "Cuboran": "Cubicon",
    "Proteron": "Protegit",
    "Streun3r": "Streun3r",
    "Boss Streun3r": "Boss Streun3r",
    "Uber Streun3r": "Uber Streun3r",
}


def get_display_npc_name(npc: NPC, use_mod_names: bool) -> str:
    """
    Returns the display name based on MOD setting.
    """
    if not use_mod_names:
        return npc.name
    return NPC_MOD_NAME_MAP.get(npc.name, npc.name)


def suggest_best_npcs(total_dps: float, npcs: list, search_time: float = 5.0, top_n: int = 10):
    """
    Theoretical farming efficiency ranking.

    We estimate:
      - TTK (time-to-kill) = (HP + shield) / DPS
      - cycle_time  = TTK + search_time
      - kills/hour  = 3600 / cycle_time
      - uri/hour    = kills/hour * reward_uri

    Additionally we apply a simple overkill / slowkill penalty:
      - Very small TTK  (< 3 s)  gets penalised (overkill)
      - Very large TTK  (> 45 s) gets penalised (too slow)
    """
    if total_dps <= 0 or not npcs:
        return []

    # Clamp search_time to a sane range
    try:
        search_time_f = float(search_time)
    except (TypeError, ValueError):
        search_time_f = 5.0
    search_time_f = max(0.0, min(search_time_f, 60.0))

    results = []

    for npc in npcs:
        hp = max(1, npc.total_hp)
        ttk = hp / total_dps if total_dps > 0 else 0.0

        # Robust reward_uri handling (int or str)
        raw_uri = getattr(npc, "reward_uri", 0)
        try:
            uri = int(raw_uri)
        except (TypeError, ValueError):
            uri = 0

        if uri <= 0 or ttk <= 0:
            uri_per_hour = 0.0
            cycle_time = ttk + search_time_f if ttk > 0 else 0.0
        else:
            cycle_time = ttk + search_time_f
            if cycle_time <= 0:
                uri_per_hour = 0.0
            else:
                kills_per_hour = 3600.0 / cycle_time
                uri_per_hour = kills_per_hour * uri

        # Overkill / slowkill penalty on uri/hour
        if ttk <= 0:
            penalty = 0.0
        else:
            ideal_min = 3.0   # below this: overkill
            ideal_max = 45.0  # above this: too slow
            if ttk < ideal_min:
                penalty = max(0.2, ttk / ideal_min)
            elif ttk > ideal_max:
                penalty = max(0.2, ideal_max / ttk)
            else:
                penalty = 1.0

        score = uri_per_hour * penalty

        results.append(
            {
                "npc": npc,
                "hp": hp,
                "ttk": ttk,
                "cycle_time": cycle_time,
                "uri": uri,
                "uri_per_hour": uri_per_hour,
                "score": score,
            }
        )

    # Sort by score (desc)
    results.sort(key=lambda r: r["score"], reverse=True)

    if top_n and top_n > 0:
        return results[:top_n]
    return results
