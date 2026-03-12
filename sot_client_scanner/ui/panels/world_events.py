"""World Events panel."""

from datetime import datetime

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel

from sot_client_scanner.ui.helpers import make_value_label


class WorldEventsPanel(QGroupBox):
    """Displays active world events (skull clouds, storms, etc.)."""

    def __init__(self):
        super().__init__("World Events")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = make_value_label("No active events", "#71717a", 11)
        layout.addWidget(self.label)

        self.timestamp = QLabel("")
        self.timestamp.setStyleSheet("font-size: 9px; color: #3f3f46; padding: 2px 0;")
        layout.addWidget(self.timestamp)

        layout.addStretch()
        self.setLayout(layout)

    def update_data(self, events):
        """Handle a world_events_update signal."""
        now = f"Updated: {datetime.now().strftime('%H:%M:%S')}"
        if events:
            lines = []
            for event in events:
                if ':' in event:
                    name, count = event.split(':', 1)
                    readable = name.replace('_', ' ').replace('Ghostship Flameheart Cloud', 'Flameheart')
                    lines.append(f"{readable} ({count})")
            self.label.setText("\n".join(lines) if lines else "No active events")
            color = "#a3e635" if lines else "#71717a"
            self.label.setStyleSheet(f"font-size: 11px; color: {color}; padding: 2px 0;")
        else:
            self.label.setText("No active events")
            self.label.setStyleSheet("font-size: 11px; color: #71717a; padding: 2px 0;")
        self.timestamp.setText(now)
