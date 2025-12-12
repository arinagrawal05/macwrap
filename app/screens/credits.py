from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on

class CreditsScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                yield Static(
                    "[bold magenta]Developed By Arin Agrawal[/bold magenta]\n"
                    "[cyan]x.com/ArinBuilds[/cyan]\n\n"
                    "[dim]Press SPACE to exit[/dim]",
                    id="credits"
                )
        yield Footer()

    def on_mount(self):
        w = self.query_one("#credits")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.5)

    @on(events.Key)
    def on_key(self, event):
        if event.key == "space":
            self.app.exit()
