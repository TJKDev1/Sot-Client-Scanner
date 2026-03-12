"""Ship Info panel."""

from datetime import datetime

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel

from sot_client_scanner.ui.helpers import make_value_label, make_header_label, make_separator
from sot_client_scanner.ui.display_names import SHIP_DISPLAY_NAMES, SYSTEM_DISPLAY_NAMES


class ShipInfoPanel(QGroupBox):
    """Displays the player's current ship type and active ship systems."""

    def __init__(self):
        super().__init__("Ship Info")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("YOUR SHIP"))
        self.ship_type_label = make_value_label("Not on a ship", "#71717a", 13, True)
        layout.addWidget(self.ship_type_label)

        layout.addWidget(make_separator())

        layout.addWidget(make_header_label("ACTIVE SYSTEMS"))
        self.ship_systems_label = make_value_label("No active systems", "#71717a", 11)
        layout.addWidget(self.ship_systems_label)

        self.timestamp = QLabel("")
        self.timestamp.setStyleSheet("font-size: 9px; color: #3f3f46; padding: 2px 0;")
        layout.addWidget(self.timestamp)

        layout.addStretch()
        self.setLayout(layout)

    def update_player_ship(self, data):
        """Handle a player_ship_update signal."""
        size = data.get("size", "")
        if size:
            name = SHIP_DISPLAY_NAMES.get(size, size)
            self.ship_type_label.setText(name)
            self.ship_type_label.setStyleSheet("font-size: 13px; color: #a3e635; font-weight: bold; padding: 2px 0;")
        else:
            self.ship_type_label.setText("Not on a ship")
            self.ship_type_label.setStyleSheet("font-size: 13px; color: #71717a; font-weight: bold; padding: 2px 0;")
        self.timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_ship_systems(self, systems):
        """Handle a ship_systems_update signal."""
        if systems:
            lines = []
            for system in systems:
                # Skip inaccurate data
                if system in ["SINKING", "Mast"] or system.startswith("Water:") or system.startswith("HullDamage:"):
                    continue
                if system in SYSTEM_DISPLAY_NAMES:
                    lines.append(SYSTEM_DISPLAY_NAMES[system])
                else:
                    lines.append(system)

            if lines:
                self.ship_systems_label.setText("\n".join(lines))
                self.ship_systems_label.setStyleSheet("font-size: 11px; color: #a3e635; padding: 2px 0;")
            else:
                self.ship_systems_label.setText("No active systems")
                self.ship_systems_label.setStyleSheet("font-size: 11px; color: #71717a; padding: 2px 0;")
        else:
            self.ship_systems_label.setText("No active systems")
            self.ship_systems_label.setStyleSheet("font-size: 11px; color: #71717a; padding: 2px 0;")
