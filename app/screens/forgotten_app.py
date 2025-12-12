from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.spike import WTFSpikeScreen

class ForgottenAppScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                content = (
                    f"[bold yellow]The App You Forgot You Had[/bold yellow]\n\n"
                    f"[bold white]{stats.get('forgotten_app','None')}[/bold white]\n\n"
                    "[italic]Less than 1 hour total usage[/italic]\n\n"
                    "[dim]Maybe it's time to uninstall?[/dim]\n\n"
                    "[dim]Press SPACE or ENTER to continue[/dim]"
                )
                yield Static(content, id="forgotten")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#forgotten")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(WTFSpikeScreen())
