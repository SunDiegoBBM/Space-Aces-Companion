
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
)
from PySide6.QtCore import Qt

from . import models


class FarmingPage(QWidget):
    """
    NPC Farming Guide

    Nutzt den zuletzt berechneten Schaden aus dem Damage Calculator
    (app_state["last_damage_result"]) und bewertet NPCs aus npcs.json.
    """

    def __init__(self, app_state=None, parent=None, name_style=None, **kwargs):
        super().__init__(parent)
        self.app_state = app_state or {}
        self.language = "en"
        self.name_style = name_style or "vanilla"

        # NPCs laden (kann leer sein, falls Datei fehlt)
        self.npcs = models.load_npcs()

        self._init_ui()
        self._update_build_summary()

    # ------------------- UI -------------------

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header
        self.heading = QLabel()
        self.heading.setObjectName("PageTitleLabel")

        self.build_label = QLabel("")
        self.build_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        self.build_label.setWordWrap(True)

        layout.addWidget(self.heading)
        layout.addWidget(self.build_label)

        # Filter & Action row
        controls = QHBoxLayout()
        controls.setSpacing(8)

        self.lbl_map = QLabel("Map:")
        self.cmb_map = QComboBox()
        self.cmb_map.addItem("All maps", "")

        maps_seen = set()
        for npc in self.npcs:
            if npc.map and npc.map not in maps_seen:
                maps_seen.add(npc.map)
        for m in sorted(maps_seen):
            self.cmb_map.addItem(m, m)

        self.btn_calc = QPushButton("Calculate suggestions")
        self.btn_calc.clicked.connect(self.recalculate)

        controls.addWidget(self.lbl_map)
        controls.addWidget(self.cmb_map)
        controls.addStretch()
        controls.addWidget(self.btn_calc)

        layout.addLayout(controls)

        # Table
        box = QGroupBox()
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(8, 8, 8, 8)

        self.table = QTableWidget(0, 7, self)
        self.table.setHorizontalHeaderLabels(
            [
                "NPC",
                "Map",
                "HP + Shield",
                "Uri / kill",
                "TTK (s)",
                "Uri / min",
                "Rating",
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid #333333;
                border-radius: 16px;
                background-color: #05060c;
            }
            QTableWidget {
                background-color: #05060c;
                gridline-color: #222222;
                color: #e0e0e0;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #10121a;
                padding: 4px;
                border: 1px solid #333333;
                color: #cccccc;
            }
        """
        )

        box_layout.addWidget(self.table)
        layout.addWidget(box, 1)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #777777; font-size: 10px;")
        layout.addWidget(self.info_label)

        layout.addStretch()

        self.set_language(self.language)

    # ------------------- Helpers -------------------

    def _get_active_dps(self) -> float:
        if not isinstance(self.app_state, dict):
            return 0.0
        last = self.app_state.get("last_damage_result") or {}
        try:
            return float(last.get("total_dps", 0.0))
        except (TypeError, ValueError):
            return 0.0

    def _update_build_summary(self):
        if not isinstance(self.app_state, dict):
            self.build_label.setText("")
            return

        res = self.app_state.get("last_damage_result") or {}
        state = self.app_state.get("last_damage_state") or {}

        total_dps = res.get("total_dps", 0.0)
        laser_dps = res.get("laser_dps", 0.0)
        rocket_dps = res.get("rocket_dps", 0.0)

        formation = state.get("formation", "NONE")
        booster = int(state.get("damage_booster", 0.0) * 100)

        drones_cfg = state.get("drones", {})
        total_drones = sum(d.get("count", 0) for d in drones_cfg.values())
        havoc = 0
        vandal = 0
        haunt = 0
        for d in drones_cfg.values():
            c = d.get("count", 0)
            design = d.get("design", "NONE")
            if design == "HAVOC":
                havoc += c
            elif design == "VANDAL":
                vandal += c
            elif design == "HAUNTVOC":
                haunt += c

        if total_dps <= 0:
            txt = "No active damage setup imported yet."
        else:
            txt = (
                f"Using last damage setup: total DPS ≈ {total_dps:,.0f} "
                f"(laser: {laser_dps:,.0f}, rockets: {rocket_dps:,.0f}) | "
                f"Formation: {formation}, Booster: +{booster}% | "
                f"Drones: {total_drones} (Havoc: {havoc}, Vandal: {vandal}, Haunt-Voc: {haunt})"
            )

        self.build_label.setText(txt)

    def _rating_for(self, uri_per_min: float, max_uri_per_min: float) -> str:
        if max_uri_per_min <= 0:
            return "-"
        ratio = uri_per_min / max_uri_per_min
        if ratio >= 0.9:
            return "A+"
        if ratio >= 0.75:
            return "A"
        if ratio >= 0.6:
            return "B"
        if ratio >= 0.4:
            return "C"
        if ratio >= 0.2:
            return "D"
        return "F"

    # ------------------- Public API -------------------

    def recalculate(self):
        dps = self._get_active_dps()
        self._update_build_summary()

        if dps <= 0:
            if self.language == "de":
                self.info_label.setText(
                    "Kein gültiges Setup gefunden. Bitte zuerst im Schadensrechner berechnen "
                    "und dann auf 'Use in Farming Guide' klicken."
                )
            else:
                self.info_label.setText(
                    "No valid setup found. Please calculate damage first and click "
                    "'Use in Farming Guide' in the Damage Calculator."
                )
            self.table.setRowCount(0)
            return

        # NPC-Filter
        map_filter = self.cmb_map.currentData()
        filtered_npcs = self.npcs
        if map_filter:
            filtered_npcs = [n for n in filtered_npcs if n.map == map_filter]

        if not filtered_npcs:
            self.table.setRowCount(0)
            if self.language == "de":
                self.info_label.setText("Keine NPCs für diesen Filter gefunden.")
            else:
                self.info_label.setText("No NPCs found for this filter.")
            return

        suggestions = models.suggest_best_npcs(dps, filtered_npcs, top_n=50)

        if not suggestions:
            self.table.setRowCount(0)
            if self.language == "de":
                self.info_label.setText("Mit diesem DPS kann keine sinnvolle Auswertung berechnet werden.")
            else:
                self.info_label.setText("No meaningful ranking could be calculated with this DPS.")
            return

        max_uri_per_min = max(
            (float(s.get("uri_per_hour", 0.0) or 0.0) / 60.0) for s in suggestions
        ) if suggestions else 0.0


        self.table.setRowCount(len(suggestions))
        use_mod = self.name_style == "mod"

        for row, entry in enumerate(suggestions):
            npc = entry["npc"]
            hp = entry["hp"]
            uri = entry["uri"]
            ttk = entry["ttk"]
            uri_per_hour = float(entry.get("uri_per_hour", 0.0) or 0.0)
            uri_per_min = uri_per_hour / 60.0

            display_name = models.get_display_npc_name(npc, "mod" if use_mod else "vanilla")
            rating = self._rating_for(uri_per_min, max_uri_per_min)

            values = [
                display_name,
                npc.map,
                f"{hp:,}",
                f"{uri:,}",
                f"{ttk:.2f}",
                f"{uri_per_min:.2f}",
                rating,
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                if col in (2, 3, 4, 5):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, item)

        if self.language == "de":
            self.info_label.setText(
                "Hinweis: Dies ist eine theoretische Effizienz (kein Reiseweg, perfekte Uptime). "
                "Nutze sie als Orientierung, nicht als absolute Wahrheit."
            )
        else:
            self.info_label.setText(
                "Note: This is a theoretical efficiency (no travel time, perfect uptime). "
                "Use this as a guideline, not an absolute truth."
            )

    def set_language(self, lang: str):
        self.language = lang
        if lang == "de":
            self.heading.setText("NPC-Farming-Guide")
            self.lbl_map.setText("Karte:")
            self.btn_calc.setText("Vorschläge berechnen")
        else:
            self.heading.setText("NPC Farming Guide")
            self.lbl_map.setText("Map:")
            self.btn_calc.setText("Calculate suggestions")

    def set_name_style(self, style: str):
        if style in ("vanilla", "mod"):
            self.name_style = style
            # Tabelle neu zeichnen, falls bereits Daten vorhanden
            if self.table.rowCount() > 0:
                self.recalculate()
