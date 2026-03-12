"""Status / Services panel."""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout

from sot_client_scanner.ui.helpers import make_value_label, make_header_label, make_separator


class StatusPanel(QGroupBox):
    """Displays UI screen, window state, services connection, client info, and boot errors."""

    def __init__(self):
        super().__init__("Status / Services")
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("UI SCREEN"))
        self.ui_screen_label = make_value_label("—", "#71717a", 11)
        layout.addWidget(self.ui_screen_label)

        layout.addWidget(make_header_label("WINDOW"))
        self.window_label = make_value_label("—", "#71717a", 11)
        layout.addWidget(self.window_label)

        layout.addWidget(make_separator())

        layout.addWidget(make_header_label("SERVICES CONNECT"))
        self.services_label = make_value_label("—", "#71717a", 10)
        self.services_label.setWordWrap(True)
        layout.addWidget(self.services_label)

        layout.addWidget(make_header_label("CLIENT"))
        self.client_info_label = make_value_label("—", "#71717a", 10)
        self.client_info_label.setWordWrap(True)
        layout.addWidget(self.client_info_label)

        layout.addWidget(make_header_label("LAST ERROR"))
        self.boot_error_label = make_value_label("—", "#71717a", 10)
        self.boot_error_label.setWordWrap(True)
        layout.addWidget(self.boot_error_label)

        layout.addStretch()
        self.setLayout(layout)

    def update_services(self, data):
        """Handle a services_update signal."""
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
        """Handle a boot_error_update signal."""
        msg = data.get("message", "").strip()
        if not msg:
            return
        self.boot_error_label.setText(msg)
        self.boot_error_label.setStyleSheet("font-size: 10px; color: #ffa657; padding: 1px 0;")

    def update_ui_screen(self, data):
        """Handle a ui_screen_update signal."""
        cur = data.get("current", "")
        prev = data.get("previous", "")
        if cur:
            self.ui_screen_label.setText(f"{prev} → {cur}" if prev else cur)

    def update_window_status(self, data):
        """Handle a window_update signal."""
        status = data.get("status", "")
        f = "Focused" if data.get("focused") else "Unfocused"
        m = "Min" if data.get("minimized") else "Norm"
        fs = "FS" if data.get("fullscreen") else "Wnd"
        txt = " • ".join([p for p in [status, f, m, fs] if p])
        self.window_label.setText(txt)

    def update_client_info(self, data):
        """Handle a client_update signal."""
        build = data.get("build", "")
        play_mode = data.get("play_mode", "")
        state = data.get("state", "")
        rhi = data.get("rhi", "")
        spec = data.get("spec", "")
        fg = data.get("foreground", "")
        txt = " • ".join([
            p for p in [
                f"Build {build}" if build else "",
                play_mode, state, rhi,
                f"Spec {spec}" if spec else "",
                f"FG {fg}" if fg else "",
            ] if p
        ])
        self.client_info_label.setText(txt)
