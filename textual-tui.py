# water_log_tui.py

import sys
import sqlite3

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer


class WaterLogApp(App):
    """Simple TUI to show the latest water_log entries."""

    CSS = """
    Screen {
        align: center middle;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reload", "Reload"),
    ]

    def __init__(self, db_path: str, **kwargs):
        super().__init__(**kwargs)
        self.db_path = db_path
        self.table = DataTable(zebra_stripes=True)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.table
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_table()

    def action_reload(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        """Fetch rows from SQLite and populate the table."""
        self.table.clear(columns=True)
        self.table.add_columns("id", "timestamp", "ounces")

        rows = self.fetch_rows()
        for row in rows:
            # row = (id, timestamp, ounces)
            self.table.add_row(str(row[0]), row[1], str(row[2]))

        if rows:
            self.table.focus()

    def fetch_rows(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, timestamp, ounces
                FROM water_log
                ORDER BY timestamp DESC
                LIMIT 10
                """
            )
            return cur.fetchall()
        finally:
            conn.close()


if __name__ == "__main__":
    # Allow passing the DB path as an argument; default to your filename.
    db_path = sys.argv[1] if len(sys.argv) > 1 else "sqlite-water-tracker.db"
    app = WaterLogApp(db_path)
    app.run()
