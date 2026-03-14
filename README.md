# AufurWizard

A terminal-based secure file shredder with multiple wiping standards.

---

## Features

- **Multiple wipe standards** – Zero Fill, Random, DoD 3-Pass, DoD 7-Pass, Gutmann 35-Pass
- **Files & folders** – shred individual files or entire directory trees
- **Disk wiping** – overwrite full block devices (requires root)
- **Operation history** – every wipe is logged locally
- **TUI interface** – keyboard-driven terminal UI via [Textual](https://textual.textualize.io/)

---

## Requirements

- Python 3.11+
- Linux or macOS
- Root/sudo for block device wiping

---

## Installation
```bash
pip install aufur-wizard
```

Or from source:
```bash
git clone https://github.com/joelwizard404/AufurWizard.git
cd AufurWizard
pip install .
```

---

## Usage
```bash
aufur
```

Use arrow keys to navigate, Enter to select, Escape to go back.

---

## Wipe Standards

| ID        | Name                   | Passes | Notes                        |
|-----------|------------------------|--------|------------------------------|
| `zero`    | Zero Fill              | 1      | Fast, not forensically secure |
| `random`  | Random                 | 1      | Single pass of random data   |
| `dod3`    | DoD 5220.22-M          | 3      | US DoD standard              |
| `dod7`    | DoD 5220.22-M ECE      | 7      | Extended DoD standard        |
| `gutmann` | Gutmann                | 35     | Maximum security for HDDs    |

---

## Log location
```
~/.aufur_wizard/history.log
```

---
## License

Public domain – see [LICENSE](LICENSE).
