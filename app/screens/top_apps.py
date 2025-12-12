from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.streak import StreakScreen

class TopAppsScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                content = "[bold magenta]Your Top 5 Apps of 2025[/bold magenta]\n\n"
                if stats.get('total_hours', 0) > 0:
                    for i, (app, hrs, launches, _) in enumerate(stats.get("top_apps", [])[:5], 1):
                        content += f"#{i} [bold]{app}[/bold] - {hrs} hrs ({launches:,} opens)\n"
                else:
                    content += "[yellow]No app usage data[/yellow]\n"
                content += "\n[dim]Press SPACE or ENTER to continue[/dim]"
                yield Static(content, id="apps")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#apps")
        w.styles.opacity = 0
        w.styles.offset_y = 5
        w.styles.animate("opacity", value=1.0, duration=1.5)
        w.styles.animate("offset_y", value=0, duration=1.2, easing="out_bounce")

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(StreakScreen())
