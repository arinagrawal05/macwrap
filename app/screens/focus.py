from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.weekend_weekday import WeekendVsWeekdayScreen

class FocusHoursScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                if stats.get('focus_hours', 0) > 0:
                    content = (
                        f"[bold cyan]Deep Focus Time[/bold cyan]\n\n"
                        f"[bold white]{stats['focus_hours']} hours[/bold white]\n"
                        f"across {stats['focus_sessions']} sessions\n\n"
                        "[italic]Sessions of 2+ hours each[/italic]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = "[yellow]No deep focus sessions detected[/yellow]\n\n[dim]Press SPACE or ENTER[/dim]"
                yield Static(content, id="focus")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#focus")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(WeekendVsWeekdayScreen())
