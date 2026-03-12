"""Main application window — assembles panels and wires proxy signals."""

import os
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QGroupBox, QGridLayout,
    QScrollArea, QProgressBar, QSplitter, QTabWidget, QMessageBox,
)
from PySide6.QtCore import Qt

from sot_client_scanner.constants.companies import COMPANY_INFO
from sot_client_scanner.proxy.thread import ProxyThread
from sot_client_scanner.utils.app import get_project_root, setup_mitmproxy, check_certificate
from sot_client_scanner.utils.proxy_control import set_system_proxy
from sot_client_scanner.ui.panels import (
    PositionPanel, NetworkPanel, ShipInfoPanel, SessionPanel,
    StatusPanel, WorldEventsPanel, ShipsPanel, AIPanel, EntitiesPanel,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.proxy_thread = None
        self.proxy_running = False
        self._stopping = False
        self.log_file_path = os.path.join(get_project_root(), "logs", "sea_of_thieves_capture.txt")
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

        title = QLabel("Sea of Thieves Telemetry")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #f4f4f5; padding: 4px 0; letter-spacing: 0.5px;")
        top_bar.addWidget(title)
        top_bar.addStretch()

        self.status_label = QLabel("  OFFLINE  ")
        self.status_label.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #ef4444; "
            "background-color: #1c0d0e; border: 1px solid #ef4444; "
            "border-radius: 10px; padding: 4px 12px; letter-spacing: 1px;")
        top_bar.addWidget(self.status_label)

        self.gamemode_label = QLabel("")
        self.gamemode_label.setStyleSheet("font-size: 11px; color: #a1a1aa; padding: 3px 6px;")
        top_bar.addWidget(self.gamemode_label)

        self.season_label = QLabel("")
        self.season_label.setStyleSheet("font-size: 11px; color: #a1a1aa; padding: 3px 6px;")
        top_bar.addWidget(self.season_label)

        root.addLayout(top_bar)

        # ── Dashboard Panels ─────────────────────────────────────────────
        splitter = QSplitter(Qt.Vertical)

        dashboard = QWidget()
        dash_layout = QVBoxLayout(dashboard)
        dash_layout.setContentsMargins(0, 0, 0, 0)
        dash_layout.setSpacing(6)

        # Row 1
        self.position_panel = PositionPanel()
        self.network_panel = NetworkPanel()
        self.ship_panel = ShipInfoPanel()
        self.session_panel = SessionPanel()
        self.status_panel = StatusPanel()

        row1 = QHBoxLayout()
        row1.setSpacing(6)
        row1.addWidget(self.position_panel, 1)
        row1.addWidget(self.network_panel, 1)
        row1.addWidget(self.ship_panel, 1)
        row1.addWidget(self.session_panel, 1)
        row1.addWidget(self.status_panel, 1)
        dash_layout.addLayout(row1)

        # Row 2
        self.world_events_panel = WorldEventsPanel()
        self.ships_panel = ShipsPanel()
        self.ai_panel = AIPanel()
        self.entities_panel = EntitiesPanel()

        row2 = QHBoxLayout()
        row2.setSpacing(6)
        row2.addWidget(self.world_events_panel, 1)
        row2.addWidget(self.ships_panel, 1)
        row2.addWidget(self.ai_panel, 1)
        row2.addWidget(self.entities_panel, 1)
        dash_layout.addLayout(row2)

        splitter.addWidget(dashboard)

        # ── Bottom Tabs ──────────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setMaximumHeight(220)

        # Event History Tab
        event_tab = QWidget()
        et_layout = QVBoxLayout(event_tab)
        et_layout.setContentsMargins(4, 4, 4, 4)
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setStyleSheet(
            "background-color: #0a0e14; color: #d4d4d8; font-family: 'Cascadia Code', 'Consolas', monospace; "
            "font-size: 11px; border: none;")
        et_layout.addWidget(self.event_log)
        tabs.addTab(event_tab, "Event Log")

        # Companies Tab
        company_tab = QWidget()
        ct_layout = QVBoxLayout(company_tab)
        ct_layout.setContentsMargins(4, 4, 4, 4)
        self.company_widget = QWidget()
        self.company_layout = QGridLayout(self.company_widget)
        self.company_layout.setSpacing(4)
        self.company_layout.setContentsMargins(0, 0, 0, 0)
        self.company_bars = {}
        self.company_labels = {}
        self._company_name_labels = {}

        scroll = QScrollArea()
        scroll.setWidget(self.company_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        ct_layout.addWidget(scroll)
        tabs.addTab(company_tab, "Companies")

        # Console Tab
        console_tab = QWidget()
        con_layout = QVBoxLayout(console_tab)
        con_layout.setContentsMargins(4, 4, 4, 4)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(
            "background-color: #0a0e14; color: #a3e635; font-family: 'Cascadia Code', 'Consolas', monospace; "
            "font-size: 10px; border: none;")
        con_layout.addWidget(self.console)
        tabs.addTab(console_tab, "Console")

        splitter.addWidget(tabs)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter)

        # ── Button Bar ───────────────────────────────────────────────────
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        self.start_button = QPushButton("Start Capture")
        self.start_button.setObjectName("startBtn")
        self.start_button.setMinimumHeight(36)
        self.start_button.clicked.connect(self.start_proxy)
        btn_bar.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Capture")
        self.stop_button.setObjectName("stopBtn")
        self.stop_button.setMinimumHeight(36)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_proxy)
        btn_bar.addWidget(self.stop_button)

        btn_bar.addStretch()

        self.crew_label = QLabel("")
        self.crew_label.setStyleSheet("font-size: 11px; color: #a1a1aa; padding: 0 8px;")
        btn_bar.addWidget(self.crew_label)

        root.addLayout(btn_bar)

        # Run initial checks
        self.check_setup()

    # ── Setup ────────────────────────────────────────────────────────────
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

        app_dir = get_project_root()
        addon_path = os.path.join(app_dir, "game_capture.py")
        if os.path.exists(addon_path):
            self.log(f"Addon found: {addon_path}")
        else:
            self.log(f"WARNING: game_capture.py not found in {app_dir}")
            QMessageBox.warning(self, "Missing File",
                                f"game_capture.py not found!\n\nPlace it in:\n{app_dir}")

    def log(self, message):
        self.console.append(message)

    # ── Proxy Control ────────────────────────────────────────────────────
    def start_proxy(self):
        if self.proxy_running:
            return

        try:
            set_system_proxy(True)
            self.log("System proxy enabled (127.0.0.1:8080)")

            self.proxy_thread = ProxyThread()

            # Wire signals → panel update methods
            self.proxy_thread.output.connect(self.log)
            self.proxy_thread.position_update.connect(self.position_panel.update_data)
            self.proxy_thread.network_update.connect(self.network_panel.update_network)
            self.proxy_thread.fps_update.connect(self.network_panel.update_fps)
            self.proxy_thread.player_ship_update.connect(self.ship_panel.update_player_ship)
            self.proxy_thread.ship_systems_update.connect(self.ship_panel.update_ship_systems)
            self.proxy_thread.action_state_update.connect(self.session_panel.update_action_state)
            self.proxy_thread.crew_update.connect(self._on_crew_update)
            self.proxy_thread.fire_update.connect(self.session_panel.update_fire)
            self.proxy_thread.prompt_update.connect(self.session_panel.update_prompt)
            self.proxy_thread.movement_base_update.connect(self.session_panel.update_movement_base)
            self.proxy_thread.services_update.connect(self.status_panel.update_services)
            self.proxy_thread.boot_error_update.connect(self.status_panel.update_boot_error)
            self.proxy_thread.ui_screen_update.connect(self.status_panel.update_ui_screen)
            self.proxy_thread.window_update.connect(self.status_panel.update_window_status)
            self.proxy_thread.client_update.connect(self.status_panel.update_client_info)
            self.proxy_thread.world_events_update.connect(self.world_events_panel.update_data)
            self.proxy_thread.ships_update.connect(self.ships_panel.update_data)
            self.proxy_thread.ai_entities_update.connect(self.ai_panel.update_data)
            self.proxy_thread.entities_update.connect(self.entities_panel.update_data)
            self.proxy_thread.event_captured.connect(self.update_event)
            self.proxy_thread.company_update.connect(self.update_companies)
            self.proxy_thread.season_update.connect(self.update_season)
            self.proxy_thread.gamemode_update.connect(self.update_gamemode)
            self.proxy_thread.finished_signal.connect(self.on_proxy_finished)

            self.proxy_thread.start()

            self.proxy_running = True
            self.status_label.setText("  CAPTURING  ")
            self.status_label.setStyleSheet(
                "font-size: 11px; font-weight: 700; color: #a3e635; "
                "background-color: #0f291a; border: 1px solid #22c55e; "
                "border-radius: 10px; padding: 4px 12px; letter-spacing: 1px;")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            self.log("Proxy started — Launch Sea of Thieves!")
            self.log(f"Logs saved to: {self.log_file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start proxy:\n{str(e)}")
            self.log(f"ERROR: {str(e)}")
            set_system_proxy(False)

    def stop_proxy(self):
        if not self.proxy_running or self._stopping:
            return

        self._stopping = True
        self.log("Stopping proxy...")
        if self.proxy_thread:
            self.proxy_thread.stop()
            if not self.proxy_thread.wait(5000):
                self.log("WARNING: Proxy thread did not stop in time, forcing termination")
                self.proxy_thread.terminate()
                self.proxy_thread.wait(2000)

        set_system_proxy(False)
        self.log("System proxy disabled")

        self.proxy_running = False
        self.status_label.setText("  OFFLINE  ")
        self.status_label.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #ef4444; "
            "background-color: #1c0d0e; border: 1px solid #ef4444; "
            "border-radius: 10px; padding: 4px 12px; letter-spacing: 1px;")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log("Proxy stopped")
        self._stopping = False

    def on_proxy_finished(self):
        if self.proxy_running and not self._stopping:
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

    # ── Handlers that live in MainWindow (cross-panel or top-bar) ────────
    def _on_crew_update(self, data):
        """Update both the session panel and the bottom-bar crew label."""
        crew_text = self.session_panel.update_crew(data)
        self.crew_label.setText(crew_text)

    def update_season(self, data):
        title = data.get("title", "")
        until = data.get("until", "")
        if until:
            try:
                end = datetime.fromisoformat(until.replace("Z", "+00:00"))
                days_left = (end - datetime.now(end.tzinfo)).days
                self.season_label.setText(f"{title}  ·  {days_left}d left")
            except Exception:
                self.season_label.setText(title)
        else:
            self.season_label.setText(title)

    def update_gamemode(self, data):
        mode = data.get("mode", "")
        state = data.get("state", "")
        if mode:
            self.gamemode_label.setText(f"{mode} — {state}")

    def update_event(self, event_name):
        ts = datetime.now().strftime("%H:%M:%S")
        noisy = ["ClientPerformanceTelemetryEvent", "MeshMemoryConstraint",
                  "AsyncExcessiveLoad", "PopUpQueueService"]
        if any(n in event_name for n in noisy):
            self.session_panel.update_event(event_name)
            return

        entry = f"<span style='color:#3f3f46'>[{ts}]</span> <span style='color:#d4d4d8'>{event_name}</span>"
        self.event_history.insert(0, entry)
        if len(self.event_history) > self.max_event_history:
            self.event_history = self.event_history[:self.max_event_history]

        self.event_log.setHtml("<br>".join(self.event_history))
        self.session_panel.update_event(event_name)

    def update_companies(self, companies):
        # Build a set of company IDs in this update
        incoming_ids = {c["id"] for c in companies}

        # Remove rows for companies no longer present
        for cid in list(self.company_bars.keys()):
            if cid not in incoming_ids:
                # Find and remove widgets for this row
                bar = self.company_bars.pop(cid, None)
                lbl = self.company_labels.pop(cid, None)
                name_lbl = self._company_name_labels.pop(cid, None)
                for w in (bar, lbl, name_lbl):
                    if w:
                        w.deleteLater()

        for c in companies:
            cid = c["id"]
            info = COMPANY_INFO.get(cid, {"name": cid, "color": "#71717a"})
            xp_next = c["xp_next"] if c["xp_next"] > 0 else 1

            if cid in self.company_bars:
                # Update existing widgets in-place
                self.company_bars[cid].setMaximum(xp_next)
                self.company_bars[cid].setValue(min(c["xp"], xp_next))
                self.company_bars[cid].setFormat(f"{c['xp']:,} / {c['xp_next']:,} XP")
                self.company_labels[cid].setText(f"Lv. {c['level']}")
            else:
                # Create new row
                row = self.company_layout.rowCount()

                name_lbl = QLabel(info['name'])
                name_lbl.setStyleSheet(f"font-size: 11px; color: {info['color']}; font-weight: bold;")
                name_lbl.setMinimumWidth(160)
                self.company_layout.addWidget(name_lbl, row, 0)

                lvl_lbl = QLabel(f"Lv. {c['level']}")
                lvl_lbl.setStyleSheet(f"font-size: 11px; color: {info['color']}; font-weight: bold; min-width: 50px;")
                self.company_layout.addWidget(lvl_lbl, row, 1)

                bar = QProgressBar()
                bar.setMinimum(0)
                bar.setMaximum(xp_next)
                bar.setValue(min(c["xp"], xp_next))
                bar.setFormat(f"{c['xp']:,} / {c['xp_next']:,} XP")
                bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: #1c2028; border: 1px solid #1e2733;
                        border-radius: 4px; height: 16px; text-align: center;
                        font-size: 9px; color: #d4d4d8;
                    }}
                    QProgressBar::chunk {{
                        background-color: {info['color']}; border-radius: 3px;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {info['color']}, stop:1 {info['color']}88);
                    }}
                """)
                self.company_layout.addWidget(bar, row, 2)

                self.company_bars[cid] = bar
                self.company_labels[cid] = lvl_lbl
                if not hasattr(self, '_company_name_labels'):
                    self._company_name_labels = {}
                self._company_name_labels[cid] = name_lbl
