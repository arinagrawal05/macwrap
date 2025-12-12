from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from app.screens.total_time import TotalTimeScreen

class LoadingScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                yield Static(
                    "[bold yellow]Unwrapping your Mac year...[/bold yellow]\n\n"
                    "[yellow]Analyzing your digital footprint...[/yellow]",
                    id="loading"
                )
        yield Footer()

    def on_mount(self):
        w = self.query_one("#loading")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)
        self.set_timer(3, lambda: self.app.push_screen(TotalTimeScreen()))
