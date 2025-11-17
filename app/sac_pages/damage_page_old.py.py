
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTabWidget,
    QFormLayout, QFrame, QComboBox, QSpinBox, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt


class DamagePage(QWidget):


    def __init__(self, name_style: str = "vanilla"):
        super().__init__()
        self.language = "en"
        self.name_style = name_style

        self._init_static_data()
        self._init_ui()

    def _init_static_data(self):
        # Laser stats: base dmg (non-upgraded), shots per second, accuracy, hidden 60 % bonus (except PR-L)
        self.lasers = {
            "LW3": {"base": 240.0, "sps": 1.0, "acc": 0.70, "hidden60": True},
            "LW4": {"base": 320.0, "sps": 1.0, "acc": 0.70, "hidden60": True},
            "LW4U": {"base": 160.0, "sps": 2.0, "acc": 0.70, "hidden60": True},
            "PRL": {"base": 600.0, "sps": 1.0 / 2.5, "acc": 0.75, "hidden60": False},
        }

        # Ammo multipliers (damage only)
        self.ammo_ids = [
            "LPC11", "PCC25", "PCC50", "QRB101", "LSA50", "RLPC75", "HSAX", "LFR4C"
        ]

        # Rockets (single)
        self.rockets = {
            "SIM311": {"base": 3000.0, "acc": 0.95},
            "S2S2026": {"base": 5000.0, "acc": 0.80},
            "S2S2021": {"base": 7000.0, "acc": 0.85},
            "S2S3030": {"base": 10000.0, "acc": 0.70},
        }

        # Rocketlauncher rockets
        self.rl_rockets = {
            "ECO10": {"base": 3500.0},
            "HRP01": {"base": 5000.0},   # +5 % vs players – hier ignoriert
            "ERS100": {"base": 4000.0},  # +100 % vs Saturn – hier ignoriert
        }

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(10)

        self.heading = QLabel()
        self.heading.setObjectName("PageTitleLabel")
        self.heading.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.desc = QLabel()
        self.desc.setWordWrap(True)

        root.addWidget(self.heading)
        root.addWidget(self.desc)

        # Tabs
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # LASERS TAB
        tab_lasers = QWidget()
        lay_lasers = QVBoxLayout(tab_lasers)
        lay_lasers.setSpacing(8)

        self.laser_info = QLabel()
        self.laser_info.setWordWrap(True)
        lay_lasers.addWidget(self.laser_info)

        self.laser_groups = []
        form_lasers = QFormLayout()
        form_lasers.setSpacing(4)

        for i in range(3):
            combo = QComboBox()
            spin_count = QSpinBox()
            spin_count.setRange(0, 50)
            spin_level = QSpinBox()
            spin_level.setRange(0, 16)
            self.laser_groups.append((combo, spin_count, spin_level))
            form_lasers.addRow(f"Group {i+1} type:", combo)
            form_lasers.addRow(f"Group {i+1} count:", spin_count)
            form_lasers.addRow(f"Group {i+1} level:", spin_level)

        lay_lasers.addLayout(form_lasers)
        self.tabs.addTab(tab_lasers, "Lasers")

        # AMMO TAB
        tab_ammo = QWidget()
        lay_ammo = QVBoxLayout(tab_ammo)
        lay_ammo.setSpacing(8)

        self.ammo_info = QLabel()
        self.ammo_info.setWordWrap(True)
        lay_ammo.addWidget(self.ammo_info)

        self.combo_ammo = QComboBox()
        lay_ammo.addWidget(self.combo_ammo)

        self.chk_pirate = QCheckBox("Target is pirate faction (for L-FR4C)")
        lay_ammo.addWidget(self.chk_pirate)

        self.tabs.addTab(tab_ammo, "Ammo")

        # ROCKETS TAB
        tab_rockets = QWidget()
        lay_rc = QVBoxLayout(tab_rockets)
        lay_rc.setSpacing(8)

        self.rc_info = QLabel()
        self.rc_info.setWordWrap(True)
        lay_rc.addWidget(self.rc_info)

        form_rc = QFormLayout()
        self.combo_rocket = QComboBox()
        self.spin_rocket_rate = QSpinBox()
        self.spin_rocket_rate.setRange(0, 20)
        self.spin_rocket_rate.setValue(0)  # 0 = ignorieren
        form_rc.addRow("Rocket type:", self.combo_rocket)
        form_rc.addRow("Rockets per second:", self.spin_rocket_rate)
        lay_rc.addLayout(form_rc)

        self.tabs.addTab(tab_rockets, "Rockets")

        # ROCKETLAUNCHER TAB
        tab_rl = QWidget()
        lay_rl = QVBoxLayout(tab_rl)
        lay_rl.setSpacing(8)

        self.rl_info = QLabel()
        self.rl_info.setWordWrap(True)
        lay_rl.addWidget(self.rl_info)

        form_rl = QFormLayout()
        self.combo_rl_type = QComboBox()
        self.combo_rl_type.addItems([
            "HST-1 (3 rockets / 3s)",
            "HST-2 (5 rockets / 5s)",
        ])
        self.combo_rl_rocket = QComboBox()
        self.spin_rl_level = QSpinBox()
        self.spin_rl_level.setRange(0, 16)
        form_rl.addRow("Launcher:", self.combo_rl_type)
        form_rl.addRow("Rocket type:", self.combo_rl_rocket)
        form_rl.addRow("Upgrade level:", self.spin_rl_level)
        lay_rl.addLayout(form_rl)

        self.tabs.addTab(tab_rl, "Rocketlauncher")

        # FORMATIONS TAB
        tab_forms = QWidget()
        lay_f = QVBoxLayout(tab_forms)
        lay_f.setSpacing(8)

        self.form_info = QLabel()
        self.form_info.setWordWrap(True)
        lay_f.addWidget(self.form_info)

        self.combo_form = QComboBox()
        self.combo_form.addItems([
            "Turtle (-7.5% all dmg)",
            "Arrow (+20% rocket/RL dmg)",
            "Star (+25% rocket dmg)",
            "Pincer (+5% PvP dmg)",
            "Double Arrow (+30% rocket/RL dmg)",
            "Chevron (+65% rocket/RL dmg)",
            "Heart (-5% all dmg)",
            "Barrier (+5% NPC dmg)",
            "None"
        ])
        self.combo_form.setCurrentText("None")
        lay_f.addWidget(self.combo_form)

        self.tabs.addTab(tab_forms, "Formations")

        # SKILLS TAB
        tab_skills = QWidget()
        lay_sk = QVBoxLayout(tab_skills)
        lay_sk.setSpacing(8)

        self.skills_info = QLabel()
        self.skills_info.setWordWrap(True)
        lay_sk.addWidget(self.skills_info)

        form_sk = QFormLayout()
        self.spin_skill_mt = QSpinBox()
        self.spin_skill_mt.setRange(0, 5)
        self.spin_skill_bh = QSpinBox()
        self.spin_skill_bh.setRange(0, 5)
        self.spin_skill_re = QSpinBox()
        self.spin_skill_re.setRange(0, 5)
        self.spin_skill_sc = QSpinBox()
        self.spin_skill_sc.setRange(0, 5)

        form_sk.addRow("Missile Targeting (0–5):", self.spin_skill_mt)
        form_sk.addRow("Bounty Hunter (0–5):", self.spin_skill_bh)
        form_sk.addRow("Rocket Engineering (0–5):", self.spin_skill_re)
        form_sk.addRow("Saturn Conqueror (0–5):", self.spin_skill_sc)

        lay_sk.addLayout(form_sk)

        self.tabs.addTab(tab_skills, "Skills")

        # Bottom: NPC HP + Results
        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        left_cfg = QFrame()
        left_layout = QFormLayout(left_cfg)
        left_layout.setSpacing(6)
        self.lbl_npc_hp = QLabel("NPC HP (target):")
        self.spin_npc_hp = QSpinBox()
        self.spin_npc_hp.setRange(1_000, 10_000_000)
        self.spin_npc_hp.setSingleStep(10_000)
        self.spin_npc_hp.setValue(500_000)
        left_layout.addRow(self.lbl_npc_hp, self.spin_npc_hp)

        right_result = QFrame()
        right_layout = QVBoxLayout(right_result)
        right_layout.setSpacing(4)
        self.result_title = QLabel()
        self.result_line_laser = QLabel()
        self.result_line_rocket = QLabel()
        self.result_line_rl = QLabel()
        self.result_line_total = QLabel()
        self.result_line_ttk = QLabel()
        self.btn_calc = QPushButton()
        right_layout.addWidget(self.result_title)
        right_layout.addWidget(self.result_line_laser)
        right_layout.addWidget(self.result_line_rocket)
        right_layout.addWidget(self.result_line_rl)
        right_layout.addWidget(self.result_line_total)
        right_layout.addWidget(self.result_line_ttk)
        right_layout.addStretch()
        right_layout.addWidget(self.btn_calc, alignment=Qt.AlignRight)

        bottom.addWidget(left_cfg, 0)
        bottom.addWidget(right_result, 1)

        root.addLayout(bottom)

        self.btn_calc.clicked.connect(self._on_calculate)

        self.set_language(self.language)
        self.set_name_style(self.name_style)

    # ---------- Helper mapping & multipliers ----------

    def _ammo_multiplier(self, ammo_id: str, is_pirate: bool) -> float:
        if ammo_id == "LPC11":
            return 1.0
        if ammo_id == "PCC25":
            return 2.0
        if ammo_id == "PCC50":
            return 3.0
        if ammo_id == "QRB101":
            return 4.0
        if ammo_id == "LSA50":
            return 2.0  # leech ignoriert
        if ammo_id == "RLPC75":
            return 6.0
        if ammo_id == "HSAX":
            return 3.0  # leech ignoriert
        if ammo_id == "LFR4C":
            return 6.0 if is_pirate else 4.0
        return 1.0

    def _skill_mult(self, levels, index):
        if index < 0 or index >= len(levels):
            return 0.0
        return levels[index]

    def _on_calculate(self):
        # ------ Skill multipliers ------
        mt_table = [0, 0.02, 0.04, 0.06, 0.08, 0.10]
        bh_table = [0, 0.02, 0.04, 0.06, 0.08, 0.12]  # aktuell nicht genutzt
        re_table = [0, 0.02, 0.04, 0.06, 0.08, 0.10]
        sc_table = [0, 0.02, 0.04, 0.08, 0.16, 0.25]

        lvl_mt = self.spin_skill_mt.value()
        lvl_bh = self.spin_skill_bh.value()
        lvl_re = self.spin_skill_re.value()
        lvl_sc = self.spin_skill_sc.value()

        missile_targeting = self._skill_mult(mt_table, lvl_mt)
        rocket_eng = self._skill_mult(re_table, lvl_re)
        saturn_conq = self._skill_mult(sc_table, lvl_sc)
        # bounty_hunter = self._skill_mult(bh_table, lvl_bh)  # für PvP, hier ignoriert

        # ------ Formation multipliers ------
        form_text = self.combo_form.currentText()
        dmg_all_mult = 1.0
        rocket_mult = 1.0
        npc_mult = 1.0

        if "Turtle" in form_text:
            dmg_all_mult *= 0.925
        if "Heart" in form_text:
            dmg_all_mult *= 0.95
        if "Arrow" in form_text and "Double" not in form_text:
            rocket_mult *= 1.20
        if "Star" in form_text:
            rocket_mult *= 1.25
        if "Double Arrow" in form_text:
            rocket_mult *= 1.30
        if "Chevron" in form_text:
            rocket_mult *= 1.65
        if "Barrier" in form_text:
            npc_mult *= 1.05
        # Pincer = PvP, ignoriert

        laser_damage_mult = dmg_all_mult * npc_mult * (1.0 + saturn_conq)
        rocket_damage_mult = dmg_all_mult * rocket_mult * (1.0 + rocket_eng)
        rl_damage_mult = dmg_all_mult * rocket_mult * (1.0 + rocket_eng)

        # ------ Lasers ------
        # map display names to internal ids
        if self.name_style == "vanilla":
            laser_map = {
                "LW-3": "LW3",
                "LW-4": "LW4",
                "LW-4U": "LW4U",
                "PR-L": "PRL",
            }
        else:
            laser_map = {
                "LF-3": "LW3",
                "LF-4": "LW4",
                "LF-4U": "LW4U",
                "Prometheus": "PRL",
            }

        # ensure data present
        total_laser_dps = 0.0

        # ammo
        is_pirate = self.chk_pirate.isChecked()
        ammo_idx = self.combo_ammo.currentIndex()
        ammo_id = self.ammo_ids[ammo_idx] if 0 <= ammo_idx < len(self.ammo_ids) else "LPC11"
        ammo_mult = self._ammo_multiplier(ammo_id, is_pirate)

        for combo, spin_count, spin_level in self.laser_groups:
            count = spin_count.value()
            if count <= 0:
                continue
            disp_name = combo.currentText()
            laser_id = laser_map.get(disp_name)
            if not laser_id or laser_id not in self.lasers:
                continue
            info = self.lasers[laser_id]
            base = info["base"]
            level = spin_level.value()
            # Upgrade: +0.5 % pro Level
            base_upgraded = base * (1.0 + 0.005 * level)
            if info["hidden60"]:
                base_upgraded *= 1.6
            group_base = base_upgraded * count  # pro Schuss/Salve

            acc = info["acc"]
            sps = info["sps"]

            dmg_per_shot = group_base * ammo_mult * laser_damage_mult
            dmg_per_hit = dmg_per_shot * acc
            dps = dmg_per_hit * sps

            total_laser_dps += dps

        # ------ Rockets (single) ------
        total_rocket_dps = 0.0
        rocket_key = None
        if self.spin_rocket_rate.value() > 0:
            # map names
            if self.name_style == "vanilla":
                rocket_map = {
                    "SIM-311": "SIM311",
                    "S2S-2026": "S2S2026",
                    "S2S-2021": "S2S2021",
                    "S2S-3030": "S2S3030",
                }
            else:
                rocket_map = {
                    "R-310": "SIM311",
                    "PLT-2026": "S2S2026",
                    "PLT-2021": "S2S2021",
                    "PLT-3030": "S2S3030",
                }
            disp_rc = self.combo_rocket.currentText()
            rocket_key = rocket_map.get(disp_rc)
            if rocket_key and rocket_key in self.rockets:
                info_rc = self.rockets[rocket_key]
                base_rc = info_rc["base"] * rocket_damage_mult
                acc_rc = info_rc["acc"]
                acc_rc_eff = min(1.0, acc_rc * (1.0 + missile_targeting))
                rps = float(self.spin_rocket_rate.value())
                total_rocket_dps = base_rc * acc_rc_eff * rps

        # ------ Rocketlauncher ------
        total_rl_dps = 0.0
        # map RL rocket names
        if self.name_style == "vanilla":
            rl_map = {
                "ECO-10": "ECO10",
                "HRP-01": "HRP01",
                "ERS-100": "ERS100",
            }
        else:
            rl_map = {
                "ECO-10": "ECO10",
                "HSTRM-01": "HRP01",
                "UBR-10": "ERS100",
            }

        disp_rl_rocket = self.combo_rl_rocket.currentText()
        rl_rocket_id = rl_map.get(disp_rl_rocket)
        if rl_rocket_id and rl_rocket_id in self.rl_rockets:
            base_rl = self.rl_rockets[rl_rocket_id]["base"]
            # RL upgrade-level: +0.5 % pro Level
            rl_level = self.spin_rl_level.value()
            base_rl_up = base_rl * (1.0 + 0.005 * rl_level)
            base_rl_up *= rl_damage_mult

            # launcher fire rate
            disp_launcher = self.combo_rl_type.currentText()
            if "HST-1" in disp_launcher:
                rockets_per_salvo = 3
                cooldown = 3.0
            else:
                rockets_per_salvo = 5
                cooldown = 5.0
            rockets_per_second = rockets_per_salvo / cooldown if cooldown > 0 else 0.0
            total_rl_dps = base_rl_up * rockets_per_second

        # ------ Total & TTK ------
        total_dps = total_laser_dps + total_rocket_dps + total_rl_dps
        npc_hp = float(self.spin_npc_hp.value())
        ttk = npc_hp / total_dps if total_dps > 0 else 0.0

        # Output
        if self.language == "de":
            self.result_line_laser.setText(f"Laser DPS: {total_laser_dps:,.0f}".replace(",", "."))
            self.result_line_rocket.setText(f"Raketen DPS: {total_rocket_dps:,.0f}".replace(",", "."))
            self.result_line_rl.setText(f"Rocketlauncher DPS: {total_rl_dps:,.0f}".replace(",", "."))
            self.result_line_total.setText(f"Gesamt DPS: {total_dps:,.0f}".replace(",", "."))
            self.result_line_ttk.setText(f"Geschätzte Zeit bis zum Kill: {ttk:,.1f} Sekunden".replace(",", "."))
        else:
            self.result_line_laser.setText(f"Laser DPS: {total_laser_dps:,.0f}")
            self.result_line_rocket.setText(f"Rocket DPS: {total_rocket_dps:,.0f}")
            self.result_line_rl.setText(f"Rocketlauncher DPS: {total_rl_dps:,.0f}")
            self.result_line_total.setText(f"Total DPS: {total_dps:,.0f}")
            self.result_line_ttk.setText(f"Estimated time to kill: {ttk:,.1f} seconds")

    def set_name_style(self, style: str):
        self.name_style = style

        # Lasers
        for combo, _, _ in self.laser_groups:
            combo.clear()
            if style == "vanilla":
                combo.addItems(["LW-3", "LW-4", "LW-4U", "PR-L"])
            else:
                combo.addItems(["LF-3", "LF-4", "LF-4U", "Prometheus"])

        # Ammo
        self.combo_ammo.clear()
        if style == "vanilla":
            self.combo_ammo.addItems([
                "LPC-11",
                "PCC-25",
                "PCC-50",
                "QRB-101",
                "LSA-50",
                "RLPC-75",
                "HSA-X",
                "L-FR4C",
            ])
        else:
            self.combo_ammo.addItems([
                "LCB-10",
                "MCB-25",
                "MCB-50",
                "UCB-100",
                "SAB-50",
                "RSB-75",
                "CBO-100",
                "L-FR4C",
            ])

        # rockets
        self.combo_rocket.clear()
        if style == "vanilla":
            self.combo_rocket.addItems([
                "SIM-311",
                "S2S-2026",
                "S2S-2021",
                "S2S-3030",
            ])
        else:
            self.combo_rocket.addItems([
                "R-310",
                "PLT-2026",
                "PLT-2021",
                "PLT-3030",
            ])

        # RL rockets
        self.combo_rl_rocket.clear()
        if style == "vanilla":
            self.combo_rl_rocket.addItems([
                "ECO-10",
                "HRP-01",
                "ERS-100",
            ])
        else:
            self.combo_rl_rocket.addItems([
                "ECO-10",
                "HSTRM-01",
                "UBR-10",
            ])

    def set_language(self, lang: str):
        self.language = lang
        if lang == "de":
            self.heading.setText("Schadensrechner")
            self.desc.setText(
                "Berechnet Laser-, Raketen- und Rocketlauncher-DPS basierend auf deinem Setup. "
                "Derzeit wird von einem NPC-Ziel ausgegangen (Saturn Conqueror / Barrier werden berücksichtigt)."
            )
            self.laser_info.setText(
                "Laser-Gruppen: Wähle für jede Gruppe Typ, Anzahl und Upgrade-Level. "
                "Beispiel: Gruppe 1 = 5× LF-3, Gruppe 2 = 10× LF-4."
            )
            self.ammo_info.setText(
                "Munition: Wähle den Munitionstyp. L-FR4C verwendet unterschiedliche Multiplikatoren "
                "gegen Piraten- und andere Ziele."
            )
            self.rc_info.setText(
                "Raketen: Schaden basiert auf Raketen-Typ, Genauigkeit, Missile Targeting und Feuerrate."
            )
            self.rl_info.setText(
                "Rocketlauncher: HST-1/HST-2 mit verschiedenen Raketen und Upgrade-Leveln."
            )
            self.form_info.setText(
                "Formationen beeinflussen Laser-, Raketen- und NPC-Schaden. Pincer wird aktuell ignoriert, "
                "da er nur PvP betrifft."
            )
            self.skills_info.setText(
                "Skilltree: Missile Targeting beeinflusst Raketen-Genauigkeit, Rocket Engineering die Raketen- "
                "und Rocketlauncher-Schaden, Saturn Conqueror den NPC-Laser-Schaden."
            )
            self.lbl_npc_hp.setText("NPC-HP (Ziel):")
            self.result_title.setText("Ergebnisse")
            self.btn_calc.setText("Berechnen")
        else:
            self.heading.setText("Damage Calculator")
            self.desc.setText(
                "Calculates laser, rocket and rocketlauncher DPS based on your setup. "
                "Currently assumes an NPC target (Saturn Conqueror / Barrier are applied)."
            )
            self.laser_info.setText(
                "Laser groups: for each group, choose type, count and upgrade level. "
                "Example: group 1 = 5× LF-3, group 2 = 10× LF-4."
            )
            self.ammo_info.setText(
                "Ammo: choose the ammunition type. L-FR4C uses different multipliers "
                "against pirate vs other targets."
            )
            self.rc_info.setText(
                "Rockets: damage based on rocket type, accuracy, Missile Targeting and fire rate."
            )
            self.rl_info.setText(
                "Rocketlauncher: HST-1/HST-2 with different rockets and upgrade levels."
            )
            self.form_info.setText(
                "Formations affect laser, rocket and NPC damage. Pincer is currently ignored "
                "since it is PvP-only."
            )
            self.skills_info.setText(
                "Skilltree: Missile Targeting affects rocket accuracy, Rocket Engineering boosts "
                "rocket and launcher damage, Saturn Conqueror boosts laser damage vs NPCs."
            )
            self.lbl_npc_hp.setText("NPC HP (target):")
            self.result_title.setText("Results")
            self.btn_calc.setText("Calculate")
