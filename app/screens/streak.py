from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.focus import FocusHoursScreen

class StreakScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                if stats.get('max_streak', 0) > 0:
                    content = (
                        f"[bold yellow]🔥 Your Longest Streak 🔥[/bold yellow]\n\n"
                        f"[bold white]{stats['max_streak']} days[/bold white]\n"
                        "of consecutive Mac usage\n\n"
                        "[green]Dedication level: Expert[/green]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = "[yellow]No streak data available[/yellow]\n\n[dim]Press SPACE or ENTER[/dim]"
                yield Static(content, id="streak")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#streak")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(FocusHoursScreen())
