from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class QuestsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.language = "en"
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)
        self.heading = QLabel()
        self.heading.setObjectName("PageTitleLabel")
        self.heading.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.desc = QLabel()
        self.desc.setWordWrap(True)
        layout.addWidget(self.heading)
        layout.addWidget(self.desc)
        layout.addStretch()
        self.set_language(self.language)

    def set_language(self, lang: str):
        self.language = lang
        if lang == "de":
            self.heading.setText("Quest-Hilfe")
            self.desc.setText("Hier wird später eine durchsuchbare Liste von Quests angezeigt.")
        else:
            self.heading.setText("Quest Helper")
            self.desc.setText("This page will show a searchable list of quests.")
