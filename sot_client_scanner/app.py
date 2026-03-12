"""Application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from sot_client_scanner.ui.style import DARK_STYLE
from sot_client_scanner.ui.main_window import MainWindow
from sot_client_scanner.utils.proxy_control import set_system_proxy, install_safety_handlers


def main():
    """Launch the Sea of Thieves Telemetry Reader."""
    install_safety_handlers()

    if sys.platform == "win32":
        print("Disabling proxy on startup...")
        set_system_proxy(False)

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    app.aboutToQuit.connect(lambda: set_system_proxy(False))

    window = MainWindow()
    window.show()

    exit_code = app.exec()

    if sys.platform == "win32":
        print("Final proxy disable...")
        set_system_proxy(False)
    sys.exit(exit_code)
