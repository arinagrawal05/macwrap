from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.forgotten_app import ForgottenAppScreen

class HourlyHeatmapScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                content = "[bold cyan]Your Hourly Heatmap[/bold cyan]\n\n"
                hourly = stats.get('hourly_breakdown', {})
                if sum(hourly.values()) > 0:
                    max_hours = max(hourly.values()) if hourly else 0
                    for hour in range(24):
                        hours = hourly.get(hour, 0)
                        bar_len = int((hours / max_hours * 20)) if max_hours > 0 else 0
                        bar = "█" * bar_len
                        am_pm = "AM" if hour < 12 else "PM"
                        display_hour = 12 if hour == 0 or hour == 12 else hour % 12
                        content += f"{display_hour:2d}{am_pm} {bar} {int(hours)}h\n"
                else:
                    content += "[yellow]No hourly data available[/yellow]\n"
                content += "\n[dim]Press SPACE or ENTER to continue[/dim]"
                yield Static(content, id="heatmap")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#heatmap")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.5)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(ForgottenAppScreen())
