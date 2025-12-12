from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle

class FinaleScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                stats = self.app.stats
                if stats.get('total_hours', 0) > 0 and stats.get('top_apps'):
                    share_text = (
                        f"> {stats['total_hours']:,} hrs - "
                        f"{stats.get('total_launches',0):,} launches - "
                        f"{stats.get('max_streak',0)} day streak\n"
                        f"> Top: {stats['top_apps'][0][0]} - "
                        f"{stats.get('personality')}\n"
                    )
                else:
                    share_text = "> Enable Screen Time to see your stats!\n"
                share = (
                    "[bold magenta]Happy end of the year![/bold magenta]\n\n"
                    "Thanks for an epic year on your Mac\n\n"
                    "[white]Share your macwrap:[/white]\n\n"
                    f"{share_text}"
                    "> brew install arinagrawal05/labs/macwrap"
                )
                yield Static(share, id="finale")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#finale")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=2.5)
