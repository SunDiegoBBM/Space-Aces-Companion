
"""
Space Aces Damage Calculator – models.py
Version: drones-as-extra-lasers + proper Havoc/level scaling

- Lasers im Lasers-Tab = Schiffslaser
- lasers_on_drones_by_type = EXTRA-Laser auf Dronen (machen eigenen Schaden)
- Dronen-Level + Havoc wirken nur auf Drone-Laser (nicht auf Schiffslaser)
- Formationen, Saturn, Vandal, Booster wirken global auf alle Laser
"""

import math

# ------------------- Lasers -------------------

LASERS = {
    "LW3": {
        "name_en": "LW-3 (LF-3)",
        "base_damage": 240,
        "shots_per_second": 1.0,
        "accuracy": 0.70,
        "hidden_60": True,
    },
    "LW4": {
        "name_en": "LW-4 (LF-4)",
        "base_damage": 320,
        "shots_per_second": 1.0,
        "accuracy": 0.70,
        "hidden_60": True,
    },
    "LW4U": {
        "name_en": "LW-4U (LF-4U)",
        "base_damage": 160,
        "shots_per_second": 2.0,
        "accuracy": 0.70,
        "hidden_60": True,
    },
    "PRL": {
        "name_en": "PR-L (Prometheus)",
        "base_damage": 600,
        "shots_per_second": 1.0 / 2.5,
        "accuracy": 0.75,
        "hidden_60": False,
    },
}

# ------------------- Ammo -------------------

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

# ------------------- Drones -------------------

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

# ------------------- Formations -------------------

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

# ------------------- Rockets -------------------

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
        "shots_per_second": 1.0,
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

# ------------------- Skill helpers -------------------

def get_saturn_conqueror_mult(level: int) -> float:
    table = [0.0, 0.02, 0.04, 0.08, 0.16, 0.25]
    return 1.0 + table[min(max(level, 0), 5)]


def get_bounty_hunter_mult(level: int) -> float:
    table = [0.0, 0.02, 0.04, 0.04, 0.08, 0.12]
    return 1.0 + table[min(max(level, 0), 5)]


def get_rocket_engineering_mult(level: int) -> float:
    table = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10]
    return 1.0 + table[min(max(level, 0), 5)]


def get_missile_targeting_accuracy_bonus(level: int) -> float:
    table = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10]
    return table[min(max(level, 0), 5)]

# ------------------- Laser DPS (Ship + Drone Lasers) -------------------

def _compute_single_laser_group_dps(laser_type: str, count: int, upgrade_level: int, ammo_mult: float) -> float:
    """Hilfsfunktion: DPS einer Lasergruppe."""
    if count <= 0:
        return 0.0
    if laser_type not in LASERS:
        return 0.0

    laser_def = LASERS[laser_type]
    base = laser_def["base_damage"]
    base *= (1.0 + 0.005 * upgrade_level)  # 0.5 % pro Upgrade

    if laser_def["hidden_60"]:
        base *= 1.6

    base *= ammo_mult
    base *= laser_def["accuracy"]

    return base * laser_def["shots_per_second"] * count


def _laser_damage_per_second(state: dict) -> dict:
    """
    Berechnet Laser-DPS aus:
    - Ship-Lasern (laser_groups)
    - extra Drone-Lasern (lasers_on_drones_by_type)
    Multiplier:
    - Formationen, Saturn, Vandal, Booster: global
    - Dronen-Level + Havoc: nur auf Drone-Laser
    """

    groups = state["laser_groups"]
    ammo_id = state["ammo"]
    ammo = AMMO.get(ammo_id, AMMO["LPC11"])
    mult_ammo = ammo["mult_pirate"] if state.get("target_is_pirate") else ammo["mult_normal"]

    # 1) Schiffslaser
    raw_dps_ship = 0.0
    total_ship_lasers = 0
    for g in groups:
        count = g["count"]
        if count <= 0:
            continue
        lt = g["type"]
        dps = _compute_single_laser_group_dps(lt, count, g["upgrade"], mult_ammo)
        raw_dps_ship += dps
        total_ship_lasers += count

    # 2) Drone-Laser (extra)
    lod = state.get("lasers_on_drones_by_type") or {}
    raw_dps_drones = 0.0
    drone_lasers = 0
    for lt, count in lod.items():
        if count <= 0:
            continue
        # Drone-Laser aktuell ohne Upgrade-Level (Upgrade = 0)
        dps = _compute_single_laser_group_dps(lt, count, 0, mult_ammo)
        raw_dps_drones += dps
        drone_lasers += count

    raw_dps_total = raw_dps_ship + raw_dps_drones
    total_lasers = total_ship_lasers + drone_lasers

    # 3) Drone-Infos (Level + Havoc + Vandal)
    drones_cfg = state["drones"]
    drone_count = 0
    sum_level_bonus = 0.0
    sum_havoc_bonus = 0.0
    vandal_drone_count = 0

    for drone_id, drone_state in drones_cfg.items():
        count = drone_state["count"]
        if count <= 0:
            continue
        drone_count += count

        level = drone_state["level"]
        level_bonus = 0.10 * (level / 16.0)  # 10% auf Level 16

        design_id = drone_state["design"]
        design_def = DRONE_DESIGNS.get(design_id, DRONE_DESIGNS["NONE"])

        havoc_bonus = 0.0
        if design_def["type"] == "laser":
            havoc_bonus = design_def.get("laser_bonus", 0.0)

        if design_def["type"] == "total":
            vandal_drone_count += count

        sum_level_bonus += level_bonus * count
        sum_havoc_bonus += havoc_bonus * count

    if drone_count > 0:
        avg_level_bonus = sum_level_bonus / drone_count
        avg_havoc_bonus = sum_havoc_bonus / drone_count
    else:
        avg_level_bonus = 0.0
        avg_havoc_bonus = 0.0

    drone_specific_mult = 1.0 + avg_level_bonus + avg_havoc_bonus

    # 4) Globale Multiplikatoren
    formation = FORMATIONS[state["formation"]]
    skills = state["skills"]
    saturn_mult = get_saturn_conqueror_mult(skills.get("saturn_conqueror", 0))
    formation_laser_global = formation["laser_global_mult"]
    formation_npc_mult = formation["npc_laser_mult"]

    vandal_mult = 1.0
    if vandal_drone_count > 0:
        vandal_mult *= 1.0 + vandal_drone_count * DRONE_DESIGNS["VANDAL"]["total_bonus"]

    booster_mult = 1.0 + float(state.get("damage_booster", 0.0))

    global_mult = formation_laser_global * formation_npc_mult * saturn_mult * vandal_mult * booster_mult

    # 5) End-DPS
    ship_final = raw_dps_ship * global_mult
    drone_final = raw_dps_drones * global_mult * drone_specific_mult
    final_dps = ship_final + drone_final

    if raw_dps_total > 0:
        eff_mult = final_dps / raw_dps_total
    else:
        eff_mult = 0.0

    return {
        "dps": final_dps,
        "raw_dps_no_mult": raw_dps_total,
        "total_lasers": total_lasers,
        "lasers_on_drones": drone_lasers,
        "laser_multiplier": eff_mult,
        "drone_count": drone_count,
    }

# ------------------- Rocket DPS -------------------

def get_rocket_engineering_mult(level: int) -> float:
    table = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10]
    return 1.0 + table[min(max(level, 0), 5)]


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

    formation = FORMATIONS[state["formation"]]
    dps *= formation["rocket_mult"]
    dps *= rocket_eng_mult

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

    booster_mult = 1.0 + float(state.get("damage_booster", 0.0))
    dps *= booster_mult

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
    accuracy = rocket_def["accuracy"]

    if rl_cfg.get("target_is_saturn", False):
        base *= (1.0 + rocket_def.get("bonus_vs_saturn", 0.0))

    dps = base * accuracy * rockets_per_second

    formation = FORMATIONS[state["formation"]]
    dps *= formation["rocket_mult"]
    dps *= rocket_eng_mult

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

    booster_mult = 1.0 + float(state.get("damage_booster", 0.0))
    dps *= booster_mult

    return dps


def _rocket_damage_per_second(state: dict) -> float:
    return _standard_rocket_dps(state) + _rocket_launcher_dps(state)

# ------------------- Public API -------------------

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
