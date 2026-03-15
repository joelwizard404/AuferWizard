from __future__ import annotations

import sys
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Footer, Header, Label, Static


class PathBrowser(ModalScreen[Path | None]):
    """Modal TUI file-browser.  Returns the selected Path or None on cancel."""

    CSS = """
    PathBrowser {
        align: center middle;
    }

    #browser-card {
        width: 80%;
        height: 80%;
        border: round $primary;
        padding: 0 1;
    }

    #browser-title {
        text-style: bold;
        color: $primary;
        padding: 0 1;
        margin-bottom: 1;
    }

    #tree {
        height: 1fr;
        border: solid $surface-lighten-2;
    }

    #selected-label {
        color: $text-muted;
        padding: 0 1;
        height: 1;
    }

    #btn-row {
        height: auto;
        padding: 1 0 0 0;
        align: right middle;
    }

    Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Select"),
    ]

    def __init__(self, start: Path | None = None) -> None:
        super().__init__()
        self._start = start or _default_root()
        self._selected: Path | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="browser-card"):
            yield Label("Browse – select a file or folder", id="browser-title")
            yield DirectoryTree(str(self._start), id="tree")
            yield Static(_fmt(self._selected), id="selected-label")
            with Horizontal(id="btn-row"):
                yield Button("Select", variant="primary", id="btn-select")
                yield Button("Cancel", id="btn-cancel")
        yield Footer()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        self._selected = Path(event.path)
        self._refresh_label()

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self._selected = Path(event.path)
        self._refresh_label()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-select":
            self.action_confirm()
        else:
            self.action_cancel()

    def action_confirm(self) -> None:
        self.dismiss(self._selected)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _refresh_label(self) -> None:
        self.query_one("#selected-label", Static).update(_fmt(self._selected))

def _fmt(path: Path | None) -> str:
    if path is None:
        return "No selection"
    return f"Selected: [bold]{path}[/bold]"


def _default_root() -> Path:
    """Return a sensible starting directory for the current OS."""
    if sys.platform == "win32":
        return Path.home()
    return Path.home()
