from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Log

class BigButtonApp(App):
    # CSS = """
    # Screen {
    #     align: center middle;
    # }

    # #button-panel {
    #     width: 80%;
    #     max-width: 60;
    #     align: center middle;
    # }

    # Button {
    #     width: 100%;
    #     height: 3;              /* Bigger click/tap area */
    #     margin: 1 0;
    #     padding: 1 2;
    #     content-align: center middle;
    #     border: heavy green;
    #     color: green;
    #     background: #101010;        
    # }

    # #output {
    #     width: 90%;
    #     height: 40%;
    #     border: round;
    #     margin-top: 1;
    # }
    # """


    # CSS = """
    # Screen {
    #     align: center middle;
    # }

    # #button-panel {
    #     width: 80%;
    #     max-width: 60;
    #     align: center middle;
    # }

    # /* Only layout/size here, no colors */
    # Button {
    #     width: 100%;
    #     height: 3;
    #     margin: 1 0;
    #     padding: 1 2;
    #     content-align: center middle;
    # }

    # #output {
    #     width: 90%;
    #     height: 40%;
    #     border: round;
    #     margin-top: 1;
    # }
    # """

    CSS = """

    Button {
        width: 20;
        height: 5;
    }

    """


    def compose(self) -> ComposeResult:
        # Big vertical stack of buttons
        with Vertical(id="button-panel"):
            yield Button("Show date & time", id="btn-datetime")
            yield Button("List home directory", id="btn-home")
            yield Button("Echo 'abc'", id="btn-echo")

        # Output area
        yield Log(id="output")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        log = self.query_one(Log)

        if event.button.id == "btn-datetime":
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"Current date/time: {now}\n")

        elif event.button.id == "btn-home":
            home = Path.home()
            entries = sorted(p.name for p in home.iterdir())
            log.write(f"Files in {home}:")
            for name in entries:
                log.write(f"  {name}\n")
            log.write("\n")

        elif event.button.id == "btn-echo":
            log.write("abc\n")

if __name__ == "__main__":
    BigButtonApp().run()
