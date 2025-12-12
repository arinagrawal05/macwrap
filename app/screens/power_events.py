from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.personality import PersonalityScreen

class PowerEventsScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                pe = stats.get('power_events', {"sleeps":0,"wakes":0,"reboots":0})
                content = (
                    f"[bold yellow]⚡ Power Events[/bold yellow]\n\n"
                    f"Sleeps: [bold]{pe.get('sleeps',0)}[/bold]\n"
                    f"Wakes: [bold]{pe.get('wakes',0)}[/bold]\n"
                    f"Reboots: [bold]{pe.get('reboots',0)}[/bold]\n\n"
                    "[italic]Your Mac's sleep cycle[/italic]\n\n"
                    "[dim]Press SPACE or ENTER to continue[/dim]"
                )
                yield Static(content, id="power")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#power")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(PersonalityScreen())
