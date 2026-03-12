"""System proxy control and emergency shutdown handlers."""

import sys
import atexit
import signal


def set_system_proxy(enable=True):
    """Enable or disable the Windows system proxy pointing at 127.0.0.1:8080."""
    if sys.platform == "win32":
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0, winreg.KEY_WRITE,
            )
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
    print("WARNING: Proxy control is only supported on Windows")
    return False


def emergency_disable_proxy():
    """Last-resort proxy disable for unexpected shutdowns."""
    print("EMERGENCY: Disabling proxy...")
    set_system_proxy(False)


def install_safety_handlers():
    """Register atexit and signal handlers that always disable the proxy on exit."""
    atexit.register(emergency_disable_proxy)

    def _signal_handler(signum, frame):
        print(f"Received signal {signum}, disabling proxy...")
        emergency_disable_proxy()
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, _signal_handler)
