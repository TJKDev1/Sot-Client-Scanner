"""Ships Nearby panel."""

from datetime import datetime

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel

from sot_client_scanner.ui.helpers import make_value_label
from sot_client_scanner.ui.display_names import SHIP_LIST_NAMES


class ShipsPanel(QGroupBox):
    """Displays nearby player and AI ships."""

    def __init__(self):
        super().__init__("Ships Nearby")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = make_value_label("No ships detected", "#71717a", 11)
        layout.addWidget(self.label)

        self.timestamp = QLabel("")
        self.timestamp.setStyleSheet("font-size: 9px; color: #3f3f46; padding: 2px 0;")
        layout.addWidget(self.timestamp)

        layout.addStretch()
        self.setLayout(layout)

    def update_data(self, ships):
        """Handle a ships_update signal."""
        now = f"Updated: {datetime.now().strftime('%H:%M:%S')}"
        if ships:
            lines = []
            for ship in ships:
                if ':' in ship:
                    name, count = ship.split(':', 1)
                    count = int(count)
                    if name in SHIP_LIST_NAMES:
                        lines.append(f"{SHIP_LIST_NAMES[name]} × {count}")
                    elif "AI_Ship" in name:
                        ai_type = name.replace("AI_Ship_", "").replace("_", " ")
                        lines.append(f"AI {ai_type} × {count}")
                    elif "Rowboat" in name:
                        rb_type = name.replace("Rowboat_", "").replace("Rowboat", "Standard")
                        lines.append(f"{rb_type} Rowboat × {count}")
                    else:
                        lines.append(f"{name} × {count}")
            self.label.setText("\n".join(lines))
            self.label.setStyleSheet("font-size: 11px; color: #60a5fa; padding: 2px 0;")
        else:
            self.label.setText("No ships detected")
            self.label.setStyleSheet("font-size: 11px; color: #71717a; padding: 2px 0;")
        self.timestamp.setText(now)
