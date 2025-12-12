from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.late_night import LateNightScreen

class WTFSpikeScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                if stats.get('wtf_spike_day', (None,0))[0]:
                    date_str, hours = stats['wtf_spike_day']
                    content = (
                        f"[bold red]The 'WTF' Spike Day[/bold red]\n\n"
                        f"[bold white]{date_str}[/bold white]\n"
                        f"{int(hours)} hours in a single day!\n\n"
                        "[italic]3x your weekly average[/italic]\n\n"
                        "[dim]What happened that day?[/dim]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = (
                        "[yellow]No extreme spike days detected[/yellow]\n\n"
                        "[green]Your usage was consistent![/green]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                yield Static(content, id="spike")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#spike")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(LateNightScreen())
