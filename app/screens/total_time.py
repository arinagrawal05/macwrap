from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.top_apps import TopAppsScreen

class TotalTimeScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                if stats.get("error"):
                    content = (
                        "[bold red]Unable to read Screen Time data[/bold red]\n\n"
                        f"[yellow]Error: {stats['error']}[/yellow]\n\n"
                        "[dim]Try running with sudo or enable Screen Time[/dim]"
                    )
                elif stats.get('total_hours', 0) == 0:
                    content = (
                        "[bold white]No data found for 2025[/bold white]\n\n"
                        "Enable Screen Time in System Preferences\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = (
                        f"[bold white]{stats['total_hours']:,} hours[/bold white]\n"
                        f"actively using apps in {stats['year']}\n\n"
                        f"That's [bold cyan]{round(stats['total_hours']/24, 1)} full days[/bold cyan] of your life.\n\n"
                        f"[green]{stats.get('total_launches',0):,} total app launches[/green]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                yield Static(content, id="total")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#total")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=2.0)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(TopAppsScreen())
