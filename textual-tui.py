# water_log_tui.py

import sys
import sqlite3

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer, Button, Static

from textual_plotext import PlotextPlot  # <--- NEW


class WaterLogApp(App):
    """TUI to show latest water entries, daily totals, and rolling 24h stats."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reload", "Reload"),
    ]

    def __init__(self, db_path: str, **kwargs):
        super().__init__(**kwargs)
        self.db_path = db_path

        # 0 = rolling table, 1 = log table, 2 = full table, 3 = rolling chart
        self.current_view = 0

        self.log_table = DataTable(zebra_stripes=True, id="log-table")
        self.full_table = DataTable(zebra_stripes=True, id="full-table")
        self.rolling_table = DataTable(zebra_stripes=True, id="rolling-table")

        # Make the log table about 20 terminal rows tall and scrollable
        self.log_table.cursor_type = "row"
        self.log_table.styles.height = 20

        # Plotext-based chart for the rolling 24h view
        self.rolling_plot = PlotextPlot(id="rolling-plot")
        self.rolling_plot.styles.height = 30  # tweak as desired

    def compose(self) -> ComposeResult:
        # Clock off
        yield Header(show_clock=False)

        # One title, updated when rotating views
        yield Static("Rolling 24h", classes="section-title", id="section-title")

        # All tables + plot are in the layout; we toggle visibility via .display
        yield self.rolling_table
        yield self.log_table
        yield self.full_table
        yield self.rolling_plot

        # View-rotation button
        yield Button("View: Latest Drinks", id="rotate-view-btn")

        # Drink button (always present)
        yield Button("Drink Water", id="drink-water-btn")

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_all()
        # Start on rolling table view
        self._show_view(0)

    def action_reload(self) -> None:
        self.refresh_all()
        self._show_view(self.current_view)

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
                LIMIT 200
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
                LIMIT 20
                """
            )
            return cur.fetchall()
        finally:
            conn.close()

    # --- Table & plot refreshers ---------------------------------------

    def refresh_all(self) -> None:
        self.refresh_log_table()
        self.refresh_full_table()
        self.refresh_rolling_table()
        self.refresh_rolling_plot()

    def refresh_log_table(self) -> None:
        """Populate the per-entry table."""
        self.log_table.clear(columns=True)
        self.log_table.add_columns("id", "timestamp", "ounces")

        rows = self.fetch_log_rows()
        for row in rows:
            self.log_table.add_row(str(row[0]), row[1], str(row[2]))

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
            "% of target",
        )

        rows = self.fetch_rolling_rows()
        for row in rows:
            # row = (timestamp, ounces, rolling_24h_ounces, weight, target, percent_of_target)
            self.rolling_table.add_row(
                str(row[0]),
                str(row[1]),
                str(row[2]),
                str(row[5]),
            )

    # def refresh_rolling_plot(self) -> None:
    #     """Build a Plotext line chart of rolling_24h_ounces."""
    #     rows = self.fetch_rolling_rows()
    #     plt = self.rolling_plot.plt

    #     # Clear any previous plot
    #     plt.clear_plot()

    #     if not rows:
    #         plt.title("Rolling 24h (no data)")
    #         return

    #     # Oldest on the left, newest on the right
    #     rows = list(reversed(rows))
    #     y = [float(r[2]) for r in rows]  # rolling_24h_ounces
    #     x = list(range(len(y)))

    #     # Simple line plot
    #     plt.plot(x, y)
    #     plt.title("Rolling 24h (oz)")
    #     plt.xlabel("Entry (oldest → newest)")
    #     plt.ylabel("24h total (oz)")
    #     plt.grid(True, True)


    def refresh_rolling_plot(self) -> None:
        """Build a Plotext line chart of rolling_24h_ounces."""
        rows = self.fetch_rolling_rows()
        plt = self.rolling_plot.plt

        # Try to clear any previous plot safely
        for name in ("clear_figure", "clear_plot", "clear_data"):
            clear = getattr(plt, name, None)
            if callable(clear):
                clear()
                break

        if not rows:
            plt.title("Rolling 24h (no data)")
            return

        # Oldest on the left, newest on the right
        # rows = list(reversed(rows))
        y = [float(r[2]) for r in rows]  # rolling_24h_ounces
        x = list(range(len(y)))

        # plt.plot(x, y)
        # plt.bar(x, y)  # Using bar plot for better visibility
        plt.bar(x, y, orientation="horizontal")
        plt.title("Rolling 24h (oz)")
        plt.xlabel("Entry (oldest → newest)")
        plt.ylabel("24h total (oz)")
        # plt.grid(True, True)




    # --- View switching -------------------------------------------------

    def _show_view(self, index: int) -> None:
        """Show one of the four views based on index 0–3."""
        self.current_view = index % 4

        title_widget = self.query_one("#section-title", Static)
        rotate_button = self.query_one("#rotate-view-btn", Button)

        if self.current_view == 0:
            # Rolling 24h table
            self.rolling_table.display = True
            self.log_table.display = False
            self.full_table.display = False
            self.rolling_plot.display = False

            title_widget.update("Rolling 24h")
            rotate_button.label = "View: Latest Drinks"

        elif self.current_view == 1:
            # Latest Drinks (water_log)
            self.rolling_table.display = False
            self.log_table.display = True
            self.full_table.display = False
            self.rolling_plot.display = False

            title_widget.update("Latest Drinks (water_log)")
            rotate_button.label = "View: Daily Totals"

            # Focus so you can scroll immediately
            self.log_table.focus()

        elif self.current_view == 2:
            # Daily Totals (water_log_full)
            self.rolling_table.display = False
            self.log_table.display = False
            self.full_table.display = True
            self.rolling_plot.display = False

            title_widget.update("Daily Totals (water_log_full)")
            rotate_button.label = "View: Rolling Chart"

        else:
            # Rolling 24h chart view (Plotext)
            self.rolling_table.display = False
            self.log_table.display = False
            self.full_table.display = False
            self.rolling_plot.display = True

            title_widget.update("Rolling 24h Chart")
            rotate_button.label = "View: Rolling 24h"

    # --- Events ---------------------------------------------------------

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "drink-water-btn":
            self.insert_drink(8.0)
            self.refresh_all()
            self._show_view(self.current_view)
        elif event.button.id == "rotate-view-btn":
            # Cycle: rolling table -> log table -> full table -> chart -> rolling table
            self._show_view(self.current_view + 1)


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "sqlite-water-tracker.db"
    app = WaterLogApp(db_path)
    app.run()
