from __future__ import annotations

import os
import sys
from pathlib import Path


def is_root() -> bool:
    if sys.platform == "win32":
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    return os.geteuid() == 0


def can_write(path: Path) -> bool:
    return os.access(path, os.W_OK)


def require_root_for_device(device: Path) -> str | None:
    if not is_root():
        return (
            f"Wiping '{device}' requires root privileges.\n"
            "Re-run AufurWizard with sudo."
        )
    return None
