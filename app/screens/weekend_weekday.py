from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.heatmap import HourlyHeatmapScreen

class WeekendVsWeekdayScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                total = stats.get('weekend_hours', 0) + stats.get('weekday_hours', 0)
                if total > 0:
                    weekend_pct = int((stats['weekend_hours'] / total) * 100) if total else 0
                    weekday_pct = 100 - weekend_pct
                    winner = "Weekends" if weekend_pct > 50 else "Weekdays"
                    content = (
                        f"[bold magenta]Weekend vs Weekday[/bold magenta]\n\n"
                        f"[yellow]Weekends:[/yellow] {stats['weekend_hours']} hrs ({weekend_pct}%)\n"
                        f"[cyan]Weekdays:[/cyan] {stats['weekday_hours']} hrs ({weekday_pct}%)\n\n"
                        f"[bold green]Winner: {winner}[/bold green]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = "[yellow]No usage data[/yellow]\n\n[dim]Press SPACE or ENTER[/dim]"
                yield Static(content, id="weekend")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#weekend")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(HourlyHeatmapScreen())
