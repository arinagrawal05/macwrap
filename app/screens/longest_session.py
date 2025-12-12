from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.command_line import CommandLineScreen

class LongestSessionScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                app_name, hours = stats.get('longest_session', ("", 0))
                if hours and hours > 0:
                    content = (
                        f"[bold cyan]Longest Single Session[/bold cyan]\n\n"
                        f"[bold white]{app_name}[/bold white]\n"
                        f"{round(hours, 1)} hours straight\n\n"
                        "[italic]Marathon mode activated[/italic]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = "[yellow]No session data[/yellow]\n\n[dim]Press SPACE or ENTER[/dim]"
                yield Static(content, id="longest")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#longest")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(CommandLineScreen())
