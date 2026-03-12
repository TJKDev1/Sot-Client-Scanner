"""Player Position panel."""

from datetime import datetime

from PySide6.QtWidgets import QGroupBox, QGridLayout, QLabel

from sot_client_scanner.constants.locations import LOCATION_NAMES
from sot_client_scanner.ui.helpers import make_value_label, make_header_label, make_separator


class PositionPanel(QGroupBox):
    """Displays the player's current position and location name."""

    def __init__(self):
        super().__init__("Player Position")
        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("LOCATION"), 0, 0, 1, 2)
        self.location_label = make_value_label("Waiting for data...", "#60a5fa", 13, True)
        layout.addWidget(self.location_label, 1, 0, 1, 2)

        layout.addWidget(make_separator(), 2, 0, 1, 2)

        layout.addWidget(make_header_label("X"), 3, 0)
        self.pos_x = make_value_label("—", "#7ee787", 11)
        layout.addWidget(self.pos_x, 3, 1)

        layout.addWidget(make_header_label("Y"), 4, 0)
        self.pos_y = make_value_label("—", "#7ee787", 11)
        layout.addWidget(self.pos_y, 4, 1)

        layout.addWidget(make_header_label("Z"), 5, 0)
        self.pos_z = make_value_label("—", "#7ee787", 11)
        layout.addWidget(self.pos_z, 5, 1)

        self.timestamp = QLabel("")
        self.timestamp.setStyleSheet("font-size: 9px; color: #3f3f46; padding: 2px 0;")
        layout.addWidget(self.timestamp, 6, 0, 1, 2)

        layout.setRowStretch(7, 1)
        self.setLayout(layout)

    def update_data(self, data):
        """Handle a position_update signal."""
        self.pos_x.setText(f"{data['x']:.1f}")
        self.pos_y.setText(f"{data['y']:.1f}")
        self.pos_z.setText(f"{data['z']:.1f}")
        self.pos_x.setStyleSheet("font-size: 11px; color: #a3e635; padding: 2px 0;")
        self.pos_y.setStyleSheet("font-size: 11px; color: #a3e635; padding: 2px 0;")
        self.pos_z.setStyleSheet("font-size: 11px; color: #a3e635; padding: 2px 0;")

        raw_loc = data['location']
        friendly = LOCATION_NAMES.get(raw_loc, raw_loc.replace("_", " ").title())
        self.location_label.setText(friendly)
        self.location_label.setStyleSheet("font-size: 13px; color: #60a5fa; font-weight: bold; padding: 2px 0;")

        self.timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
