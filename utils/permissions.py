from __future__ import annotations

import os
import sys
from pathlib import Path


def is_root() -> bool:
    """Return True if the process has elevated / admin privileges."""
    if sys.platform == "win32":
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    # Linux / macOS
    return os.geteuid() == 0


def can_write(path: Path) -> bool:
    return os.access(path, os.W_OK)


def require_root_for_device(device: Path) -> str | None:
    """Return an error string if elevation is missing, else None."""
    if not is_root():
        app_name = "AufurWizard"
        if sys.platform == "win32":
            return (
                f"Wiping '{device}' requires Administrator privileges.\n"
                f"Right-click {app_name} and choose 'Run as administrator'."
            )
        return (
            f"Wiping '{device}' requires root privileges.\n"
            f"Re-run {app_name} with sudo."
        )
    return None
