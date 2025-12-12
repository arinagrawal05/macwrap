from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.finale import FinaleScreen

class PersonalityScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                yield Static(
                    f"[bold italic cyan]Your 2025 Mac Personality:[/bold italic cyan]\n\n"
                    f"[bold yellow]{stats['personality']}[/bold yellow]\n\n"
                    "[dim]Press SPACE or ENTER for finale[/dim]",
                    id="personality"
                )
        yield Footer()

    def on_mount(self):
        w = self.query_one("#personality")
        w.styles.opacity = 0
        w.styles.rotate = -8
        w.styles.animate("opacity", value=1.0, duration=2.0)
        w.styles.animate("rotate", value=0, duration=2.0, easing="out_back")

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(FinaleScreen())
