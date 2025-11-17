from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QCheckBox
from PySide6.QtCore import Qt


class SettingsPage(QWidget):
    def __init__(self, on_language_change=None, on_rgb_toggle=None, on_name_style_change=None):
        super().__init__()
        self.language = "en"
        self.on_language_change = on_language_change
        self.on_rgb_toggle = on_rgb_toggle
        self.on_name_style_change = on_name_style_change
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(12)

        self.heading = QLabel()
        self.heading.setObjectName("PageTitleLabel")
        self.heading.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.desc = QLabel()
        self.desc.setWordWrap(True)

        # Language
        row_lang = QHBoxLayout()
        self.lbl_lang = QLabel()
        self.combo_lang = QComboBox()
        self.combo_lang.addItem("English", userData="en")
        self.combo_lang.addItem("Deutsch", userData="de")
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)
        row_lang.addWidget(self.lbl_lang)
        row_lang.addStretch()
        row_lang.addWidget(self.combo_lang)

        # RGB
        row_rgb = QHBoxLayout()
        self.lbl_rgb = QLabel()
        self.chk_rgb = QCheckBox()
        self.chk_rgb.setChecked(True)
        self.chk_rgb.stateChanged.connect(self._on_rgb_changed)
        row_rgb.addWidget(self.lbl_rgb)
        row_rgb.addStretch()
        row_rgb.addWidget(self.chk_rgb)

        # Name style (vanilla / mod)
        row_style = QHBoxLayout()
        self.lbl_style = QLabel()
        self.combo_style = QComboBox()
        self.combo_style.addItem("Vanilla", userData="vanilla")
        self.combo_style.addItem("Mod (DarkOrbit names)", userData="mod")
        self.combo_style.currentIndexChanged.connect(self._on_style_changed)
        row_style.addWidget(self.lbl_style)
        row_style.addStretch()
        row_style.addWidget(self.combo_style)

        layout.addWidget(self.heading)
        layout.addWidget(self.desc)
        layout.addLayout(row_lang)
        layout.addLayout(row_rgb)
        layout.addLayout(row_style)
        layout.addStretch()

        self.set_language(self.language)

    def _on_lang_changed(self, index: int):
        lang = self.combo_lang.itemData(index)
        if self.on_language_change and lang:
            self.on_language_change(lang)
        self.set_language(lang)

    def _on_rgb_changed(self, state: int):
        enabled = state == 2
        if self.on_rgb_toggle:
            self.on_rgb_toggle(enabled)

    def _on_style_changed(self, index: int):
        style = self.combo_style.itemData(index)
        if self.on_name_style_change and style:
            self.on_name_style_change(style)

    def set_language(self, lang: str):
        self.language = lang
        if lang == "de":
            self.heading.setText("Einstellungen")
            self.desc.setText("Sprache, RGB-Design und Namensstil (Vanilla/Mod) anpassen.")
            self.lbl_lang.setText("Sprache:")
            self.lbl_rgb.setText("RGB-Effekte aktivieren:")
            self.lbl_style.setText("Namenstil (Laser/Munition):")
        else:
            self.heading.setText("Settings")
            self.desc.setText("Adjust language, RGB look and name style (Vanilla/Mod).")
            self.lbl_lang.setText("Language:")
            self.lbl_rgb.setText("Enable RGB effects:")
            self.lbl_style.setText("Name style (lasers/ammo):")
