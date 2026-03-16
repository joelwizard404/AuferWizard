# AufurWizard

A terminal-based secure file shredder for Linux and macOS. Built with Python and Textual.

Supports multiple wipe standards — from a quick zero-fill to the full 35-pass Gutmann algorithm. Operates on individual files, folders, and raw block devices/partitions.

-----

## Features

- **Multiple wipe standards** — Zero Fill, Random, DoD 3-Pass, DoD 7-Pass, Gutmann 35-Pass
- **File & folder shredding** — recursively wipes directory trees
- **Block device wiping** — targets raw disks and partitions (requires root)
- **Operation history** — logs every shred to `~/.aufur_wizard/history.log`
- **Terminal UI** — keyboard-navigable interface via Textual

-----

## Requirements

- Python 3.11+
- Linux or macOS
- Root/sudo access for block device operations

-----

## Installation

```bash
git clone https://github.com/joelwizard404/AuferWizard.git
cd AuferWizard
pip install -e .
```

-----

## Usage

```bash
aufur
```

Or without installing:

```bash
python -m aufur_wizard.main
```

Navigate the menu with arrow keys and Enter. Press `Escape` to go back, `Q` to quit.

-----

## Wipe Standards

|ID       |Name             |Passes|Notes                                   |
|---------|-----------------|------|----------------------------------------|
|`zero`   |Zero Fill        |1     |Fast, not forensically secure           |
|`random` |Random           |1     |Single pass of cryptographic random data|
|`dod3`   |DoD 5220.22-M    |3     |US DoD standard — zeros, ones, random   |
|`dod7`   |DoD 5220.22-M ECE|7     |Extended DoD — recommended default      |
|`gutmann`|Gutmann          |35    |Maximum security for older HDDs         |

-----

## Logs

All operations are appended to `~/.aufur_wizard/history.log` in JSON format. Viewable from within the app under **View history**.

-----

## License

Public domain — see <LICENSE>.