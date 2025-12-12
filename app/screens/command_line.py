from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.power_events import PowerEventsScreen
 
class CommandLineScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                if stats.get('command_count', 0) > 0:
                    content = (
                        f"[bold green]⌨️  Command Line Stats[/bold green]\n\n"
                        f"[bold white]{stats['command_count']:,}[/bold white]\n"
                        "shell commands executed\n\n"
                        "[italic]Terminal warrior detected[/italic]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = (
                        "[yellow]No command history found[/yellow]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                yield Static(content, id="commands")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#commands")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(PowerEventsScreen())
