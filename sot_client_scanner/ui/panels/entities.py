"""Entities / Loot panel."""

from datetime import datetime

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel

from sot_client_scanner.ui.helpers import make_value_label
from sot_client_scanner.ui.display_names import ENTITY_DISPLAY_NAMES


class EntitiesPanel(QGroupBox):
    """Displays nearby entities (players, NPCs, loot, etc.)."""

    def __init__(self):
        super().__init__("Entities / Loot")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = make_value_label("No entities", "#71717a", 11)
        layout.addWidget(self.label)

        self.timestamp = QLabel("")
        self.timestamp.setStyleSheet("font-size: 9px; color: #3f3f46; padding: 2px 0;")
        layout.addWidget(self.timestamp)

        layout.addStretch()
        self.setLayout(layout)

    def update_data(self, entities):
        """Handle an entities_update signal."""
        now = f"Updated: {datetime.now().strftime('%H:%M:%S')}"
        if entities:
            lines = []
            for entity in entities:
                if ':' in entity:
                    name, count = entity.split(':', 1)
                    friendly = ENTITY_DISPLAY_NAMES.get(name, name.replace("_", " "))
                    lines.append(f"{friendly} × {count}")
            self.label.setText("\n".join(lines))
            self.label.setStyleSheet("font-size: 11px; color: #58a6ff; padding: 1px 0;")
        else:
            self.label.setText("No entities")
            self.label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")
        self.timestamp.setText(now)
