"""Session panel — crew, action state, prompts, movement base, fire, events."""

from datetime import datetime

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel

from sot_client_scanner.constants.game_data import ACTION_STATES, SESSION_SHIP
from sot_client_scanner.ui.helpers import make_value_label, make_header_label, make_separator


class SessionPanel(QGroupBox):
    """Displays crew info, current action, prompts, fire status, and last event."""

    def __init__(self):
        super().__init__("Session")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("CREW"))
        self.crew_label = make_value_label("No crew data", "#71717a", 11)
        layout.addWidget(self.crew_label)

        layout.addWidget(make_header_label("ACTION"))
        self.action_label = make_value_label("—", "#71717a", 12, True)
        layout.addWidget(self.action_label)

        layout.addWidget(make_header_label("LAST PROMPT"))
        self.prompt_label = make_value_label("—", "#71717a", 10)
        self.prompt_label.setWordWrap(True)
        layout.addWidget(self.prompt_label)

        layout.addWidget(make_header_label("MOVEMENT BASE"))
        self.movement_base_label = make_value_label("—", "#71717a", 10)
        self.movement_base_label.setWordWrap(True)
        layout.addWidget(self.movement_base_label)

        layout.addWidget(make_header_label("FIRE"))
        self.fire_label = make_value_label("No fire", "#71717a", 11)
        layout.addWidget(self.fire_label)

        layout.addWidget(make_separator())

        layout.addWidget(make_header_label("LAST EVENT"))
        self.last_event_label = make_value_label("—", "#71717a", 10)
        self.last_event_label.setWordWrap(True)
        layout.addWidget(self.last_event_label)

        self.timestamp = QLabel("")
        self.timestamp.setStyleSheet("font-size: 9px; color: #3f3f46; padding: 2px 0;")
        layout.addWidget(self.timestamp)

        layout.addStretch()
        self.setLayout(layout)

    def update_action_state(self, data):
        """Handle an action_state_update signal."""
        state_id = data["to"]
        friendly = ACTION_STATES.get(state_id, state_id.replace("ActionStateId", "").replace("Id", ""))
        self.action_label.setText(friendly)

        danger_states = [
            "DeadActionStateId", "GhostActionStateId", "ReviveableActionStateId",
            "SinkingTunnelOfTheDamnedActionStateId",
        ]
        active_states = [
            "UseCannonActionStateId", "HarpoonActionStateId", "FiredFromCannonActionStateId",
            "DigActionStateId", "FishingActionStateId", "RepairActionStateId", "BailingActionStateId",
        ]
        ship_states = [
            "ControlWheelActionStateId", "ControlCapstanArmActionStateId",
            "SailManipulationActionStateId", "ControlPulleyActionStateId",
        ]

        if state_id in danger_states:
            color = "#ef4444"
        elif state_id in active_states:
            color = "#f97316"
        elif state_id in ship_states:
            color = "#60a5fa"
        else:
            color = "#fbbf24"
        self.action_label.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: bold; padding: 2px 0;")

        self.timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_crew(self, data):
        """Handle a crew_update signal. Returns the formatted text for the bottom bar."""
        ship_name = SESSION_SHIP.get(data["session"], data["session"])
        parts = [f"Crew: {data['count']}"]
        if ship_name:
            parts.append(ship_name)
        parts.append(data["type"])
        if data["captained"]:
            parts.append("Captain")
        if data["alliance"]:
            parts.append("Alliance")
        if data["guild"]:
            parts.append("Guild")
        crew_text = "  |  ".join(parts)
        self.crew_label.setText(crew_text)
        return crew_text

    def update_fire(self, data):
        """Handle a fire_update signal."""
        ships = data["ships"]
        cells = data["cells"]
        if cells > 0:
            self.fire_label.setText(f"{cells} fire cells on {ships} ship(s)!")
            self.fire_label.setStyleSheet("font-size: 11px; color: #ef4444; font-weight: bold; padding: 2px 0;")
        else:
            self.fire_label.setText("No fire")
            self.fire_label.setStyleSheet("font-size: 11px; color: #71717a; padding: 2px 0;")

    def update_prompt(self, data):
        """Handle a prompt_update signal."""
        msg = data.get("message", "")
        if msg:
            self.prompt_label.setText(msg)
            self.prompt_label.setStyleSheet("font-size: 11px; color: #c4b5fd; padding: 2px 0;")

    def update_movement_base(self, data):
        """Handle a movement_base_update signal."""
        prev = data.get("from", "")
        new = data.get("to", "")
        if prev or new:
            self.movement_base_label.setText(f"{prev} → {new}" if prev else new)

    def update_event(self, event_name):
        """Update the last-event label (called for every captured event)."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.last_event_label.setText(f"[{ts}] {event_name}")
