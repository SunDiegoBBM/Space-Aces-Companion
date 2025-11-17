from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QPushButton, QLabel, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
import sys

from sac_pages.wiki_page import WikiPage
from sac_pages.damage_page import DamagePage
from sac_pages.quests_page import QuestsPage
from sac_pages.farming_page import FarmingPage
from sac_pages.settings_page import SettingsPage
from update_checker import check_for_update
from version import APP_VERSION


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.language = "en"
        self.rgb_enabled = True
        self.name_style = "vanilla"  # or "mod"
        self.app_state = {}

        self._init_translations()
        self._init_ui()
        self._apply_style()
        self._apply_language()

    def _init_translations(self):
        self.translations = {
            "en": {
                "window_title": "Space Aces Companion",
                "header_title": "Space Aces Companion",
                "header_subtitle": "Tools, data and planning for your Space Aces journey.",
                "nav_title": "Navigation",
                "nav_wiki": "Wiki",
                "nav_damage": "Damage Calculator",
                "nav_quests": "Quest Helper",
                "nav_farming": "NPC Farming Guide",
                "nav_settings": "Settings",
                "footer_app": "Space Aces <3",
                "footer_dev": "Dev: SunDiegoBBM",
            },
            "de": {
                "window_title": "Space Aces Companion",
                "header_title": "Space Aces Companion",
                "header_subtitle": "Tools, Daten und Planung für deine Space Aces Reise.",
                "nav_title": "Navigation",
                "nav_wiki": "Wiki",
                "nav_damage": "Schadensrechner",
                "nav_quests": "Quest-Hilfe",
                "nav_farming": "NPC-Farming-Guide",
                "nav_settings": "Einstellungen",
                "footer_app": "Space Aces <3",
                "footer_dev": "Dev: SunDiegoBBM",
            },
        }

    def _init_ui(self):
        self.setWindowTitle("Space Aces Companion")
        self.resize(1100, 650)

        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(10)

        # Header
        header = QFrame()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel")
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("SubtitleLabel")

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)

        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # Navigation
        nav_panel = QFrame()
        nav_panel.setObjectName("NavPanel")
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(14, 14, 14, 14)
        nav_layout.setSpacing(10)

        self.nav_title_label = QLabel()
        self.nav_title_label.setObjectName("NavTitleLabel")

        self.btn_wiki = QPushButton()
        self.btn_damage = QPushButton()
        self.btn_quests = QPushButton()
        self.btn_farming = QPushButton()
        self.btn_settings = QPushButton()

        for btn in (self.btn_wiki, self.btn_damage, self.btn_quests, self.btn_farming, self.btn_settings):
            btn.setObjectName("NavButton")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(40)

        self.btn_wiki.clicked.connect(lambda: self._switch_page(0, "wiki"))
        self.btn_damage.clicked.connect(lambda: self._switch_page(1, "damage"))
        self.btn_quests.clicked.connect(lambda: self._switch_page(2, "quests"))
        self.btn_farming.clicked.connect(lambda: self._switch_page(3, "farming"))
        self.btn_settings.clicked.connect(lambda: self._switch_page(4, "settings"))

        nav_layout.addWidget(self.nav_title_label)
        nav_layout.addSpacing(6)
        nav_layout.addWidget(self.btn_wiki)
        nav_layout.addWidget(self.btn_damage)
        nav_layout.addWidget(self.btn_quests)
        nav_layout.addWidget(self.btn_farming)
        nav_layout.addWidget(self.btn_settings)
        nav_layout.addStretch()

        # Content panel
        content_panel = QFrame()
        content_panel.setObjectName("ContentPanel")
        content_panel_layout = QVBoxLayout(content_panel)
        content_panel_layout.setContentsMargins(18, 18, 18, 18)
        content_panel_layout.setSpacing(8)

        self.page_title = QLabel()
        self.page_title.setObjectName("PageTitleLabel")

        self.stack = QStackedWidget()
        self.page_wiki = WikiPage()
        self.page_damage = DamagePage(app_state=self.app_state, name_style=self.name_style)
        self.page_quests = QuestsPage()
        self.page_farm = FarmingPage(app_state=self.app_state, name_style=self.name_style)
        self.page_settings = SettingsPage(
            on_language_change=self.set_language,
            on_rgb_toggle=self.set_rgb_enabled,
            on_name_style_change=self.set_name_style,
        )

        self.stack.addWidget(self.page_wiki)
        self.stack.addWidget(self.page_damage)
        self.stack.addWidget(self.page_quests)
        self.stack.addWidget(self.page_farm)
        self.stack.addWidget(self.page_settings)

        # Footer inside content panel
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(10)
        footer_layout.addStretch()
        self.footer_app_label = QLabel()
        self.footer_app_label.setObjectName("FooterLabel")
        self.footer_dev_label = QLabel()
        self.footer_dev_label.setObjectName("FooterLabel")
        footer_layout.addWidget(self.footer_app_label)
        footer_layout.addWidget(self.footer_dev_label)

        content_panel_layout.addWidget(self.page_title)
        content_panel_layout.addWidget(self.stack, 1)
        content_panel_layout.addLayout(footer_layout)

        content_layout.addWidget(nav_panel, 0)
        content_layout.addWidget(content_panel, 1)

        main_layout.addWidget(header)
        main_layout.addLayout(content_layout)

        self.setCentralWidget(central)

        self._switch_page(1, "damage")  # open damage by default

    def _switch_page(self, index: int, key: str):
        self.stack.setCurrentIndex(index)

        titles = {
            "wiki": {"en": "Wiki", "de": "Wiki"},
            "damage": {"en": "Damage Calculator", "de": "Schadensrechner"},
            "quests": {"en": "Quest Helper", "de": "Quest-Hilfe"},
            "farming": {"en": "NPC Farming Guide", "de": "NPC-Farming-Guide"},
            "settings": {"en": "Settings", "de": "Einstellungen"},
        }
        self.page_title.setText(titles.get(key, {}).get(self.language, key))

        buttons = [self.btn_wiki, self.btn_damage, self.btn_quests, self.btn_farming, self.btn_settings]
        for i, btn in enumerate(buttons):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def set_language(self, lang: str):
        if lang not in self.translations:
            return
        self.language = lang
        self._apply_language()
        if hasattr(self.page_damage, "set_language"):
            self.page_damage.set_language(lang)
        if hasattr(self.page_wiki, "set_language"):
            self.page_wiki.set_language(lang)
        if hasattr(self.page_quests, "set_language"):
            self.page_quests.set_language(lang)
        if hasattr(self.page_farm, "set_language"):
            self.page_farm.set_language(lang)
        if hasattr(self.page_settings, "set_language"):
            self.page_settings.set_language(lang)

    def set_rgb_enabled(self, enabled: bool):
        self.rgb_enabled = enabled
        self._apply_style()

    def set_name_style(self, style: str):
        if style not in ("vanilla", "mod"):
            return
        self.name_style = style
        if hasattr(self.page_damage, "set_name_style"):
            self.page_damage.set_name_style(style)
        if hasattr(self.page_farm, "set_name_style"):
            self.page_farm.set_name_style(style)

    def _apply_language(self):
        tr = self.translations[self.language]
        self.setWindowTitle(tr["window_title"])
        self.title_label.setText(tr["header_title"])
        self.subtitle_label.setText(tr["header_subtitle"])
        self.nav_title_label.setText(tr["nav_title"])
        self.btn_wiki.setText(tr["nav_wiki"])
        self.btn_damage.setText(tr["nav_damage"])
        self.btn_quests.setText(tr["nav_quests"])
        self.btn_farming.setText(tr["nav_farming"])
        self.btn_settings.setText(tr["nav_settings"])
        self.footer_app_label.setText(tr["footer_app"])
        self.footer_dev_label.setText(tr["footer_dev"])



    def open_farming_guide(self, dps: float | None = None):
        """
        Wird vom Damage Calculator aufgerufen, um direkt in den Farming-Guide
        zu springen. Optional kann ein DPS-Wert übergeben werden, der im
        app_state abgelegt wird.
        """
        if dps is not None:
            if isinstance(self.app_state, dict):
                last = self.app_state.get("last_damage_result") or {}
                last["total_dps"] = float(dps)
                self.app_state["last_damage_result"] = last

        # auf Farming-Seite umschalten
        self._switch_page(3, "farming")

        # Farming-Page neu berechnen lassen
        if hasattr(self.page_farm, "recalculate"):
            try:
                self.page_farm.recalculate()
            except TypeError:
                # alte Signatur ohne Parameter
                self.page_farm.recalculate()
    def _apply_style(self):
        if self.rgb_enabled:
            stylesheet = """
            QMainWindow {
                background-color: #040616;
            }

            #TitleLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: 700;
            }

            #SubtitleLabel {
                color: #9fa4c9;
                font-size: 12px;
            }

            #NavTitleLabel {
                color: #e0e3ff;
                font-size: 13px;
                font-weight: 600;
            }

            #PageTitleLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 6px;
            }

            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            #NavPanel {
                background-color: #090f20;
                border-radius: 14px;
                border: 1px solid rgba(120, 150, 255, 0.45);
            }

            #ContentPanel {
                background-color: #070b18;
                border-radius: 18px;
                border: 1px solid rgba(145, 180, 255, 0.38);
            }

            QPushButton#NavButton {
                background-color: #12172b;
                color: #e2e6ff;
                border-radius: 10px;
                border: 1px solid rgba(120, 150, 255, 0.6);
                padding: 8px 12px;
                text-align: left;
            }

            QPushButton#NavButton:hover {
                background-color: #171d35;
                border-color: rgba(160, 190, 255, 0.9);
            }

            QPushButton#NavButton[active="true"] {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2730ff,
                    stop: 0.5 #ff2fb9,
                    stop: 1 #00ffd0
                );
                color: #ffffff;
                border-color: rgba(255, 255, 255, 0.9);
                font-weight: 600;
            }

            QPushButton#NavButton:pressed {
                background-color: #1b22c8;
            }

            QLabel#FooterLabel {
                color: #7f86b0;
                font-size: 11px;
            }
            """
        else:
            stylesheet = """
            QMainWindow {
                background-color: #050816;
            }

            #TitleLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: 700;
            }

            #SubtitleLabel {
                color: #9fa4c9;
                font-size: 12px;
            }

            #NavTitleLabel {
                color: #e0e3ff;
                font-size: 13px;
                font-weight: 600;
            }

            #PageTitleLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 6px;
            }

            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            #NavPanel {
                background-color: #090f20;
                border-radius: 14px;
                border: 1px solid rgba(120, 150, 255, 0.25);
            }

            #ContentPanel {
                background-color: #070b18;
                border-radius: 18px;
                border: 1px solid rgba(145, 180, 255, 0.18);
            }

            QPushButton#NavButton {
                background-color: #12172b;
                color: #e2e6ff;
                border-radius: 10px;
                border: 1px solid rgba(120, 150, 255, 0.3);
                padding: 8px 12px;
                text-align: left;
            }

            QPushButton#NavButton:hover {
                background-color: #171d35;
                border-color: rgba(160, 190, 255, 0.7);
            }

            QPushButton#NavButton[active="true"] {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2730ff,
                    stop: 1 #8c42f5
                );
                color: #ffffff;
                border-color: rgba(255, 255, 255, 0.8);
                font-weight: 600;
            }

            QPushButton#NavButton:pressed {
                background-color: #1b22c8;
            }

            QLabel#FooterLabel {
                color: #7f86b0;
                font-size: 11px;
            }
            """

        self.setStyleSheet(stylesheet)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    QTimer.singleShot(2000, lambda: check_for_update(window, APP_VERSION))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
