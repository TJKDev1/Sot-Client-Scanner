"""Network & Performance panel."""

from datetime import datetime

from PySide6.QtWidgets import QGroupBox, QGridLayout, QLabel

from sot_client_scanner.ui.helpers import make_value_label, make_header_label, make_separator


class NetworkPanel(QGroupBox):
    """Displays ping, jitter, packet loss, bandwidth, and FPS."""

    def __init__(self):
        super().__init__("Network & Performance")
        layout = QGridLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(make_header_label("PING"), 0, 0)
        self.ping_label = make_value_label("— ms", "#d4d4d8", 12, True)
        layout.addWidget(self.ping_label, 0, 1)

        layout.addWidget(make_header_label("JITTER"), 1, 0)
        self.jitter_label = make_value_label("— ms", "#71717a", 11)
        layout.addWidget(self.jitter_label, 1, 1)

        layout.addWidget(make_header_label("PACKET LOSS"), 2, 0)
        self.loss_label = make_value_label("—", "#71717a", 11)
        layout.addWidget(self.loss_label, 2, 1)

        layout.addWidget(make_separator(), 3, 0, 1, 2)

        layout.addWidget(make_header_label("BANDWIDTH"), 4, 0)
        self.bw_label = make_value_label("— / —", "#71717a", 11)
        layout.addWidget(self.bw_label, 4, 1)

        layout.addWidget(make_header_label("FPS (avg)"), 5, 0)
        self.fps_label = make_value_label("—", "#d4d4d8", 12, True)
        layout.addWidget(self.fps_label, 5, 1)

        self.timestamp = QLabel("")
        self.timestamp.setStyleSheet("font-size: 9px; color: #3f3f46; padding: 2px 0;")
        layout.addWidget(self.timestamp, 6, 0, 1, 2)

        layout.setRowStretch(7, 1)
        self.setLayout(layout)

    def update_network(self, data):
        """Handle a network_update signal."""
        rtt = data["rtt"]
        rtt_var = data["rtt_var"]

        if rtt < 0:
            ping_color = "#71717a"
            ping_text = "— ms"
        elif rtt <= 60:
            ping_color = "#a3e635"
            ping_text = f"{rtt} ms"
        elif rtt <= 120:
            ping_color = "#fbbf24"
            ping_text = f"{rtt} ms"
        else:
            ping_color = "#ef4444"
            ping_text = f"{rtt} ms"

        self.ping_label.setText(ping_text)
        self.ping_label.setStyleSheet(f"font-size: 12px; color: {ping_color}; font-weight: bold; padding: 2px 0;")

        self.jitter_label.setText(f"±{rtt_var} ms" if rtt_var >= 0 else "— ms")

        out_loss = data["out_loss"]
        in_loss = data["in_loss"]
        if out_loss == 0 and in_loss == 0:
            self.loss_label.setText("0%")
            self.loss_label.setStyleSheet("font-size: 11px; color: #a3e635; padding: 2px 0;")
        else:
            total = max(out_loss, in_loss) * 100
            loss_color = "#fbbf24" if total < 5 else "#ef4444"
            self.loss_label.setText(f"{total:.1f}%")
            self.loss_label.setStyleSheet(f"font-size: 11px; color: {loss_color}; padding: 2px 0;")

        out_kb = data["out_bps"] / 1024
        in_kb = data["in_bps"] / 1024
        self.bw_label.setText(f"↑{out_kb:.1f} / ↓{in_kb:.1f} KB/s")

        self.timestamp.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def update_fps(self, data):
        """Handle an fps_update signal."""
        avg_frame = data["avg_frame"]
        if avg_frame > 0:
            fps = 1000.0 / avg_frame
            if fps >= 60:
                color = "#a3e635"
            elif fps >= 30:
                color = "#fbbf24"
            else:
                color = "#ef4444"
            self.fps_label.setText(f"{fps:.0f}")
            self.fps_label.setStyleSheet(f"font-size: 12px; color: {color}; font-weight: bold; padding: 2px 0;")
        else:
            self.fps_label.setText("—")
