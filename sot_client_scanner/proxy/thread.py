"""QThread that runs mitmdump and emits parsed telemetry signals."""

import subprocess
import os

from PySide6.QtCore import QThread, Signal

from sot_client_scanner.proxy.parser import parse_line
from sot_client_scanner.utils.app import get_project_root


class ProxyThread(QThread):
    """Runs mitmdump as a subprocess, parses its output, and emits Qt signals."""

    output = Signal(str)
    position_update = Signal(dict)
    world_events_update = Signal(list)
    ships_update = Signal(list)
    ship_systems_update = Signal(list)
    ai_entities_update = Signal(list)
    entities_update = Signal(list)
    event_captured = Signal(str)
    network_update = Signal(dict)
    fps_update = Signal(dict)
    action_state_update = Signal(dict)
    crew_update = Signal(dict)
    player_ship_update = Signal(dict)
    company_update = Signal(list)
    season_update = Signal(dict)
    fire_update = Signal(dict)
    gamemode_update = Signal(dict)
    prompt_update = Signal(dict)
    services_update = Signal(dict)
    boot_error_update = Signal(dict)
    ui_screen_update = Signal(dict)
    window_update = Signal(dict)
    client_update = Signal(dict)
    movement_base_update = Signal(dict)
    finished_signal = Signal()

    # Map parser result names → Qt signals (populated in __init__)
    _signal_map: dict

    def __init__(self):
        super().__init__()
        self.process = None
        self.running = False

        # Build dispatch table from signal names → bound Signal objects
        self._signal_map = {
            "output": self.output,
            "position_update": self.position_update,
            "world_events_update": self.world_events_update,
            "ships_update": self.ships_update,
            "ship_systems_update": self.ship_systems_update,
            "ai_entities_update": self.ai_entities_update,
            "entities_update": self.entities_update,
            "event_captured": self.event_captured,
            "network_update": self.network_update,
            "fps_update": self.fps_update,
            "action_state_update": self.action_state_update,
            "crew_update": self.crew_update,
            "player_ship_update": self.player_ship_update,
            "company_update": self.company_update,
            "season_update": self.season_update,
            "fire_update": self.fire_update,
            "gamemode_update": self.gamemode_update,
            "prompt_update": self.prompt_update,
            "services_update": self.services_update,
            "boot_error_update": self.boot_error_update,
            "ui_screen_update": self.ui_screen_update,
            "window_update": self.window_update,
            "client_update": self.client_update,
            "movement_base_update": self.movement_base_update,
        }

    def run(self):
        self.running = True
        try:
            app_dir = get_project_root()
            addon_path = os.path.join(app_dir, "game_capture.py")

            if not os.path.exists(addon_path):
                self.output.emit(f"ERROR: game_capture.py not found in {app_dir}")
                self.output.emit("Make sure game_capture.py is in the same folder as the exe!")
                return

            self.output.emit(f"Using addon: {addon_path}")

            self.process = subprocess.Popen(
                ["mitmdump", "-s", addon_path, "--set", "block_global=false"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=app_dir,
            )

            for line in self.process.stdout:
                if not self.running:
                    break
                self._dispatch(line.strip())

            self.process.wait()
        except Exception as e:
            self.output.emit(f"Error: {str(e)}")
        finally:
            self.finished_signal.emit()

    def _dispatch(self, line):
        """Parse a line and emit the corresponding Qt signals."""
        for signal_name, data in parse_line(line):
            sig = self._signal_map.get(signal_name)
            if sig is not None:
                sig.emit(data)

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
