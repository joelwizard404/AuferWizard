from __future__ import annotations

import os
import secrets
import stat
import struct
import sys
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable

from .standards import Standard, Pass


class EventType(Enum):
    PASS_START    = auto()
    PASS_PROGRESS = auto()
    PASS_DONE     = auto()
    FILE_DONE     = auto()
    VERIFY_START  = auto()
    VERIFY_DONE   = auto()
    ERROR         = auto()


@dataclass
class ShredEvent:
    type: EventType
    path: Path | None = None
    pass_index: int = 0
    pass_total: int = 0
    pass_label: str = ""
    bytes_written: int = 0
    bytes_total: int = 0
    message: str = ""


Callback = Callable[[ShredEvent], None]

CHUNK = 1024 * 1024

def shred_file(path: Path, standard: Standard,
               callback: Callback | None = None) -> bool:
    cb = callback or _noop
    try:
        size = path.stat().st_size
    except OSError as exc:
        cb(ShredEvent(EventType.ERROR, path=path, message=str(exc)))
        return False

    try:
        with open(path, "r+b") as fh:
            for i, p in enumerate(standard.passes):
                cb(ShredEvent(EventType.PASS_START, path=path,
                              pass_index=i, pass_total=len(standard.passes),
                              pass_label=p.label, bytes_total=size))
                _overwrite_fd(fh, size, p, i, len(standard.passes), path, cb)
                cb(ShredEvent(EventType.PASS_DONE, path=path,
                              pass_index=i, pass_total=len(standard.passes),
                              pass_label=p.label))
            if standard.verify:
                cb(ShredEvent(EventType.VERIFY_START, path=path))
                _verify_zeros(fh, size)
                cb(ShredEvent(EventType.VERIFY_DONE, path=path))
        path.unlink()
        cb(ShredEvent(EventType.FILE_DONE, path=path))
        return True
    except OSError as exc:
        cb(ShredEvent(EventType.ERROR, path=path, message=str(exc)))
        return False


def shred_directory(root: Path, standard: Standard,
                    callback: Callback | None = None) -> tuple[int, int]:
    ok = err = 0
    all_files = sorted(p for p in root.rglob("*") if p.is_file())
    for fpath in all_files:
        if shred_file(fpath, standard, callback):
            ok += 1
        else:
            err += 1
    for dirpath in sorted(root.rglob("*"), reverse=True):
        if dirpath.is_dir():
            try:
                dirpath.rmdir()
            except OSError:
                pass
    try:
        root.rmdir()
    except OSError:
        pass
    return ok, err


def shred_block_device(device: Path, standard: Standard,
                       callback: Callback | None = None) -> bool:
    cb = callback or _noop

    if not device.exists():
        cb(ShredEvent(EventType.ERROR, path=device,
                      message=f"Device not found: {device}"))
        return False
        
    if sys.platform != "win32":
        try:
            if not stat.S_ISBLK(device.stat().st_mode):
                cb(ShredEvent(EventType.ERROR, path=device,
                              message=f"{device} is not a block device"))
                return False
        except OSError as exc:
            cb(ShredEvent(EventType.ERROR, path=device, message=str(exc)))
            return False

    size = _block_device_size(device)
    if size == 0:
        cb(ShredEvent(EventType.ERROR, path=device,
                      message="Could not determine device size"))
        return False

    try:
        with open(device, "r+b", buffering=0) as fh:
            for i, p in enumerate(standard.passes):
                cb(ShredEvent(EventType.PASS_START, path=device,
                              pass_index=i, pass_total=len(standard.passes),
                              pass_label=p.label, bytes_total=size))
                _overwrite_fd(fh, size, p, i, len(standard.passes), device, cb)
                cb(ShredEvent(EventType.PASS_DONE, path=device,
                              pass_index=i, pass_total=len(standard.passes),
                              pass_label=p.label))
        return True
    except PermissionError:
        cb(ShredEvent(EventType.ERROR, path=device,
                      message="Permission denied – run as root / Administrator."))
        return False
    except OSError as exc:
        cb(ShredEvent(EventType.ERROR, path=device, message=str(exc)))
        return False

def _overwrite_fd(fh, size: int, p: Pass, pass_idx: int,
                  pass_total: int, path: Path, cb: Callback) -> None:
    fh.seek(0)
    written = 0
    while written < size:
        chunk_size = min(CHUNK, size - written)
        if p.pattern is None:
            data = secrets.token_bytes(chunk_size)
        else:
            repeats = -(-chunk_size // len(p.pattern))
            data = (p.pattern * repeats)[:chunk_size]
        fh.write(data)
        written += chunk_size
        cb(ShredEvent(EventType.PASS_PROGRESS, path=path,
                      pass_index=pass_idx, pass_total=pass_total,
                      pass_label=p.label, bytes_written=written,
                      bytes_total=size))
    fh.flush()
    try:
        os.fsync(fh.fileno())
    except OSError:
        pass


def _verify_zeros(fh, size: int) -> None:
    fh.seek(0)
    read = 0
    while read < size:
        chunk = fh.read(min(CHUNK, size - read))
        if not chunk:
            break
        if any(chunk):
            raise OSError("Verify failed: non-zero byte detected after shred")
        read += len(chunk)


def _block_device_size(device: Path) -> int:
    """Determine the byte-size of a block device, cross-platform."""
    if sys.platform == "win32":
        return _block_device_size_windows(device)
    if sys.platform == "darwin":
        return _block_device_size_macos(device)
    return _block_device_size_linux(device)


def _block_device_size_linux(device: Path) -> int:
    name = device.name.rstrip("0123456789")
    for path in (
        Path(f"/sys/block/{name}/{device.name}/size"),
        Path(f"/sys/block/{name}/size"),
    ):
        try:
            return int(path.read_text().strip()) * 512
        except (OSError, ValueError):
            pass
    return _block_device_size_seek(device)


def _block_device_size_macos(device: Path) -> int:
    """Use ioctl DKIOCGETBLOCKCOUNT + DKIOCGETBLOCKSIZE on macOS."""
    try:
        import fcntl
        DKIOCGETBLOCKCOUNT = 0x40086419
        DKIOCGETBLOCKSIZE  = 0x40046418
        with open(device, "rb") as fh:
            buf = b"\x00" * 8
            count = struct.unpack("Q", fcntl.ioctl(fh, DKIOCGETBLOCKCOUNT, buf))[0]
            bsize = struct.unpack("I", fcntl.ioctl(fh, DKIOCGETBLOCKSIZE, b"\x00" * 4))[0]
            return count * bsize
    except Exception:
        return _block_device_size_seek(device)


def _block_device_size_windows(device: Path) -> int:
    """
    Use DeviceIoControl(IOCTL_DISK_GET_DRIVE_GEOMETRY_EX) on Windows.
    Falls back to a simple seek-to-end.
    """
    try:
        import ctypes
        import ctypes.wintypes as wt

        GENERIC_READ               = 0x80000000
        FILE_SHARE_READ            = 0x00000001
        FILE_SHARE_WRITE           = 0x00000002
        OPEN_EXISTING              = 3
        IOCTL_DISK_GET_DRIVE_GEOMETRY_EX = 0x000700A0

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.CreateFileW(
            str(device),
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            0,
            None,
        )
        if handle == wt.HANDLE(-1).value:
            return _block_device_size_seek(device)

        # DISK_GEOMETRY_EX is 24 bytes (DISK_GEOMETRY 24 + DiskSize 8 + Data 1)
        buf = ctypes.create_string_buffer(32)
        returned = wt.DWORD(0)
        ok = kernel32.DeviceIoControl(
            handle, IOCTL_DISK_GET_DRIVE_GEOMETRY_EX,
            None, 0, buf, ctypes.sizeof(buf), ctypes.byref(returned), None,
        )
        kernel32.CloseHandle(handle)
        if ok:
            # DiskSize is at offset 24 (after DISK_GEOMETRY)
            disk_size = struct.unpack_from("<q", buf, 24)[0]
            return disk_size
    except Exception:
        pass
    return _block_device_size_seek(device)


def _block_device_size_seek(device: Path) -> int:
    """Universal fallback: seek to end."""
    try:
        with open(device, "rb") as fh:
            fh.seek(0, 2)
            return fh.tell()
    except OSError:
        return 0


def _noop(_: ShredEvent) -> None:
    pass
