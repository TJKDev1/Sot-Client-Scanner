"""
Sea of Thieves Client Reader - Main GUI Application
Requires: PySide6, mitmproxy

For PyInstaller:
  pyinstaller --onefile --windowed --name "SoT_Reader" sot_reader.py

Then distribute SoT_Reader.exe + game_capture.py together in the same folder.
"""
import subprocess
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QPushButton, QTextEdit, QLabel, QHBoxLayout,
                               QMessageBox, QGroupBox, QGridLayout, QScrollArea,
                               QFrame, QProgressBar, QSplitter, QTabWidget)
from PySide6.QtCore import QThread, Signal, Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QIcon
import atexit
import signal
import re
from datetime import datetime

# ─── Sea of Thieves location name mapping ────────────────────────────────────
LOCATION_NAMES = {
    # Outposts - The Shores of Plenty
    "wsp_outpost_1": "Sanctuary Outpost",
    "wsp_outpost_2": "Plunder Outpost",
    # Outposts - The Wilds
    "wld_outpost_1": "Dagger Tooth Outpost",
    "wld_outpost_2": "Galleon's Grave Outpost",
    # Outposts - The Ancient Isles
    "anc_outpost_1": "Ancient Spire Outpost",
    "anc_outpost_2": "Plunder Outpost",
    # Outposts - The Devil's Roar
    "dvr_outpost_1": "Morrow's Peak Outpost",
    # Seaposts
    "wsp_seapost_1": "The North Star Seapost",
    "wsp_seapost_2": "The Spoils of Plenty Store",
    "wld_seapost_1": "Stephen's Spoils",
    "wld_seapost_2": "The Wild Treasures Store",
    "anc_seapost_1": "Three Paces East Seapost",
    "anc_seapost_2": "Roaring Traders",
    "dvr_seapost_1": "Brian's Bazaar",
    # Large islands - Shores of Plenty
    "wsp_large_island_01": "Smugglers' Bay",
    "wsp_large_island_02": "Cannon Cove",
    "wsp_large_island_03": "Wanderers Refuge",
    "wsp_large_island_04": "Crook's Hollow",
    "wsp_large_island_05": "Mermaid's Hideaway",
    # Large islands - The Wilds
    "wld_large_island_01": "Marauder's Arch",
    "wld_large_island_02": "Kraken's Fall",
    "wld_large_island_03": "Shipwreck Bay",
    "wld_large_island_04": "The Crooked Masts",
    # Large islands - Ancient Isles
    "anc_large_island_01": "Plunder Valley",
    "anc_large_island_02": "Discovery Ridge",
    "anc_large_island_03": "Snake Island",
    "anc_large_island_04": "Devil's Ridge",
    "anc_large_island_05": "Thieves' Haven",
    # Devil's Roar islands
    "dvr_large_island_01": "The Devil's Thirst",
    "dvr_large_island_02": "Fetcher's Rest",
    "dvr_large_island_03": "Flintlock Peninsula",
    "dvr_large_island_04": "Ashen Reaches",
    "dvr_large_island_05": "Ruby's Fall",
    # Forts
    "wsp_fort_01": "Sailor's Knot Stronghold",
    "wsp_fort_02": "Hidden Spring Keep",
    "wld_fort_01": "Keel Haul Fort",
    "wld_fort_02": "The Crow's Nest Fortress",
    "anc_fort_01": "Skull Keep",
    "anc_fort_02": "Kraken Watchtower",
    "anc_fort_03": "Lost Gold Fort",
    "anc_fort_04": "Old Boot Fort",
    "dvr_fort_01": "Molten Sands Fortress",
    # Special
    "open_sea": "Open Sea",
    "sea_of_the_damned": "Sea of the Damned",
    "reapers_hideout": "Reaper's Hideout",
    "athena_hideout": "Pirate Legend Hideout",
}

# Company display names and icons
COMPANY_INFO = {
    "GoldHoarders": {"name": "Gold Hoarders", "icon": "🔑", "color": "#FFD700"},
    "OrderOfSouls": {"name": "Order of Souls", "icon": "💀", "color": "#9B59B6"},
    "MerchantAlliance": {"name": "Merchant Alliance", "icon": "📦", "color": "#2ECC71"},
    "ReapersBones": {"name": "Reaper's Bones", "icon": "☠️", "color": "#E74C3C"},
    "AthenasFortune": {"name": "Athena's Fortune", "icon": "💎", "color": "#00CED1"},
    "HuntersCall": {"name": "Hunter's Call", "icon": "🐟", "color": "#3498DB"},
    "SeaDogs": {"name": "Sea Dogs", "icon": "⚔️", "color": "#E67E22"},
    "FactionB": {"name": "Servants of the Flame", "icon": "🔥", "color": "#FF4500"},
    "FactionG": {"name": "Guardians of Fortune", "icon": "🛡️", "color": "#1ABC9C"},
    "Smugglers": {"name": "Smugglers", "icon": "🗝️", "color": "#95A5A6"},
}

# Action state readable names
ACTION_STATES = {
    # Basic Movement
    "LocomotionActionStateId": "Walking",
    "SprintActionStateId": "Sprinting",
    "JumpActionStateId": "Jumping",
    "CrouchActionStateId": "Crouching",
    "SwimmingActionStateId": "Swimming",
    "SwimmingIdleActionStateId": "Treading Water",

    # Ladders & Climbing
    "ClimbingActionStateId": "Climbing Ladder",
    "UseLadderActionStateId": "Using Ladder",
    "OnBottomTransitionLadderActionStateId": "Mounting Ladder",
    "OffTopTransitionLadderActionStateId": "Dismounting Ladder",

    # Ship Controls
    "ControlWheelActionStateId": "Steering Ship",
    "ControlCapstanArmActionStateId": "Operating Anchor",
    "SailManipulationActionStateId": "Adjusting Sails",
    "ControlPulleyActionStateId": "Using Pulley",
    "HarpoonActionStateId": "Using Harpoon",

    # Combat & Actions
    "UseCannonActionStateId": "Using Cannon",
    "FiredFromCannonActionStateId": "Fired from Cannon",
    "LoadItemActionStateId": "Loading Item",
    "DigActionStateId": "Digging",
    "FishingActionStateId": "Fishing",
    "CookingActionStateId": "Cooking",
    "RepairActionStateId": "Repairing",
    "BailingActionStateId": "Bailing Water",

    # Interactions
    "UseMapTableActionStateId": "Viewing Map",
    "QuestTableActionStateId": "Quest Table",
    "InteractObjectActionStateId": "Interacting",
    "ItemInteractionActionStateId": "Interacting",
    "CompanyShopActionStateId": "Shopping",
    "TakeControlActionStateId": "Taking Control",

    # Social & Emotes
    "EmoteActionStateId": "Emoting",
    "WalkableEmoteActionStateId": "Emoting (Walking)",
    "SittingActionStateId": "Sitting",
    "SleepingActionStateId": "Sleeping",
    "PlayingInstrumentActionStateId": "Playing Instrument",
    "HideInObjectActionStateId": "Hiding",

    # Death & Respawn
    "DeadActionStateId": "Dead",
    "GhostActionStateId": "Ghost (Ferry)",
    "ReviveActionStateId": "Being Revived",
    "ReviveableActionStateId": "Reviveable",
    "RespawnActionStateId": "Respawning",
    "WaitingToSpawnActionStateId": "Waiting to Spawn",

    # Tunnels & Teleports
    "TeleportActionStateId": "Teleporting",
    "EnterTunnelOfTheDamnedActionStateId": "Entering Ferry",
    "SinkingTunnelOfTheDamnedActionStateId": "Ship Sinking (Ferry)",
    "ArrivalTunnelOfTheDamnedActionStateId": "Arriving at Ferry",
    "LeaveGhostShipActionStateId": "Leaving Ghost Ship",

    # Special States
    "ZiplineActionStateId": "Using Zipline",
    "RideTransitionActionStateId": "Mounting/Dismounting",
    "LoadPlayerActionStateId": "Loading",
    "MigrationActionStateId": "Server Migration",
    "RowingActionStateId": "Rowing",
    "NullActionStateId": "Idle",
    "Invalid": "Transitioning",
}

# Session type to ship name
SESSION_SHIP = {
    "SmallShipSessionTemplate": "Sloop",
    "MediumShipSessionTemplate": "Brigantine",
    "LargeShipSessionTemplate": "Galleon",
}


# ─── Stylesheet ──────────────────────────────────────────────────────────────
DARK_STYLE = """
QMainWindow {
    background-color: #0d1117;
}
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'Consolas', monospace;
}
QGroupBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    margin-top: 14px;
    padding: 12px 8px 8px 8px;
    font-size: 11px;
    font-weight: bold;
    color: #8b949e;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    color: #c9d1d9;
}
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
}
QPushButton:pressed {
    background-color: #0d1117;
}
QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}
QPushButton#startBtn {
    background-color: #238636;
    border-color: #2ea043;
    color: #ffffff;
}
QPushButton#startBtn:hover {
    background-color: #2ea043;
}
QPushButton#startBtn:disabled {
    background-color: #1a3a25;
    border-color: #1a3a25;
    color: #3d6b4f;
}
QPushButton#stopBtn {
    background-color: #da3633;
    border-color: #f85149;
    color: #ffffff;
}
QPushButton#stopBtn:hover {
    background-color: #f85149;
}
QPushButton#stopBtn:disabled {
    background-color: #3d1518;
    border-color: #3d1518;
    color: #6b3539;
}
QTextEdit {
    background-color: #0d1117;
    color: #7ee787;
    border: 1px solid #30363d;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    padding: 4px;
    selection-background-color: #264f78;
}
QLabel {
    background-color: transparent;
    border: none;
}
QTabWidget::pane {
    border: 1px solid #30363d;
    background-color: #161b22;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #21262d;
    color: #8b949e;
    border: 1px solid #30363d;
    border-bottom: none;
    padding: 6px 14px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 11px;
}
QTabBar::tab:selected {
    background-color: #161b22;
    color: #c9d1d9;
    font-weight: bold;
}
QTabBar::tab:hover {
    background-color: #30363d;
    color: #c9d1d9;
}
QProgressBar {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 3px;
    height: 14px;
    text-align: center;
    font-size: 9px;
    color: #c9d1d9;
}
QProgressBar::chunk {
    border-radius: 2px;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QSplitter::handle {
    background-color: #30363d;
    height: 2px;
}
"""


def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def setup_mitmproxy():
    try:
        import mitmproxy
        return True
    except ImportError:
        return False


def check_certificate():
    cert_path = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.cer"
    return cert_path.exists()


def set_system_proxy(enable=True):
    if sys.platform == "win32":
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                                 0, winreg.KEY_WRITE)
            if enable:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:8080")
            else:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error setting proxy: {e}")
            return False
    return False


def emergency_disable_proxy():
    print("EMERGENCY: Disabling proxy...")
    set_system_proxy(False)


atexit.register(emergency_disable_proxy)


def signal_handler(signum, frame):
    print(f"Received signal {signum}, disabling proxy...")
    emergency_disable_proxy()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
if sys.platform == "win32":
    signal.signal(signal.SIGBREAK, signal_handler)


# ─── Proxy Thread ────────────────────────────────────────────────────────────
class ProxyThread(QThread):
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

    def __init__(self):
        super().__init__()
        self.process = None
        self.running = False

    def run(self):
        self.running = True
        try:
            app_dir = get_app_dir()
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
                cwd=app_dir
            )

            for line in self.process.stdout:
                if not self.running:
                    break

                self._parse_line(line.strip())

            self.process.wait()
        except Exception as e:
            self.output.emit(f"Error: {str(e)}")
        finally:
            self.finished_signal.emit()

    def _parse_line(self, line):
        if not line:
            return

        if "[POSITION]" in line:
            match = re.search(r"X:([\d.-]+) Y:([\d.-]+) Z:([\d.-]+) Location:(\S+)", line)
            if match:
                self.position_update.emit({
                    "x": float(match.group(1)),
                    "y": float(match.group(2)),
                    "z": float(match.group(3)),
                    "location": match.group(4)
                })

        elif "[NETWORK]" in line:
            match = re.search(
                r"RTT:(-?[\d]+)ms Var:(-?[\d]+)ms Out:(\d+)B/s In:(\d+)B/s OutLoss:([\d.]+) InLoss:([\d.]+)",
                line)
            if match:
                self.network_update.emit({
                    "rtt": int(match.group(1)),
                    "rtt_var": int(match.group(2)),
                    "out_bps": int(match.group(3)),
                    "in_bps": int(match.group(4)),
                    "out_loss": float(match.group(5)),
                    "in_loss": float(match.group(6)),
                })

        elif "[FPS]" in line:
            match = re.search(
                r"AvgFrame:([\d.]+)ms MinFrame:([\d.]+)ms MaxFrame:([\d.]+)ms Target:([\d.]+)ms Histogram:(.*)",
                line)
            if match:
                self.fps_update.emit({
                    "avg_frame": float(match.group(1)),
                    "min_frame": float(match.group(2)),
                    "max_frame": float(match.group(3)),
                    "target": float(match.group(4)),
                    "histogram": match.group(5),
                })

        elif "[ACTION_STATE]" in line:
            match = re.search(r"From:(\S+) To:(\S+) TimeInPrev:([\d.]+)s", line)
            if match:
                self.action_state_update.emit({
                    "from": match.group(1),
                    "to": match.group(2),
                    "time_in_prev": float(match.group(3)),
                })

        elif "[CREW]" in line:
            match = re.search(
                r"Count:(\d+) Session:(\S*) Type:(\S*) Captained:(\S+) Alliance:(\S+) Guild:(\S+)",
                line)
            if match:
                self.crew_update.emit({
                    "count": int(match.group(1)),
                    "session": match.group(2),
                    "type": match.group(3),
                    "captained": match.group(4) == "True",
                    "alliance": match.group(5) == "True",
                    "guild": match.group(6) == "True",
                })

        elif "[PLAYER_SHIP]" in line:
            match = re.search(r"Size:(\S*) IsCrewShip:(\S+) ShipPos:\(([\d.-]+),([\d.-]+),([\d.-]+)\)", line)
            if match:
                self.player_ship_update.emit({
                    "size": match.group(1),
                    "is_crew": match.group(2) == "True",
                    "x": float(match.group(3)),
                    "y": float(match.group(4)),
                    "z": float(match.group(5)),
                })

        elif "[COMPANIES]" in line:
            data = line.split("[COMPANIES]")[1].strip()
            companies = []
            for entry in data.split(';'):
                parts = entry.split(':')
                if len(parts) == 4:
                    companies.append({
                        "id": parts[0],
                        "level": int(parts[1]),
                        "xp": int(parts[2]),
                        "xp_next": int(parts[3]),
                    })
            if companies:
                self.company_update.emit(companies)

        elif "[SEASON]" in line:
            match = re.search(r"Title:(.+?) Theme:(\S+) Until:(\S+)", line)
            if match:
                self.season_update.emit({
                    "title": match.group(1),
                    "theme": match.group(2),
                    "until": match.group(3),
                })

        elif "[FIRE]" in line:
            match = re.search(r"ShipsOnFire:(\d+) ActiveCells:(\d+)", line)
            if match:
                self.fire_update.emit({
                    "ships": int(match.group(1)),
                    "cells": int(match.group(2)),
                })

        elif "[GAMEMODE]" in line:
            match = re.search(r"Mode:(\S+) State:(\S*)", line)
            if match:
                self.gamemode_update.emit({
                    "mode": match.group(1),
                    "state": match.group(2),
                })

        elif "[PROMPT]" in line:
            match = re.search(r"Message:(.+?) Key:(.+)$", line)
            if match:
                self.prompt_update.emit({
                    "message": match.group(1),
                    "key": match.group(2),
                })

        elif "[WORLD_EVENTS]" in line:
            events = line.split("[WORLD_EVENTS]")[1].strip().split(',')
            self.world_events_update.emit(events)

        elif "[SHIPS]" in line:
            ships = line.split("[SHIPS]")[1].strip().split(',')
            self.ships_update.emit(ships)

        elif "[SHIP_SYSTEMS]" in line:
            systems = line.split("[SHIP_SYSTEMS]")[1].strip().split(',')
            self.ship_systems_update.emit(systems)

        elif "[AI_ENTITIES]" in line:
            ai_list = line.split("[AI_ENTITIES]")[1].strip().split(',')
            self.ai_entities_update.emit(ai_list)

        elif "[ENTITIES]" in line:
            entities = line.split("[ENTITIES]")[1].strip().split(',')
            self.entities_update.emit(entities)

        elif "[EVENT]" in line:
            event_name = line.split("[EVENT]")[1].strip()
            self.event_captured.emit(event_name)

        # Log relevant lines
        if any(kw in line for kw in
               ["[CAPTURED]", "[POSITION]", "[EVENT]", "[FILTER]", "[ERROR]",
                "[WORLD_EVENTS]", "[SHIPS]", "[SHIP_SYSTEMS]", "[AI_ENTITIES]",
                "[ENTITIES]", "[WEBSOCKET]", "[NETWORK]", "[FPS]", "[ACTION_STATE]",
                "[CREW]", "[COMPANIES]", "[SEASON]", "[FIRE]", "[GAMEMODE]",
                "[PROMPT]", "[PLAYER_SHIP]", "Error", "Exception"]):
            self.output.emit(line)

        elif "[SERVICES]" in line:
            # [SERVICES] Result:None Total:3.502s Refresh:0.466s Token:2.418s Reconnect:-0.618s Reason:... Requested:... Discovery:...
            match = re.search(
                r"Result:(\S*) Total:([\d.-]+)s Refresh:([\d.-]+)s Token:([\d.-]+)s Reconnect:([\d.-]+)s Reason:(.*?) Requested:(\S*) Discovery:(\S*) Logon:(\S*) Contest:(\S*)",
                line
            )
            if match:
                self.services_update.emit({
                    "result": match.group(1),
                    "total": float(match.group(2)),
                    "refresh": float(match.group(3)),
                    "token": float(match.group(4)),
                    "reconnect": float(match.group(5)),
                    "reason": match.group(6).strip(),
                    "requested": match.group(7),
                    "discovery": match.group(8),
                    "logon": match.group(9),
                    "contest": match.group(10),
                })

        elif "[BOOT_ERROR]" in line:
            msg = line.split("[BOOT_ERROR]", 1)[-1].strip()
            if msg:
                self.boot_error_update.emit({"message": msg})

        elif "[UI_SCREEN]" in line:
            match = re.search(r"Current:(\S*) Previous:(\S*)", line)
            if match:
                self.ui_screen_update.emit({"current": match.group(1), "previous": match.group(2)})

        elif "[WINDOW]" in line:
            match = re.search(r"Status:(\S*) Focused:(\S+) Minimized:(\S+) FullScreen:(\S+)", line)
            if match:
                def _to_bool(v: str) -> bool:
                    return v.lower() in ("true", "1", "yes")
                self.window_update.emit({
                    "status": match.group(1),
                    "focused": _to_bool(match.group(2)),
                    "minimized": _to_bool(match.group(3)),
                    "fullscreen": _to_bool(match.group(4)),
                })

        elif "[CLIENT]" in line:
            match = re.search(
                r"Build:(\S*) Platform:(\S*) Spec:(\S*) RHI:(\S*) Foreground:(\S*) Device:(\S*) PlayerGameId:(\S*) Session:(\S*) PlayMode:(\S*) State:(\S*)",
                line
            )
            if match:
                self.client_update.emit({
                    "build": match.group(1),
                    "platform": match.group(2),
                    "spec": match.group(3),
                    "rhi": match.group(4),
                    "foreground": match.group(5),
                    "device": match.group(6),
                    "player_game_id": match.group(7),
                    "session": match.group(8),
                    "play_mode": match.group(9),
                    "state": match.group(10),
                })

        elif "[MOVEMENT_BASE]" in line:
            match = re.search(r"From:(\S*) To:(\S*)", line)
            if match:
                self.movement_base_update.emit({"from": match.group(1), "to": match.group(2)})

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()


# ─── Helper: make a styled label ─────────────────────────────────────────────
def make_value_label(text="—", color="#c9d1d9", size=12, bold=False):
    label = QLabel(text)
    weight = "bold" if bold else "normal"
    label.setStyleSheet(f"font-size: {size}px; color: {color}; font-weight: {weight}; padding: 1px 0;")
    label.setWordWrap(True)
    return label


def make_header_label(text, color="#8b949e", size=10):
    label = QLabel(text)
    label.setStyleSheet(f"font-size: {size}px; color: {color}; font-weight: bold; padding: 0; margin: 0;")
    return label


def make_separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("background-color: #30363d; max-height: 1px; margin: 4px 0;")
    return line


# ─── Main Window ─────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.proxy_thread = None
        self.proxy_running = False
        self.log_file_path = os.path.join(get_app_dir(), "logs\sea_of_thieves_capture.txt")
        self.event_history = []
        self.max_event_history = 50

        self.setWindowTitle("Sea of Thieves — Telemetry Reader")
        self.setGeometry(50, 50, 1360, 780)
        self.setMinimumSize(1100, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root = QVBoxLayout(central_widget)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # ── Top Bar ──────────────────────────────────────────────────────
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        # Title
        title = QLabel("☠  Sea of Thieves Telemetry")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e6edf3; padding: 4px 0;")
        top_bar.addWidget(title)

        top_bar.addStretch()

        # Status pill
        self.status_label = QLabel("  ● OFFLINE  ")
        self.status_label.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #f85149; "
            "background-color: #3d1518; border: 1px solid #f85149; "
            "border-radius: 10px; padding: 3px 10px;")
        top_bar.addWidget(self.status_label)

        # Game mode
        self.gamemode_label = QLabel("")
        self.gamemode_label.setStyleSheet(
            "font-size: 11px; color: #8b949e; padding: 3px 6px;")
        top_bar.addWidget(self.gamemode_label)

        # Season
        self.season_label = QLabel("")
        self.season_label.setStyleSheet(
            "font-size: 11px; color: #8b949e; padding: 3px 6px;")
        top_bar.addWidget(self.season_label)

        root.addLayout(top_bar)

        # ── Main Splitter (panels vs. log) ───────────────────────────────
        splitter = QSplitter(Qt.Vertical)

        # Top area: dashboard panels
        dashboard = QWidget()
        dash_layout = QVBoxLayout(dashboard)
        dash_layout.setContentsMargins(0, 0, 0, 0)
        dash_layout.setSpacing(6)        # Row 1: Position | Network/FPS | Session | Status
        row1 = QHBoxLayout()
        row1.setSpacing(6)
        row1.addWidget(self._build_position_panel(), 1)
        row1.addWidget(self._build_network_panel(), 1)
        row1.addWidget(self._build_session_panel(), 1)
        row1.addWidget(self._build_status_panel(), 1)
        dash_layout.addLayout(row1)

        # Row 2: World Events | Ships | AI | Entities
        row2 = QHBoxLayout()
        row2.setSpacing(6)
        row2.addWidget(self._build_world_events_panel(), 1)
        row2.addWidget(self._build_ships_panel(), 1)
        row2.addWidget(self._build_ai_panel(), 1)
        row2.addWidget(self._build_entities_panel(), 1)
        dash_layout.addLayout(row2)

        splitter.addWidget(dashboard)

        # Bottom area: tabs (event log, companies, console)
        tabs = QTabWidget()
        tabs.setMaximumHeight(220)

        # Event History Tab
        event_tab = QWidget()
        et_layout = QVBoxLayout(event_tab)
        et_layout.setContentsMargins(4, 4, 4, 4)
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setStyleSheet(
            "background-color: #0d1117; color: #c9d1d9; font-family: 'Consolas'; "
            "font-size: 11px; border: none;")
        et_layout.addWidget(self.event_log)
        tabs.addTab(event_tab, "📋 Event Log")

        # Companies Tab
        company_tab = QWidget()
        ct_layout = QVBoxLayout(company_tab)
        ct_layout.setContentsMargins(4, 4, 4, 4)
        self.company_widget = QWidget()
        self.company_layout = QGridLayout(self.company_widget)
        self.company_layout.setSpacing(4)
        self.company_layout.setContentsMargins(0, 0, 0, 0)

        # Create progress bars for companies
        self.company_bars = {}
        self.company_labels = {}

        scroll = QScrollArea()
        scroll.setWidget(self.company_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        ct_layout.addWidget(scroll)
        tabs.addTab(company_tab, "🏴‍☠️ Companies")

        # Console Tab
        console_tab = QWidget()
        con_layout = QVBoxLayout(console_tab)
        con_layout.setContentsMargins(4, 4, 4, 4)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(
            "background-color: #0d1117; color: #7ee787; font-family: 'Consolas'; "
            "font-size: 10px; border: none;")
        con_layout.addWidget(self.console)
        tabs.addTab(console_tab, "🖥 Console")

        splitter.addWidget(tabs)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter)

        # ── Button Bar ───────────────────────────────────────────────────
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        self.start_button = QPushButton("▶  Start Capture")
        self.start_button.setObjectName("startBtn")
        self.start_button.setMinimumHeight(36)
        self.start_button.clicked.connect(self.start_proxy)
        btn_bar.addWidget(self.start_button)

        self.stop_button = QPushButton("■  Stop Capture")
        self.stop_button.setObjectName("stopBtn")
        self.stop_button.setMinimumHeight(36)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_proxy)
        btn_bar.addWidget(self.stop_button)

        btn_bar.addStretch()

        # Crew info inline
        self.crew_label = QLabel("")
        self.crew_label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 0 8px;")
        btn_bar.addWidget(self.crew_label)

        root.addLayout(btn_bar)

        # Run initial checks
        self.check_setup()

    # ── Panel Builders ───────────────────────────────────────────────────
    def _build_position_panel(self):
        group = QGroupBox("🗺  Player Position")
        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("LOCATION"), 0, 0, 1, 2)
        self.location_label = make_value_label("Waiting for data...", "#58a6ff", 13, True)
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

        # Timestamp
        self.position_timestamp = QLabel("")
        self.position_timestamp.setStyleSheet("font-size: 9px; color: #484f58; padding: 2px 0;")
        layout.addWidget(self.position_timestamp, 6, 0, 1, 2)

        layout.setRowStretch(7, 1)
        group.setLayout(layout)
        return group

    def _build_session_panel(self):
        group = QGroupBox("🧭  Session")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("CREW"))
        self.crew_label = make_value_label("No crew data", "#8b949e", 11)
        layout.addWidget(self.crew_label)

        layout.addWidget(make_header_label("ACTION"))
        self.action_label = make_value_label("—", "#8b949e", 12, True)
        layout.addWidget(self.action_label)

        layout.addWidget(make_header_label("LAST PROMPT"))
        self.prompt_label = make_value_label("—", "#8b949e", 10)
        self.prompt_label.setWordWrap(True)
        layout.addWidget(self.prompt_label)

        layout.addWidget(make_header_label("MOVEMENT BASE"))
        self.movement_base_label = make_value_label("—", "#8b949e", 10)
        self.movement_base_label.setWordWrap(True)
        layout.addWidget(self.movement_base_label)

        layout.addWidget(make_header_label("FIRE"))
        self.fire_label = make_value_label("No fire", "#8b949e", 11)
        layout.addWidget(self.fire_label)

        # Timestamp for action state updates
        self.activity_timestamp = QLabel("")
        self.activity_timestamp.setStyleSheet("font-size: 9px; color: #484f58; padding: 2px 0;")
        layout.addWidget(self.activity_timestamp)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _build_status_panel(self):
        group = QGroupBox("📡  Status / Services")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("UI SCREEN"))
        self.ui_screen_label = make_value_label("—", "#8b949e", 11)
        layout.addWidget(self.ui_screen_label)

        layout.addWidget(make_header_label("WINDOW"))
        self.window_label = make_value_label("—", "#8b949e", 11)
        layout.addWidget(self.window_label)

        layout.addWidget(make_separator())

        layout.addWidget(make_header_label("SERVICES CONNECT"))
        self.services_label = make_value_label("—", "#8b949e", 10)
        self.services_label.setWordWrap(True)
        layout.addWidget(self.services_label)

        layout.addWidget(make_header_label("CLIENT"))
        self.client_info_label = make_value_label("—", "#8b949e", 10)
        self.client_info_label.setWordWrap(True)
        layout.addWidget(self.client_info_label)

        layout.addWidget(make_header_label("LAST ERROR"))
        self.boot_error_label = make_value_label("—", "#8b949e", 10)
        self.boot_error_label.setWordWrap(True)
        layout.addWidget(self.boot_error_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _build_network_panel(self):
        group = QGroupBox("📡  Network & Performance")
        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("PING"), 0, 0)
        self.ping_label = make_value_label("— ms", "#c9d1d9", 12, True)
        layout.addWidget(self.ping_label, 0, 1)

        layout.addWidget(make_header_label("JITTER"), 1, 0)
        self.jitter_label = make_value_label("— ms", "#8b949e", 11)
        layout.addWidget(self.jitter_label, 1, 1)

        layout.addWidget(make_header_label("PACKET LOSS"), 2, 0)
        self.loss_label = make_value_label("—", "#8b949e", 11)
        layout.addWidget(self.loss_label, 2, 1)

        layout.addWidget(make_separator(), 3, 0, 1, 2)

        layout.addWidget(make_header_label("BANDWIDTH"), 4, 0)
        self.bw_label = make_value_label("— / —", "#8b949e", 11)
        layout.addWidget(self.bw_label, 4, 1)

        layout.addWidget(make_header_label("FPS (avg)"), 5, 0)
        self.fps_label = make_value_label("—", "#c9d1d9", 12, True)
        layout.addWidget(self.fps_label, 5, 1)

        # Timestamp
        self.network_timestamp = QLabel("")
        self.network_timestamp.setStyleSheet("font-size: 9px; color: #484f58; padding: 2px 0;")
        layout.addWidget(self.network_timestamp, 6, 0, 1, 2)

        layout.setRowStretch(7, 1)
        group.setLayout(layout)
        return group

    def _build_action_panel(self):
        group = QGroupBox("🎮  Player Activity")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("CURRENT ACTION"))
        self.action_label = make_value_label("Unknown", "#ffa657", 13, True)
        layout.addWidget(self.action_label)

        layout.addWidget(make_separator())

        layout.addWidget(make_header_label("LAST PROMPT"))
        self.prompt_label = make_value_label("—", "#d2a8ff", 11)
        layout.addWidget(self.prompt_label)

        layout.addWidget(make_separator())

        layout.addWidget(make_header_label("LAST EVENT"))
        self.last_event_label = make_value_label("—", "#8b949e", 10)
        layout.addWidget(self.last_event_label)

        # Timestamp
        self.activity_timestamp = QLabel("")
        self.activity_timestamp.setStyleSheet("font-size: 9px; color: #484f58; padding: 2px 0;")
        layout.addWidget(self.activity_timestamp)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _build_world_events_panel(self):
        group = QGroupBox("🌩  World Events")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)
        self.world_events_label = make_value_label("No active events", "#8b949e", 11)
        layout.addWidget(self.world_events_label)
        self.world_events_timestamp = QLabel("")
        self.world_events_timestamp.setStyleSheet("font-size: 9px; color: #484f58; padding: 2px 0;")
        layout.addWidget(self.world_events_timestamp)
        layout.addStretch()
        group.setLayout(layout)
        return group

    def _build_ships_panel(self):
        group = QGroupBox("⛵  Ships Nearby")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)
        self.ships_label = make_value_label("No ships detected", "#8b949e", 11)
        layout.addWidget(self.ships_label)
        self.ships_timestamp = QLabel("")
        self.ships_timestamp.setStyleSheet("font-size: 9px; color: #484f58; padding: 2px 0;")
        layout.addWidget(self.ships_timestamp)
        layout.addStretch()
        group.setLayout(layout)
        return group

    def _build_ai_panel(self):
        group = QGroupBox("💀  AI / Enemies")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)
        self.ai_label = make_value_label("No active threats", "#8b949e", 11)
        layout.addWidget(self.ai_label)
        self.ai_timestamp = QLabel("")
        self.ai_timestamp.setStyleSheet("font-size: 9px; color: #484f58; padding: 2px 0;")
        layout.addWidget(self.ai_timestamp)
        layout.addStretch()
        group.setLayout(layout)
        return group

    def _build_entities_panel(self):
        group = QGroupBox("📦  Entities / Loot")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)
        self.entities_label = make_value_label("No entities", "#8b949e", 11)
        layout.addWidget(self.entities_label)
        self.entities_timestamp = QLabel("")
        self.entities_timestamp.setStyleSheet("font-size: 9px; color: #484f58; padding: 2px 0;")
        layout.addWidget(self.entities_timestamp)
        layout.addStretch()
        group.setLayout(layout)
        return group

    # ── Data Update Handlers ─────────────────────────────────────────────
    def update_position(self, data):
        self.pos_x.setText(f"{data['x']:.1f}")
        self.pos_y.setText(f"{data['y']:.1f}")
        self.pos_z.setText(f"{data['z']:.1f}")
        self.pos_x.setStyleSheet("font-size: 11px; color: #7ee787; padding: 1px 0;")
        self.pos_y.setStyleSheet("font-size: 11px; color: #7ee787; padding: 1px 0;")
        self.pos_z.setStyleSheet("font-size: 11px; color: #7ee787; padding: 1px 0;")

        raw_loc = data['location']
        friendly = LOCATION_NAMES.get(raw_loc, raw_loc.replace("_", " ").title())
        self.location_label.setText(friendly)
        self.location_label.setStyleSheet("font-size: 13px; color: #58a6ff; font-weight: bold; padding: 1px 0;")

        # Update timestamp
        self.position_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_network(self, data):
        rtt = data["rtt"]
        rtt_var = data["rtt_var"]

        # Color code ping
        if rtt < 0:
            ping_color = "#8b949e"
            ping_text = "— ms"
        elif rtt <= 60:
            ping_color = "#7ee787"
            ping_text = f"{rtt} ms"
        elif rtt <= 120:
            ping_color = "#ffa657"
            ping_text = f"{rtt} ms"
        else:
            ping_color = "#f85149"
            ping_text = f"{rtt} ms"

        self.ping_label.setText(ping_text)
        self.ping_label.setStyleSheet(f"font-size: 12px; color: {ping_color}; font-weight: bold; padding: 1px 0;")

        self.jitter_label.setText(f"±{rtt_var} ms" if rtt_var >= 0 else "— ms")

        # Packet loss
        out_loss = data["out_loss"]
        in_loss = data["in_loss"]
        if out_loss == 0 and in_loss == 0:
            self.loss_label.setText("0%")
            self.loss_label.setStyleSheet("font-size: 11px; color: #7ee787; padding: 1px 0;")
        else:
            total = max(out_loss, in_loss) * 100
            loss_color = "#ffa657" if total < 5 else "#f85149"
            self.loss_label.setText(f"{total:.1f}%")
            self.loss_label.setStyleSheet(f"font-size: 11px; color: {loss_color}; padding: 1px 0;")

        # Bandwidth
        out_kb = data["out_bps"] / 1024
        in_kb = data["in_bps"] / 1024
        self.bw_label.setText(f"↑{out_kb:.1f} / ↓{in_kb:.1f} KB/s")

        # Update timestamp
        self.network_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_fps(self, data):
        avg_frame = data["avg_frame"]
        if avg_frame > 0:
            fps = 1000.0 / avg_frame
            if fps >= 60:
                color = "#7ee787"
            elif fps >= 30:
                color = "#ffa657"
            else:
                color = "#f85149"
            self.fps_label.setText(f"{fps:.0f}")
            self.fps_label.setStyleSheet(f"font-size: 12px; color: {color}; font-weight: bold; padding: 1px 0;")
        else:
            self.fps_label.setText("—")

    def update_action_state(self, data):
        state_id = data["to"]
        friendly = ACTION_STATES.get(state_id, state_id.replace("ActionStateId", "").replace("Id", ""))
        self.action_label.setText(friendly)

        # Color by activity type
        danger_states = ["DeadActionStateId", "GhostActionStateId", "ReviveableActionStateId",
                        "SinkingTunnelOfTheDamnedActionStateId"]
        active_states = ["UseCannonActionStateId", "HarpoonActionStateId", "FiredFromCannonActionStateId",
                        "DigActionStateId", "FishingActionStateId", "RepairActionStateId", "BailingActionStateId"]
        ship_states = ["ControlWheelActionStateId", "ControlCapstanArmActionStateId", "SailManipulationActionStateId",
                      "ControlPulleyActionStateId"]

        if state_id in danger_states:
            color = "#f85149"
        elif state_id in active_states:
            color = "#f0883e"
        elif state_id in ship_states:
            color = "#58a6ff"
        else:
            color = "#ffa657"
        self.action_label.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: bold; padding: 1px 0;")

        # Update timestamp
        self.activity_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_crew(self, data):
        ship_name = SESSION_SHIP.get(data["session"], data["session"])
        parts = [f"Crew: {data['count']}"]
        if ship_name:
            parts.append(ship_name)
        parts.append(data["type"])
        if data["captained"]:
            parts.append("👑 Captain")
        if data["alliance"]:
            parts.append("🤝 Alliance")
        if data["guild"]:
            parts.append("⚓ Guild")
        self.crew_label.setText("  │  ".join(parts))

    def update_player_ship(self, data):
        size = data.get("size", "")
        if size:
            ship_names = {"Small": "Sloop", "Medium": "Brigantine", "Large": "Galleon"}
            name = ship_names.get(size, size)
            icon = {"Small": "🛶", "Medium": "⛵", "Large": "🚢"}.get(size, "🚢")
            self.ship_type_label.setText(f"{icon} {name}")
            self.ship_type_label.setStyleSheet("font-size: 13px; color: #7ee787; font-weight: bold; padding: 1px 0;")
        else:
            self.ship_type_label.setText("Not on a ship")
            self.ship_type_label.setStyleSheet("font-size: 13px; color: #8b949e; font-weight: bold; padding: 1px 0;")

    def update_companies(self, companies):
        # Clear existing
        for i in reversed(range(self.company_layout.count())):
            w = self.company_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        self.company_bars = {}
        self.company_labels = {}

        row = 0
        for c in companies:
            cid = c["id"]
            info = COMPANY_INFO.get(cid, {"name": cid, "icon": "🏴", "color": "#8b949e"})

            # Name label
            name_lbl = QLabel(f"{info['icon']} {info['name']}")
            name_lbl.setStyleSheet(f"font-size: 11px; color: {info['color']}; font-weight: bold;")
            name_lbl.setMinimumWidth(160)
            self.company_layout.addWidget(name_lbl, row, 0)

            # Level
            lvl_lbl = QLabel(f"Lv. {c['level']}")
            lvl_lbl.setStyleSheet(f"font-size: 11px; color: {info['color']}; font-weight: bold; min-width: 50px;")
            self.company_layout.addWidget(lvl_lbl, row, 1)

            # Progress bar
            bar = QProgressBar()
            bar.setMinimum(0)
            xp_next = c["xp_next"] if c["xp_next"] > 0 else 1
            bar.setMaximum(xp_next)
            bar.setValue(min(c["xp"], xp_next))
            bar.setFormat(f"{c['xp']:,} / {c['xp_next']:,} XP")
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #21262d; border: 1px solid #30363d;
                    border-radius: 3px; height: 16px; text-align: center;
                    font-size: 9px; color: #c9d1d9;
                }}
                QProgressBar::chunk {{
                    background-color: {info['color']}; border-radius: 2px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {info['color']}, stop:1 {info['color']}88);
                }}
            """)
            self.company_layout.addWidget(bar, row, 2)

            self.company_bars[cid] = bar
            self.company_labels[cid] = lvl_lbl
            row += 1

    def update_season(self, data):
        title = data.get("title", "")
        until = data.get("until", "")
        if until:
            try:
                end = datetime.fromisoformat(until.replace("Z", "+00:00"))
                days_left = (end - datetime.now(end.tzinfo)).days
                self.season_label.setText(f"🏴‍☠️ {title}  •  {days_left}d left")
            except Exception:
                self.season_label.setText(f"🏴‍☠️ {title}")
        else:
            self.season_label.setText(f"🏴‍☠️ {title}")

    def update_fire(self, data):
        ships = data["ships"]
        cells = data["cells"]
        if cells > 0:
            self.fire_label.setText(f"🔥 {cells} fire cells on {ships} ship(s)!")
            self.fire_label.setStyleSheet("font-size: 11px; color: #f85149; font-weight: bold; padding: 1px 0;")
        else:
            self.fire_label.setText("No fire")
            self.fire_label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")

    def update_gamemode(self, data):
        mode = data.get("mode", "")
        state = data.get("state", "")
        if mode:
            self.gamemode_label.setText(f"🎮 {mode} — {state}")

    def update_prompt(self, data):
        msg = data.get("message", "")
        if msg:
            self.prompt_label.setText(msg)
            self.prompt_label.setStyleSheet("font-size: 11px; color: #d2a8ff; padding: 1px 0;")
    def update_services(self, data):
        # Keep it compact but informative
        txt = (
            f"{data.get('result','')} • {data.get('total',0):.2f}s  "
            f"(refresh {data.get('refresh',0):.2f}s, token {data.get('token',0):.2f}s)"
        )
        reason = data.get("reason", "")
        stamps = f"stamp {data.get('discovery','')}" if data.get("discovery") else ""
        extra = " — ".join([p for p in [reason, stamps] if p])
        if extra:
            txt = f"{txt}\n{extra}"
        self.services_label.setText(txt)

    def update_boot_error(self, data):
        msg = data.get("message", "").strip()
        if not msg:
            return
        self.boot_error_label.setText(msg)
        self.boot_error_label.setStyleSheet("font-size: 10px; color: #ffa657; padding: 1px 0;")

    def update_ui_screen(self, data):
        cur = data.get("current", "")
        prev = data.get("previous", "")
        if cur:
            self.ui_screen_label.setText(f"{prev} → {cur}" if prev else cur)

    def update_window_status(self, data):
        status = data.get("status", "")
        f = "Focused" if data.get("focused") else "Unfocused"
        m = "Min" if data.get("minimized") else "Norm"
        fs = "FS" if data.get("fullscreen") else "Wnd"
        txt = " • ".join([p for p in [status, f, m, fs] if p])
        self.window_label.setText(txt)

    def update_client_info(self, data):
        build = data.get("build", "")
        play_mode = data.get("play_mode", "")
        state = data.get("state", "")
        rhi = data.get("rhi", "")
        spec = data.get("spec", "")
        fg = data.get("foreground", "")
        txt = " • ".join([p for p in [f"Build {build}" if build else "", play_mode, state, rhi, f"Spec {spec}" if spec else "", f"FG {fg}" if fg else ""] if p])
        self.client_info_label.setText(txt)

    def update_movement_base(self, data):
        prev = data.get("from", "")
        new = data.get("to", "")
        if prev or new:
            self.movement_base_label.setText(f"{prev} → {new}" if prev else new)


    def update_world_events(self, events):
        if events:
            lines = []
            for event in events:
                if ':' in event:
                    name, count = event.split(':', 1)
                    readable = name.replace('_', ' ').replace('Ghostship Flameheart Cloud', 'Flameheart')
                    icons = {
                        "SkullCloud": "💀☁", "AshenLordCloud": "🔥☁", "ShipCloud": "🚢☁",
                        "Ghostship_Flameheart_Cloud": "👻☁", "Storm": "⛈️", "FogBank": "🌫️",
                        "Volcano": "🌋", "Earthquake": "🌍", "Geyser": "💨",
                        "SuperHeatedWater": "♨️", "Haunted_Fort": "🏰", "Spire": "🗼",
                        "SkeletonThrone": "🦴", "Shipwreck": "🚢", "Shipwreck_Graveyard": "⚓",
                        "Shipwreck_Smuggler": "🗝️", "BarrelsOfPlenty": "🛢️",
                        "Jettisoned_Supplies": "📦", "MessageInABottle": "🍾",
                        "WreckDebris_Land": "🪵", "WreckDebris_Sea": "🌊", "Mermaid": "🧜",
                    }
                    icon = icons.get(name, "⚡")
                    lines.append(f"{icon} {readable} ({count})")
            self.world_events_label.setText("\n".join(lines) if lines else "No active events")
            if lines:
                self.world_events_label.setStyleSheet("font-size: 11px; color: #7ee787; padding: 1px 0;")
            else:
                self.world_events_label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")
            self.world_events_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
        else:
            self.world_events_label.setText("No active events")
            self.world_events_label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")
            self.world_events_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_ships(self, ships):
        if ships:
            lines = []
            for ship in ships:
                if ':' in ship:
                    name, count = ship.split(':', 1)
                    count = int(count)
                    if name == "Ship_Small":
                        lines.append(f"🛶 Sloop × {count}")
                    elif name == "Ship_Medium":
                        lines.append(f"⛵ Brigantine × {count}")
                    elif name == "Ship_Large":
                        lines.append(f"🚢 Galleon × {count}")
                    elif "AI_Ship" in name:
                        ai_type = name.replace("AI_Ship_", "").replace("_", " ")
                        lines.append(f"🏴‍☠️ AI {ai_type} × {count}")
                    elif "Rowboat" in name:
                        rb_type = name.replace("Rowboat_", "").replace("Rowboat", "Standard")
                        lines.append(f"🚣 {rb_type} Rowboat × {count}")
                    else:
                        lines.append(f"❓ {name} × {count}")
            self.ships_label.setText("\n".join(lines))
            self.ships_label.setStyleSheet("font-size: 11px; color: #58a6ff; padding: 1px 0;")
            self.ships_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
        else:
            self.ships_label.setText("No ships detected")
            self.ships_label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")
            self.ships_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_ship_systems(self, systems):
        if systems:
            lines = []

            system_icons = {
                "Sails": "⛵ Sails",
                "Cannons": "💣 Cannons",
                "Wheel": "🎡 Wheel",
                "Capstan": "⚓ Anchor",
                "Rudder": "📐 Rudder",
                "Harpoon": "🪝 Harpoon",
            }

            for system in systems:
                # Skip inaccurate data: Mast, HullDamage, Water, SINKING
                if system in ["SINKING", "Mast"] or system.startswith("Water:") or system.startswith("HullDamage:"):
                    continue

                if system in system_icons:
                    lines.append(system_icons[system])
                else:
                    lines.append(f"• {system}")

            if lines:
                self.ship_systems_label.setText("\n".join(lines))
                self.ship_systems_label.setStyleSheet(
                    "font-size: 11px; color: #7ee787; padding: 1px 0;")
            else:
                self.ship_systems_label.setText("No active systems")
                self.ship_systems_label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")
        else:
            self.ship_systems_label.setText("No active systems")
            self.ship_systems_label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")

    def update_ai_entities(self, ai_list):
        if ai_list:
            lines = []
            ai_icons = {
                "AI_Skeleton": "💀 Skeleton", "AI_Phantom": "👻 Phantom",
                "AI_Shark": "🦈 Shark", "AI_Megalodon": "🦈 Megalodon",
                "AI_Megalodon_Ancient": "🦈 Ancient Meg", "AI_Megalodon_OnDemand": "🦈 Summoned Meg",
                "AI_Kraken": "🐙 Kraken", "AI_Kraken_Tiny": "🐙 Baby Kraken",
                "AI_SwimmingCreature": "🐠 Sea Creature",
                "AI_GhostShip_Captain": "👻 Ghost Captain", "AI_GhostShip_MiniBoss": "👻 Ghost MiniBoss",
                "AI_GhostShip_Grunt": "👻 Ghost Ship",
                "AI_OceanCrawler_Crab": "🦀 Crab", "AI_OceanCrawler_Eel": "🐍 Eel",
                "AI_OceanCrawler_Hermit": "🐚 Hermit",
                "AI_Siren": "🧜‍♀️ Siren",
                "AI_Fauna": "🐔 Fauna", "AI_Pets": "🐕 Pet", "AI_Pets_Wielded": "🐕 Pet (held)",
                "FishingFish": "🐟 Fish",
            }
            for ai in ai_list:
                if ':' in ai:
                    name, count = ai.split(':', 1)
                    friendly = ai_icons.get(name, name.replace("AI_", "").replace("_", " "))
                    lines.append(f"{friendly} × {count}")
            self.ai_label.setText("\n".join(lines))

            # Red if threats present, muted if just fauna/pets
            has_threats = any(not any(p in ai for p in ["Fauna", "Pets", "Fish"]) for ai in ai_list)
            color = "#f85149" if has_threats else "#8b949e"
            self.ai_label.setStyleSheet(f"font-size: 11px; color: {color}; padding: 1px 0;")
            self.ai_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
        else:
            self.ai_label.setText("No active threats")
            self.ai_label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")
            self.ai_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_entities(self, entities):
        if entities:
            lines = []
            entity_icons = {
                "Player": "👤 Player", "NPC": "🧑‍🌾 NPC", "GoalDrivenCharacter": "🧑 Character",
                "Mercenary": "⚔️ Mercenary", "MercenarySpawner": "⚔️ Merc Spawner",
                "ReapersChestMercenary": "☠️ Reaper Merc",
                "Booty": "💰 Treasure", "Booty_AshenWindsSkull": "🔥 Ashen Skull",
                "Booty_CaptainsLog": "📖 Captain's Log", "Booty_ReapersChest": "☠️ Reaper's Chest",
                "Booty_RuinedCaptainsLog": "📜 Ruined Log",
                "Consumable": "🍌 Consumable", "GoldCoin": "🪙 Gold",
                "Pouch_Ammo": "🔫 Ammo", "Pouch_Doubloons": "🪙 Doubloons", "Pouch_Gold": "💰 Gold Pouch",
                "HuntingSpear": "🔱 Spear", "BlowpipeDart": "🎯 Dart",
                "StorageContainer": "📦 Storage", "StorageContainerBuoyant": "📦 Floating Storage",
                "Mechanism": "⚙️ Mechanism", "Mechanism_OneShot": "⚙️ Trap Mechanism",
                "Trap": "🪤 Trap", "StatueThreat": "🗿 Coral Statue",
                "FireworkExplosion": "🎆 Firework", "FireworkProjectile": "🎇 Firework",
            }
            for entity in entities:
                if ':' in entity:
                    name, count = entity.split(':', 1)
                    friendly = entity_icons.get(name, name.replace("_", " "))
                    lines.append(f"{friendly} × {count}")
            self.entities_label.setText("\n".join(lines))
            self.entities_label.setStyleSheet("font-size: 11px; color: #58a6ff; padding: 1px 0;")
            self.entities_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
        else:
            self.entities_label.setText("No entities")
            self.entities_label.setStyleSheet("font-size: 11px; color: #8b949e; padding: 1px 0;")
            self.entities_timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_event(self, event_name):
        ts = datetime.now().strftime("%H:%M:%S")
        # Skip noisy perf events from the history display
        noisy = ["ClientPerformanceTelemetryEvent", "MeshMemoryConstraint",
                 "AsyncExcessiveLoad", "PopUpQueueService"]
        if any(n in event_name for n in noisy):
            if hasattr(self, 'last_event_label'):

                self.last_event_label.setText(f"[{ts}] {event_name}")
            return

        entry = f"<span style='color:#484f58'>[{ts}]</span> <span style='color:#c9d1d9'>{event_name}</span>"
        self.event_history.insert(0, entry)
        if len(self.event_history) > self.max_event_history:
            self.event_history = self.event_history[:self.max_event_history]

        self.event_log.setHtml("<br>".join(self.event_history))
        if hasattr(self, "last_event_label"):
            self.last_event_label.setText(f"[{ts}] {event_name}")

    # ── Setup / Proxy Control ────────────────────────────────────────────
    def check_setup(self):
        if not setup_mitmproxy():
            QMessageBox.warning(self, "mitmproxy Not Installed",
                                "mitmproxy is not installed.\nPlease run: pip install mitmproxy")
            self.log("ERROR: mitmproxy not installed")
            return

        if not check_certificate():
            QMessageBox.warning(self, "Certificate Not Found",
                                "mitmproxy certificate not found.\n\n"
                                "Please run 'mitmdump' once, then visit http://mitm.it\n"
                                "and install the certificate for Windows.")
            self.log("WARNING: Certificate not found at ~/.mitmproxy/")
        else:
            self.log("Certificate found — ready to capture")

        app_dir = get_app_dir()
        addon_path = os.path.join(app_dir, "game_capture.py")
        if os.path.exists(addon_path):
            self.log(f"Addon found: {addon_path}")
        else:
            self.log(f"WARNING: game_capture.py not found in {app_dir}")
            QMessageBox.warning(self, "Missing File",
                                f"game_capture.py not found!\n\nPlace it in:\n{app_dir}")

    def log(self, message):
        self.console.append(message)

    def start_proxy(self):
        if self.proxy_running:
            return

        try:
            set_system_proxy(True)
            self.log("System proxy enabled (127.0.0.1:8080)")

            self.proxy_thread = ProxyThread()
            self.proxy_thread.output.connect(self.log)
            self.proxy_thread.position_update.connect(self.update_position)
            self.proxy_thread.world_events_update.connect(self.update_world_events)
            self.proxy_thread.ships_update.connect(self.update_ships)
            self.proxy_thread.ai_entities_update.connect(self.update_ai_entities)
            self.proxy_thread.entities_update.connect(self.update_entities)
            self.proxy_thread.event_captured.connect(self.update_event)
            self.proxy_thread.network_update.connect(self.update_network)
            self.proxy_thread.fps_update.connect(self.update_fps)
            self.proxy_thread.action_state_update.connect(self.update_action_state)
            self.proxy_thread.crew_update.connect(self.update_crew)
            self.proxy_thread.company_update.connect(self.update_companies)
            self.proxy_thread.season_update.connect(self.update_season)
            self.proxy_thread.fire_update.connect(self.update_fire)
            self.proxy_thread.gamemode_update.connect(self.update_gamemode)
            self.proxy_thread.prompt_update.connect(self.update_prompt)
            self.proxy_thread.services_update.connect(self.update_services)
            self.proxy_thread.boot_error_update.connect(self.update_boot_error)
            self.proxy_thread.ui_screen_update.connect(self.update_ui_screen)
            self.proxy_thread.window_update.connect(self.update_window_status)
            self.proxy_thread.client_update.connect(self.update_client_info)
            self.proxy_thread.movement_base_update.connect(self.update_movement_base)
            self.proxy_thread.finished_signal.connect(self.on_proxy_finished)
            self.proxy_thread.start()

            self.proxy_running = True
            self.status_label.setText("  ● CAPTURING  ")
            self.status_label.setStyleSheet(
                "font-size: 11px; font-weight: bold; color: #7ee787; "
                "background-color: #1a3a25; border: 1px solid #2ea043; "
                "border-radius: 10px; padding: 3px 10px;")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            self.log("Proxy started — Launch Sea of Thieves!")
            self.log(f"Logs saved to: {self.log_file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start proxy:\n{str(e)}")
            self.log(f"ERROR: {str(e)}")
            set_system_proxy(False)

    def stop_proxy(self):
        if not self.proxy_running:
            return

        self.log("Stopping proxy...")
        if self.proxy_thread:
            self.proxy_thread.stop()
            self.proxy_thread.wait()

        set_system_proxy(False)
        self.log("System proxy disabled")

        self.proxy_running = False
        self.status_label.setText("  ● OFFLINE  ")
        self.status_label.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #f85149; "
            "background-color: #3d1518; border: 1px solid #f85149; "
            "border-radius: 10px; padding: 3px 10px;")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log("Proxy stopped")

    def on_proxy_finished(self):
        if self.proxy_running:
            self.stop_proxy()

    def closeEvent(self, event):
        self.log("Closing — disabling proxy...")
        if self.proxy_running:
            self.stop_proxy()
        else:
            set_system_proxy(False)
        event.accept()

    def __del__(self):
        try:
            set_system_proxy(False)
        except Exception:
            pass


# ─── Entry Point ─────────────────────────────────────────────────────────────
def main():
    print("Disabling proxy on startup...")
    set_system_proxy(False)

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    app.aboutToQuit.connect(lambda: set_system_proxy(False))

    window = MainWindow()
    window.show()

    exit_code = app.exec()

    print("Final proxy disable...")
    set_system_proxy(False)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()