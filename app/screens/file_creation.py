from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle
from textual import events, on
from app.screens.power_events import PowerEventsScreen

class FileCreationScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                if stats.get('file_stats', {}).get('total', 0) > 0:
                    fs = stats['file_stats']
                    content = (
                        f"[bold magenta]📁 File Creation Stats[/bold magenta]\n\n"
                        f"[bold white]{fs['total']:,}[/bold white]\n"
                        "new files created in the year\n\n"
                    )
                    if fs.get('top_types'):
                        content += "Top file types:\n"
                        for ext, count in fs['top_types'][:3]:
                            content += f"  {ext}: {count:,}\n"
                    content += "\n[dim]Press SPACE or ENTER to continue[/dim]"
                else:
                    content = "[yellow]No file creation data[/yellow]\n\n[dim]Press SPACE or ENTER to continue[/dim]"
                yield Static(content, id="files")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#files")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(PowerEventsScreen())
