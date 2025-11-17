from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QAbstractItemView,
)
from PySide6.QtCore import Qt

from . import models


class WikiPage(QWidget):
    """
    Wiki page – currently focused on NPCs.

    - Left: searchable NPC table (data from npcs.json via models.load_npcs()).
    - Right: details for the selected NPC.
    - Supports language (EN/DE) and vanilla/mod name styles.
    """

    def __init__(self, name_style: str = "vanilla"):
        super().__init__()
        self.language = "en"
        self.name_style = name_style or "vanilla"
        self.npcs = models.load_npcs()
        # indices into self.npcs that are currently visible in the table
        self.filtered_indices = list(range(len(self.npcs)))
        self._init_ui()
        self.set_language(self.language)
        self._populate_table()

    # ------------------- UI -------------------

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        # Heading + description
        self.heading = QLabel()
        self.heading.setObjectName("PageTitleLabel")
        self.heading.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.desc = QLabel()
        self.desc.setWordWrap(True)

        layout.addWidget(self.heading)
        layout.addWidget(self.desc)

        # Search row
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self.lbl_search = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name or map...")
        self.search_edit.textChanged.connect(self._on_search_changed)

        search_row.addWidget(self.lbl_search)
        search_row.addWidget(self.search_edit, 1)

        layout.addLayout(search_row)

        # Main content: table + details
        content = QHBoxLayout()
        content.setSpacing(10)

        # Table
        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(
            ["NPC", "Map", "HP + Shield", "Uri / kill"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        self.table.setStyleSheet(
            """
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

        content.addWidget(self.table, 3)

        # Detail panel
        self.detail_box = QGroupBox()
        detail_layout = QVBoxLayout(self.detail_box)
        detail_layout.setContentsMargins(8, 8, 8, 8)
        detail_layout.setSpacing(6)

        self.detail_name = QLabel("")
        self.detail_name.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.detail_meta = QLabel("")
        self.detail_meta.setStyleSheet("font-size: 11px; color: #aaaaaa;")
        self.detail_meta.setWordWrap(True)

        self.detail_stats = QLabel("")
        self.detail_stats.setStyleSheet("font-size: 11px; color: #dddddd;")
        self.detail_stats.setWordWrap(True)

        detail_layout.addWidget(self.detail_name)
        detail_layout.addWidget(self.detail_meta)
        detail_layout.addWidget(self.detail_stats)
        detail_layout.addStretch()

        self.detail_box.setTitle("Details")
        self.detail_box.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid #333333;
                border-radius: 12px;
                background-color: #080a12;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #dddddd;
                font-weight: 600;
            }
            """
        )

        content.addWidget(self.detail_box, 2)
        layout.addLayout(content)
        layout.addStretch()

    # ------------------- Data & filtering -------------------

    def _on_search_changed(self, text: str):
        """
        Filter NPC list by name or map (case-insensitive).
        """
        term = (text or "").strip().lower()
        if not term:
            self.filtered_indices = list(range(len(self.npcs)))
        else:
            self.filtered_indices = []
            for idx, npc in enumerate(self.npcs):
                use_mod = self.name_style == "mod"
                name = models.get_display_npc_name(npc, use_mod_names=use_mod)
                map_name = npc.map or ""
                if term in name.lower() or term in map_name.lower():
                    self.filtered_indices.append(idx)
        self._populate_table()

    def _populate_table(self):
        self.table.setRowCount(0)
        if not self.npcs:
            self._clear_details()
            return

        if not self.filtered_indices:
            self._clear_details()
            return

        use_mod = self.name_style == "mod"

        self.table.setRowCount(len(self.filtered_indices))
        for row, npc_index in enumerate(self.filtered_indices):
            npc = self.npcs[npc_index]
            name = models.get_display_npc_name(npc, use_mod_names=use_mod)

            hp_total = npc.total_hp
            uri_raw = npc.reward_uri or 0
            try:
                uri_val = int(uri_raw)
            except (TypeError, ValueError):
                uri_val = 0

            values = [
                name,
                npc.map,
                f"{hp_total:,}",
                f"{uri_val:,}",
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                if col in (2, 3):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                # store original npc index for retrieval
                item.setData(Qt.UserRole, npc_index)
                self.table.setItem(row, col, item)

        # select the first row by default
        self.table.selectRow(0)
        first_index = self.table.item(0, 0).data(Qt.UserRole)
        if first_index is not None and 0 <= first_index < len(self.npcs):
            self._update_details(self.npcs[first_index])

    def _clear_details(self):
        self.detail_name.setText("")
        self.detail_meta.setText("")
        self.detail_stats.setText("")

    def _on_selection_changed(self):
        selected = self.table.selectedItems()
        if not selected:
            self._clear_details()
            return
        # any item in the selected row has the npc index in UserRole
        item = selected[0]
        npc_index = item.data(Qt.UserRole)
        if npc_index is None or not (0 <= npc_index < len(self.npcs)):
            self._clear_details()
            return
        npc = self.npcs[npc_index]
        self._update_details(npc)

    def _update_details(self, npc: models.NPC):
        use_mod = self.name_style == "mod"
        display_name = models.get_display_npc_name(npc, use_mod_names=use_mod)

        hp_total = npc.total_hp
        shields = npc.shields
        hp = npc.health

        uri_raw = npc.reward_uri or 0
        creds_raw = npc.reward_credits or 0
        try:
            uri = int(uri_raw)
        except (TypeError, ValueError):
            uri = 0
        try:
            creds = int(creds_raw)
        except (TypeError, ValueError):
            creds = 0

        self.detail_name.setText(display_name)

        if self.language == "de":
            meta = f"Karte: {npc.map or '-'} | ID: {npc.id}"
            stats = (
                f"HP: {hp:,} | Schild: {shields:,} | Gesamt-HP: {hp_total:,}\n"
                f"Belohnung: {uri:,} Uri, {creds:,} Credits"
            )
        else:
            meta = f"Map: {npc.map or '-'} | ID: {npc.id}"
            stats = (
                f"HP: {hp:,} | Shield: {shields:,} | Total HP: {hp_total:,}\n"
                f"Reward: {uri:,} Uri, {creds:,} Credits"
            )

        self.detail_meta.setText(meta)
        self.detail_stats.setText(stats)

    # ------------------- Public API -------------------

    def set_language(self, lang: str):
        self.language = lang
        if lang == "de":
            self.heading.setText("Wiki – NPC-Übersicht")
            self.desc.setText("Alle bekannten NPCs mit HP, Schild, Uri-Belohnung und Karte. "
                              "Mit der Suche kannst du nach Namen oder Karten filtern.")
            self.lbl_search.setText("Suche:")
            self.search_edit.setPlaceholderText("Nach Name oder Karte suchen...")
            self.detail_box.setTitle("Details")
        else:
            self.heading.setText("Wiki – NPC Overview")
            self.desc.setText("All known NPCs with HP, shields, Uri reward and map. "
                              "Use the search to filter by name or map.")
            self.lbl_search.setText("Search:")
            self.search_edit.setPlaceholderText("Search by name or map...")
            self.detail_box.setTitle("Details")

        # refresh details text in the new language
        selected = self.table.selectedItems()
        if selected:
            npc_index = selected[0].data(Qt.UserRole)
            if npc_index is not None and 0 <= npc_index < len(self.npcs):
                self._update_details(self.npcs[npc_index])

    def set_name_style(self, style: str):
        if style not in ("vanilla", "mod"):
            return
        self.name_style = style
        # keep filter term but repopulate table with new display names
        self._populate_table()
