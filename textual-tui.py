# water_log_tui.py

import sys
import sqlite3

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer, Button, Static


class WaterLogApp(App):
    """TUI to show latest water entries, daily totals, and rolling 24h stats."""

    # CSS = """
    # Screen {
    #     layout: vertical;
    # }

    # .section-title {
    #     height: 1;
    #     content-align: left middle;
    #     padding: 0 1;
    # }

    # #log-table {
    #     height: 1fr;
    # }

    # #full-table {
    #     height: 1fr;
    # }

    # #rolling-table {
    #     height: 1fr;
    # }

    # #drink-water-btn {
    #     dock: bottom;
    #     height: 3;
    #     content-align: center middle;
    # }
    # """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reload", "Reload"),
    ]

    def __init__(self, db_path: str, **kwargs):
        super().__init__(**kwargs)
        self.db_path = db_path

        self.log_table = DataTable(zebra_stripes=True, id="log-table")
        self.full_table = DataTable(zebra_stripes=True, id="full-table")
        self.rolling_table = DataTable(zebra_stripes=True, id="rolling-table")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # yield Static("Latest Drinks (water_log)", classes="section-title")
        # yield self.log_table

        # yield Static("Daily Totals (water_log_full)", classes="section-title")
        # yield self.full_table

        yield Static("Rolling 24h", classes="section-title")
        yield self.rolling_table

        yield Button("Drink Water", id="drink-water-btn")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_all()

    def action_reload(self) -> None:
        self.refresh_all()

    # --- DB helpers -----------------------------------------------------

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def insert_drink(self, ounces: float = 8.0) -> None:
        """Insert a new drink entry into water_log."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO water_log (timestamp, ounces)
                VALUES (datetime('now', 'localtime'), ?)
                """,
                (ounces,),
            )
            conn.commit()
        finally:
            conn.close()

    def fetch_log_rows(self):
        """Latest individual entries from water_log."""
        conn = self._connect()
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

    def fetch_full_rows(self):
        """Latest daily summary rows from water_log_full."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT date, total, weight, target, percent_of_target
                FROM water_log_full
                ORDER BY date DESC
                LIMIT 10
                """
            )
            return cur.fetchall()
        finally:
            conn.close()

    def fetch_rolling_rows(self):
        """Latest rolling 24h rows from rolling_log_full."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT timestamp,
                       ounces,
                       rolling_24h_ounces,
                       weight,
                       target,
                       percent_of_target
                FROM rolling_log_full
                ORDER BY timestamp DESC
                LIMIT 10
                """
            )
            return cur.fetchall()
        finally:
            conn.close()

    # --- Table refreshers ----------------------------------------------

    def refresh_all(self) -> None:
        self.refresh_log_table()
        self.refresh_full_table()
        self.refresh_rolling_table()

    def refresh_log_table(self) -> None:
        """Populate the per-entry table."""
        self.log_table.clear(columns=True)
        self.log_table.add_columns("id", "timestamp", "ounces")

        rows = self.fetch_log_rows()
        for row in rows:
            self.log_table.add_row(str(row[0]), row[1], str(row[2]))

        if rows:
            self.log_table.focus()

    def refresh_full_table(self) -> None:
        """Populate the daily summary table."""
        self.full_table.clear(columns=True)
        self.full_table.add_columns(
            "date", "total", "weight", "target", "% of target"
        )

        rows = self.fetch_full_rows()
        for row in rows:
            # row = (date, total, weight, target, percent_of_target)
            self.full_table.add_row(
                str(row[0]),
                str(row[1]),
                str(row[2]),
                str(row[3]),
                str(row[4]),
            )

    def refresh_rolling_table(self) -> None:
        """Populate the rolling 24h table."""
        self.rolling_table.clear(columns=True)
        self.rolling_table.add_columns(
            "timestamp",
            "oz",
            "24h",
            # "weight",
            # "target",
            "% of target",
        )

        rows = self.fetch_rolling_rows()
        for row in rows:
            # row = (timestamp, ounces, rolling_24h_ounces, weight, target, percent_of_target)
            self.rolling_table.add_row(
                str(row[0]),
                str(row[1]),
                str(row[2]),
                # str(row[3]),
                # str(row[4]),
                str(row[5]),
            )

    # --- Events ---------------------------------------------------------

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "drink-water-btn":
            self.insert_drink(8.0)
            self.refresh_all()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "sqlite-water-tracker.db"
    app = WaterLogApp(db_path)
    app.run()
