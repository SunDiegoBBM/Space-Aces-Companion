
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QFormLayout, QComboBox, QSpinBox, QPushButton,
    QCheckBox, QGroupBox, QGridLayout, QFrame
)
from PySide6.QtCore import Qt

from . import models


class DamagePage(QWidget):
    """
    Damage Calculator page for Space Aces Companion.

    Copy to: app/sac_pages/damage_page.py
    MainWindow import:
        from sac_pages.damage_page import DamagePage
    """

    def __init__(self, app_state=None, parent=None, name_style=None, **kwargs):
        super().__init__(parent)
        self.app_state = app_state
        self.name_style = name_style

        self.state = {
            "laser_groups": [
                {"type": "LW3", "count": 10, "upgrade": 0},
                {"type": "LW4", "count": 0, "upgrade": 0},
                {"type": "LW4U", "count": 0, "upgrade": 0},
            ],
            "ammo": "LPC11",
            "target_is_pirate": False,
            "npc_hp": 250000,
            "drones": {
                "IRIS": {"count": 8, "level": 16, "design": "NONE", "lasers_per_drone": 2},
                "APIS": {"count": 0, "level": 16, "design": "NONE", "lasers_per_drone": 2},
                "ZEUS": {"count": 0, "level": 16, "design": "NONE", "lasers_per_drone": 2},
            },
            # aggregated: how many of each laser type sit on drones
            "lasers_on_drones_by_type": {
                "LW3": 0,
                "LW4": 0,
                "LW4U": 0,
                "PRL": 0,
            },
            "skills": {
                "missile_targeting": 0,
                "rocket_engineering": 0,
                "saturn_conqueror": 0,
                "bounty_hunter": 0,
            },
            "formation": "NONE",
            "damage_booster": 0.0,  # 0, 0.10, 0.20, 0.25
            "language": "EN",
            "rockets": {
                "type": "NONE",
            },
            "rocket_launcher": {
                "launcher_type": "NONE",
                "rocket_type": "ECO10",
                "target_is_saturn": False,
            },
        }

        self._build_ui()
        self._update_drone_slots_info()
        self.recalculate()

    # ------------------- UI shell -------------------

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title_row = QHBoxLayout()
        lbl_title = QLabel("Damage Calculator")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: 600;")
        title_row.addWidget(lbl_title)
        title_row.addStretch()
        lbl_sub = QLabel("Lasers • Drones • Ammo • Rockets • Modifiers")
        lbl_sub.setStyleSheet("font-size: 11px; color: #bbbbbb;")
        title_row.addWidget(lbl_sub)
        root.addLayout(title_row)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #333333;")
        root.addWidget(line)

        content = QHBoxLayout()
        content.setSpacing(12)
        root.addLayout(content, 1)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setStyleSheet(self._tab_stylesheet())
        content.addWidget(self.tabs, 3)

        self.results_box = self._create_results_box()
        content.addWidget(self.results_box, 2)

        self._build_lasers_tab()
        self._build_drones_tab()
        self._build_ammo_rockets_tab()
        self._build_modifiers_tab()

    def _tab_stylesheet(self) -> str:
        return """
        QTabWidget::pane {
            border: 1px solid #333333;
            border-radius: 10px;
            background: #111318;
        }
        QTabBar::tab {
            background: #181b22;
            color: #d0d0d0;
            padding: 6px 14px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            margin-right: 2px;
            font-size: 12px;
        }
        QTabBar::tab:selected {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #3a5bff,
                stop:0.5 #c93aff,
                stop:1 #3affd2
            );
            color: #ffffff;
        }
        QTabBar::tab:hover {
            background: #222532;
        }
        """

    def _wrap_card(self, inner_layout, title: str) -> QGroupBox:
        box = QGroupBox(title)
        box.setLayout(inner_layout)
        box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #333333;
                border-radius: 12px;
                margin-top: 10px;
                padding: 8px 10px 10px 10px;
                font-weight: 600;
                background-color: #101018;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0px 4px;
                color: #dddddd;
            }
        """)
        return box

    def _create_results_box(self) -> QGroupBox:
        lay = QVBoxLayout()
        lay.setSpacing(8)

        self.lbl_laser_dps = QLabel("Laser DPS: –")
        self.lbl_rocket_dps = QLabel("Rocket DPS: –")
        self.lbl_total_dps = QLabel("Total DPS: –")
        self.lbl_ttk = QLabel("Estimated TTK: –")

        for lbl in (self.lbl_laser_dps, self.lbl_rocket_dps, self.lbl_total_dps):
            lbl.setStyleSheet("font-size: 15px;")
        self.lbl_ttk.setStyleSheet("font-size: 13px; color: #bbbbbb;")

        lay.addWidget(self.lbl_laser_dps)
        lay.addWidget(self.lbl_rocket_dps)
        lay.addWidget(self.lbl_total_dps)
        lay.addSpacing(4)
        lay.addWidget(self.lbl_ttk)

        lay.addSpacing(10)
        self.details_label = QLabel("")
        self.details_label.setStyleSheet("font-size: 11px; color: #888888;")
        self.details_label.setWordWrap(True)
        lay.addWidget(self.details_label)

        lay.addStretch()

        btn_use = QPushButton("Use in Farming Guide")
        btn_use.clicked.connect(self._go_to_farming_guide)
        btn_use.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border-radius: 6px;
                background-color: #4455aa;
                color: #ffffff;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5566cc;
            }
        """)

        btn = QPushButton("Recalculate")
        btn.clicked.connect(self.recalculate)
        btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border-radius: 6px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3a5bff,
                    stop:0.5 #c93aff,
                    stop:1 #3affd2
                );
                color: #ffffff;
                font-weight: 600;
            }
        """)

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(btn_use)
        row.addWidget(btn)

        lay.addLayout(row)

        box = QGroupBox("Results")
        box.setLayout(lay)
        box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #333333;
                border-radius: 16px;
                background-color: #05060c;
                margin-top: 8px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                color: #dddddd;
            }
        """)
        return box

    

    # ------------------- Farming Guide integration -------------------

    def _go_to_farming_guide(self):
        """
        Speichert aktuelles Ergebnis im app_state und wechselt zur Farming-Seite,
        falls das MainWindow eine open_farming_guide()-Methode besitzt.
        """
        # Stelle sicher, dass das Ergebnis aktuell ist
        result = models.calculate_damage_overview(self.state)

        if self.app_state is not None:
            self.app_state["last_damage_state"] = dict(self.state)
            self.app_state["last_damage_result"] = dict(result)

        parent = self.parent()
        # Nach oben laufen, bis ein Objekt mit open_farming_guide gefunden wird
        visited = set()
        while parent is not None and id(parent) not in visited:
            visited.add(id(parent))
            if hasattr(parent, "open_farming_guide"):
                try:
                    parent.open_farming_guide()
                except TypeError:
                    # Falls die Methode ein Argument erwartet, DPS übergeben
                    parent.open_farming_guide(result.get("total_dps", 0.0))
                break
            parent = parent.parent()


    # ------------------- Tabs -------------------

    def _build_lasers_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)

        headers = ["Group", "Laser type", "Count", "Upgrade level"]
        for col, text in enumerate(headers):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: 600; color: #dddddd;")
            grid.addWidget(lbl, 0, col)

        self.laser_type_boxes = []
        self.laser_count_boxes = []
        self.laser_upgrade_boxes = []

        for row in range(3):
            row_index = row + 1
            grid.addWidget(QLabel(f"Group {row_index}"), row_index, 0)

            cmb = QComboBox()
            for lid, ldef in models.LASERS.items():
                cmb.addItem(ldef["name_en"], userData=lid)
            cmb.setCurrentIndex(row)  # LW3, LW4, LW4U
            cmb.currentIndexChanged.connect(self._on_laser_group_changed)
            self.laser_type_boxes.append(cmb)
            grid.addWidget(cmb, row_index, 1)

            spn_c = QSpinBox()
            spn_c.setRange(0, 50)
            spn_c.setValue(self.state["laser_groups"][row]["count"])
            spn_c.valueChanged.connect(self._on_laser_group_changed)
            self.laser_count_boxes.append(spn_c)
            grid.addWidget(spn_c, row_index, 2)

            spn_u = QSpinBox()
            spn_u.setRange(0, 16)
            spn_u.setValue(self.state["laser_groups"][row]["upgrade"])
            spn_u.valueChanged.connect(self._on_laser_group_changed)
            self.laser_upgrade_boxes.append(spn_u)
            grid.addWidget(spn_u, row_index, 3)

        layout.addWidget(self._wrap_card(grid, "Lasers on ship"))

        hp_row = QHBoxLayout()
        hp_row.addWidget(QLabel("NPC HP for TTK:"))
        self.spn_npc_hp = QSpinBox()
        self.spn_npc_hp.setRange(1000, 50000000)
        self.spn_npc_hp.setSingleStep(10000)
        self.spn_npc_hp.setValue(self.state["npc_hp"])
        self.spn_npc_hp.valueChanged.connect(self._on_npc_hp_changed)
        hp_row.addWidget(self.spn_npc_hp)
        hp_row.addStretch()
        layout.addLayout(hp_row)

        layout.addStretch()
        self.tabs.addTab(w, "Lasers")

    def _build_drones_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        headers = ["Drone", "Count", "Level", "Design"]
        for col, text in enumerate(headers):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: 600; color: #dddddd;")
            grid.addWidget(lbl, 0, col)

        self.drone_controls = {}
        row = 1
        for drone_id, drone_def in models.DRONES.items():
            grid.addWidget(QLabel(drone_def["name_en"]), row, 0)

            spn_count = QSpinBox()
            spn_count.setRange(0, drone_def["max_count"])
            spn_count.setValue(self.state["drones"][drone_id]["count"])
            spn_count.valueChanged.connect(self._on_drones_changed)
            grid.addWidget(spn_count, row, 1)

            spn_level = QSpinBox()
            spn_level.setRange(1, 16)
            spn_level.setValue(self.state["drones"][drone_id]["level"])
            spn_level.valueChanged.connect(self._on_drones_changed)
            grid.addWidget(spn_level, row, 2)

            cmb_design = QComboBox()
            for did, ddef in models.DRONE_DESIGNS.items():
                cmb_design.addItem(ddef["name_en"], userData=did)
            cmb_design.setCurrentIndex(0)
            cmb_design.currentIndexChanged.connect(self._on_drones_changed)
            grid.addWidget(cmb_design, row, 3)

            self.drone_controls[drone_id] = {
                "count": spn_count,
                "level": spn_level,
                "design": cmb_design,
            }

            row += 1

        layout.addWidget(self._wrap_card(grid, "Drones and designs"))

        # aggregated lasers on drones by type – table-like (Variant B)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.spn_lw3_on_drones = QSpinBox()
        self.spn_lw3_on_drones.setRange(0, 64)
        self.spn_lw3_on_drones.setValue(self.state["lasers_on_drones_by_type"]["LW3"])
        self.spn_lw3_on_drones.valueChanged.connect(self._on_lasers_on_drones_changed)
        form.addRow("LW-3 (LF-3) on drones:", self.spn_lw3_on_drones)

        self.spn_lw4_on_drones = QSpinBox()
        self.spn_lw4_on_drones.setRange(0, 64)
        self.spn_lw4_on_drones.setValue(self.state["lasers_on_drones_by_type"]["LW4"])
        self.spn_lw4_on_drones.valueChanged.connect(self._on_lasers_on_drones_changed)
        form.addRow("LW-4 (LF-4) on drones:", self.spn_lw4_on_drones)

        self.spn_lw4u_on_drones = QSpinBox()
        self.spn_lw4u_on_drones.setRange(0, 64)
        self.spn_lw4u_on_drones.setValue(self.state["lasers_on_drones_by_type"]["LW4U"])
        self.spn_lw4u_on_drones.valueChanged.connect(self._on_lasers_on_drones_changed)
        form.addRow("LW-4U (LF-4U) on drones:", self.spn_lw4u_on_drones)

        self.spn_prl_on_drones = QSpinBox()
        self.spn_prl_on_drones.setRange(0, 64)
        self.spn_prl_on_drones.setValue(self.state["lasers_on_drones_by_type"]["PRL"])
        self.spn_prl_on_drones.valueChanged.connect(self._on_lasers_on_drones_changed)
        form.addRow("PR-L (Prometheus) on drones:", self.spn_prl_on_drones)

        inner = QVBoxLayout()
        inner.setSpacing(6)
        inner.addLayout(form)

        self.lbl_drone_slots_info = QLabel("")
        self.lbl_drone_slots_info.setStyleSheet("font-size: 11px; color: #aaaaaa;")
        inner.addWidget(self.lbl_drone_slots_info)

        layout.addWidget(self._wrap_card(inner, "Drone lasers (total)"))

        layout.addStretch()
        self.tabs.addTab(w, "Drones")

    def _build_ammo_rockets_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        form_ammo = QFormLayout()
        form_ammo.setLabelAlignment(Qt.AlignRight)

        self.cmb_ammo = QComboBox()
        for aid, adef in models.AMMO.items():
            self.cmb_ammo.addItem(adef["name_en"], userData=aid)
        self.cmb_ammo.currentIndexChanged.connect(self._on_ammo_changed)
        form_ammo.addRow("Laser ammo:", self.cmb_ammo)

        layout.addWidget(self._wrap_card(form_ammo, "Laser ammo"))

        self.chk_pirate = QCheckBox("Target is Pirate faction (for L-FR4C)")
        self.chk_pirate.stateChanged.connect(self._on_target_flags_changed)
        layout.addWidget(self.chk_pirate)

        form_rockets = QFormLayout()
        form_rockets.setLabelAlignment(Qt.AlignRight)

        self.cmb_rocket = QComboBox()
        for rid, rdef in models.ROCKETS.items():
            self.cmb_rocket.addItem(rdef["name_en"], userData=rid)
        self.cmb_rocket.currentIndexChanged.connect(self._on_rocket_changed)
        form_rockets.addRow("Standard rocket:", self.cmb_rocket)

        self.cmb_launcher = QComboBox()
        for lid, ldef in models.ROCKET_LAUNCHERS.items():
            self.cmb_launcher.addItem(ldef["name_en"], userData=lid)
        self.cmb_launcher.currentIndexChanged.connect(self._on_launcher_changed)
        form_rockets.addRow("Rocket launcher:", self.cmb_launcher)

        self.cmb_launcher_rocket = QComboBox()
        for rrid, rrdef in models.RL_ROCKETS.items():
            self.cmb_launcher_rocket.addItem(rrdef["name_en"], userData=rrid)
        self.cmb_launcher_rocket.currentIndexChanged.connect(self._on_launcher_rocket_changed)
        form_rockets.addRow("Launcher rocket:", self.cmb_launcher_rocket)

        self.chk_saturn = QCheckBox("Target is Saturn faction (for ERS-100)")
        self.chk_saturn.stateChanged.connect(self._on_saturn_target_changed)

        layout.addWidget(self._wrap_card(form_rockets, "Rockets"))
        layout.addWidget(self.chk_saturn)

        layout.addStretch()
        self.tabs.addTab(w, "Ammo & Rockets")

    def _build_modifiers_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        form_form = QFormLayout()
        form_form.setLabelAlignment(Qt.AlignRight)
        self.cmb_formation = QComboBox()
        for fid, fdef in models.FORMATIONS.items():
            self.cmb_formation.addItem(fdef["name_en"], userData=fid)
        self.cmb_formation.currentIndexChanged.connect(self._on_formation_changed)
        form_form.addRow("Drone formation:", self.cmb_formation)
        layout.addWidget(self._wrap_card(form_form, "Formation"))

        booster_form = QFormLayout()
        booster_form.setLabelAlignment(Qt.AlignRight)
        self.cmb_booster = QComboBox()
        self.cmb_booster.addItem("None", userData=0.0)
        self.cmb_booster.addItem("10% damage booster", userData=0.10)
        self.cmb_booster.addItem("20% damage booster", userData=0.20)
        self.cmb_booster.addItem("25% damage booster", userData=0.25)
        self.cmb_booster.currentIndexChanged.connect(self._on_booster_changed)
        booster_form.addRow("Damage booster:", self.cmb_booster)
        layout.addWidget(self._wrap_card(booster_form, "Boosters"))

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        labels = [
            ("Saturn Conqueror (NPC lasers)", "saturn_conqueror"),
            ("Bounty Hunter (PvP lasers)", "bounty_hunter"),
            ("Rocket Engineering", "rocket_engineering"),
            ("Missile Targeting", "missile_targeting"),
        ]

        self.skill_spinboxes = {}
        for row, (label, key) in enumerate(labels):
            grid.addWidget(QLabel(label), row, 0)
            spn = QSpinBox()
            spn.setRange(0, 5)
            spn.valueChanged.connect(self._on_skills_changed)
            grid.addWidget(spn, row, 1)
            self.skill_spinboxes[key] = spn

        layout.addWidget(self._wrap_card(grid, "Skill tree"))
        layout.addStretch()

        self.tabs.addTab(w, "Modifiers")

    # ------------------- State handlers -------------------

    def _on_laser_group_changed(self):
        for idx in range(3):
            self.state["laser_groups"][idx]["type"] = self.laser_type_boxes[idx].currentData()
            self.state["laser_groups"][idx]["count"] = self.laser_count_boxes[idx].value()
            self.state["laser_groups"][idx]["upgrade"] = self.laser_upgrade_boxes[idx].value()
        self.recalculate()

    def _on_npc_hp_changed(self, value: int):
        self.state["npc_hp"] = value
        self.recalculate()

    def _on_drones_changed(self):
        for drone_id, ctrls in self.drone_controls.items():
            self.state["drones"][drone_id]["count"] = ctrls["count"].value()
            self.state["drones"][drone_id]["level"] = ctrls["level"].value()
            self.state["drones"][drone_id]["design"] = ctrls["design"].currentData()
        self._update_drone_slots_info()
        self.recalculate()

    def _on_lasers_on_drones_changed(self, _value: int):
        self.state["lasers_on_drones_by_type"]["LW3"] = self.spn_lw3_on_drones.value()
        self.state["lasers_on_drones_by_type"]["LW4"] = self.spn_lw4_on_drones.value()
        self.state["lasers_on_drones_by_type"]["LW4U"] = self.spn_lw4u_on_drones.value()
        self.state["lasers_on_drones_by_type"]["PRL"] = self.spn_prl_on_drones.value()
        self._update_drone_slots_info()
        self.recalculate()

    def _update_drone_slots_info(self):
        """
        Update label that shows how many drone laser slots are used vs. available.
        """
        if not hasattr(self, "lbl_drone_slots_info"):
            return

        drones_cfg = self.state.get("drones", {})
        total_slots = 0
        for drone_id, d in drones_cfg.items():
            drone_def = models.DRONES.get(drone_id)
            if not drone_def:
                continue
            count = int(d.get("count", 0) or 0)
            total_slots += count * int(drone_def.get("max_lasers", 0) or 0)

        used_slots = sum(int(v or 0) for v in self.state.get("lasers_on_drones_by_type", {}).values())

        text = f"Drone laser slots used: {used_slots} / {total_slots}"
        if total_slots > 0:
            if used_slots > total_slots:
                text += " (too many – some lasers will be ignored in the calculation)"
            elif used_slots < total_slots:
                text += " (free slots remaining)"
            else:
                text += " (all slots used)"

        self.lbl_drone_slots_info.setText(text)


    def _on_ammo_changed(self, _idx: int):
        self.state["ammo"] = self.cmb_ammo.currentData()
        self.recalculate()

    def _on_target_flags_changed(self, _state: int):
        self.state["target_is_pirate"] = self.chk_pirate.isChecked()
        self.recalculate()

    def _on_rocket_changed(self, _idx: int):
        self.state["rockets"]["type"] = self.cmb_rocket.currentData()
        self.recalculate()

    def _on_launcher_changed(self, _idx: int):
        self.state["rocket_launcher"]["launcher_type"] = self.cmb_launcher.currentData()
        self.recalculate()

    def _on_launcher_rocket_changed(self, _idx: int):
        self.state["rocket_launcher"]["rocket_type"] = self.cmb_launcher_rocket.currentData()
        self.recalculate()

    def _on_saturn_target_changed(self, _state: int):
        self.state["rocket_launcher"]["target_is_saturn"] = self.chk_saturn.isChecked()
        self.recalculate()

    def _on_formation_changed(self, _idx: int):
        self.state["formation"] = self.cmb_formation.currentData()
        self.recalculate()

    def _on_booster_changed(self, _idx: int):
        self.state["damage_booster"] = float(self.cmb_booster.currentData())
        self.recalculate()

    def _on_skills_changed(self):
        for key, spn in self.skill_spinboxes.items():
            self.state["skills"][key] = spn.value()
        self.recalculate()

    # ------------------- Calculation -------------------

    
    def recalculate(self):
        result = models.calculate_damage_overview(self.state)

        # Save last result for Farming Guide
        if self.app_state is not None:
            self.app_state["last_damage_state"] = dict(self.state)
            self.app_state["last_damage_result"] = dict(result)

        self.lbl_laser_dps.setText(f"Laser DPS: {result['laser_dps']:.0f}")
        self.lbl_rocket_dps.setText(f"Rocket DPS: {result['rocket_dps']:.0f}")
        self.lbl_total_dps.setText(f"Total DPS: {result['total_dps']:.0f}")

        if result["ttk_seconds"] > 0:
            self.lbl_ttk.setText(
                f"Estimated TTK vs NPC ({self.state['npc_hp']:,} HP): {result['ttk_seconds']:.1f} s"
            )
        else:
            self.lbl_ttk.setText("Estimated TTK: – (no damage)")

        details = []
        details.append(f"Effective laser multiplier (drones + fo...rmation + skills + booster): x{result['laser_multiplier']:.3f}")
        details.append(f"Lasers on drones: {result['lasers_on_drones']} / {result['total_lasers']} (approx.)")
        details.append(f"Drones contributing to damage: {result['drone_count']}")
        details.append(f"Rocket DPS contribution: {result['rocket_dps']:.0f}")
        details.append(f"Damage booster: {int(self.state['damage_booster'] * 100)} %")
        self.details_label.setText("\n".join(details))
