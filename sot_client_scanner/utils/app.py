"""Application-level helpers: paths, mitmproxy detection, certificate check."""

import sys
import os
from pathlib import Path


def get_app_dir():
    """Return the directory where the application is running from."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def get_project_root():
    """Return the project root directory (parent of sot_client_scanner/).

    __file__ = sot_client_scanner/utils/app.py
    → dirname × 3 = project root
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def setup_mitmproxy():
    """Check whether mitmproxy is importable."""
    try:
        import mitmproxy  # noqa: F401
        return True
    except ImportError:
        return False


def check_certificate():
    """Check whether the mitmproxy CA certificate exists."""
    cert_path = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.cer"
    return cert_path.exists()
