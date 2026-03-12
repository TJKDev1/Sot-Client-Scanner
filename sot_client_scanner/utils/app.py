"""Application-level helpers: paths, mitmproxy detection, certificate check."""

import sys
from pathlib import Path


def get_project_root():
    """Return the project root directory (parent of sot_client_scanner/).

    When running from a frozen executable (PyInstaller / cx_Freeze), uses
    the directory containing the .exe.  Otherwise walks up from __file__.
    """
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).parent)
    return str(Path(__file__).parents[2])


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
