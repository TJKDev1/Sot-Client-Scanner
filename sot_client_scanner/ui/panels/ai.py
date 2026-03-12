"""AI / Enemies panel."""

from datetime import datetime

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel

from sot_client_scanner.ui.helpers import make_value_label
from sot_client_scanner.ui.display_names import AI_DISPLAY_NAMES


class AIPanel(QGroupBox):
    """Displays active AI threats (skeletons, megs, krakens, etc.)."""

    def __init__(self):
        super().__init__("AI / Enemies")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = make_value_label("No active threats", "#71717a", 11)
        layout.addWidget(self.label)

        self.timestamp = QLabel("")
        self.timestamp.setStyleSheet("font-size: 9px; color: #3f3f46; padding: 2px 0;")
        layout.addWidget(self.timestamp)

        layout.addStretch()
        self.setLayout(layout)

    def update_data(self, ai_list):
        """Handle an ai_entities_update signal."""
        now = f"Updated: {datetime.now().strftime('%H:%M:%S')}"
        if ai_list:
            lines = []
            for ai in ai_list:
                if ':' in ai:
                    name, count = ai.split(':', 1)
                    friendly = AI_DISPLAY_NAMES.get(name, name.replace("AI_", "").replace("_", " "))
                    lines.append(f"{friendly} × {count}")
            self.label.setText("\n".join(lines))

            has_threats = any(not any(p in ai for p in ["Fauna", "Pets", "Fish"]) for ai in ai_list)
            color = "#ef4444" if has_threats else "#71717a"
            self.label.setStyleSheet(f"font-size: 11px; color: {color}; padding: 2px 0;")
        else:
            self.label.setText("No active threats")
            self.label.setStyleSheet("font-size: 11px; color: #71717a; padding: 2px 0;")
        self.timestamp.setText(now)
