from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from app.screens.loading import LoadingScreen

class IntroScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                yield Static("[bold magenta]macwrap[/bold magenta]\n[cyan]Your Mac. Your 2025.[/cyan]", id="title")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#title")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=2.0)
        self.set_timer(3.5, lambda: self.app.push_screen(LoadingScreen()))
