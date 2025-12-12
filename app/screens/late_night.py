from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.longest_session import LongestSessionScreen

class LateNightScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                if stats.get('late_night_hours', 0) > 0:
                    pct = int((stats['late_night_hours'] / stats['total_hours']) * 100) if stats.get('total_hours',0) else 0
                    content = (
                        f"[bold magenta]🌙 Late Night Sessions 🌙[/bold magenta]\n\n"
                        f"[bold white]{stats['late_night_hours']} hours[/bold white]\n"
                        "between 10pm - 4am\n\n"
                        f"[yellow]That's {pct}% of your total time![/yellow]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = (
                        "[green]No late night sessions![/green]\n\n"
                        "[italic]Healthy sleep schedule detected[/italic]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                yield Static(content, id="latenight")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#latenight")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(LongestSessionScreen())
