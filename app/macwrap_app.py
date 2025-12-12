from textual.app import App
from app.screens.intro import IntroScreen
from app.utils.stats import get_all_stats

class MacWrap(App):
    CSS = """
    Screen {
        background: #0d1117;
        color: #c9d1d9;
    }
    Static {
        text-align: center;
        width: auto;
        padding: 2 4;
    }
    Header, Footer {
        background: #161b22;
        color: #58a6ff;
    }
    """

    def on_mount(self):
        # Compute stats once at startup and attach to app for screens to use.
        try:
            self.stats = get_all_stats()
        except Exception as e:
            error_msg = str(e)
            if "Operation not permitted" in error_msg or "Permission denied" in error_msg:
                error_msg = (
                    "Access to Screen Time database denied.\n\n"
                    "1. Go to System Settings > Privacy & Security > Full Disk Access\n"
                    "2. Enable it for your Terminal (iTerm/Terminal)\n"
                    "3. Restart Terminal and try again"
                )
            
            self.stats = {
                "year": 2025,
                "total_hours": 0,
                "top_apps": [("No data", 0, 0, 0)],
                "total_launches": 0,
                "longest_session": ("", 0),
                "max_streak": 0,
                "weekend_hours": 0,
                "weekday_hours": 0,
                "hourly_breakdown": {h: 0 for h in range(24)},
                "peak_hour": 12,
                "late_night_hours": 0,
                "focus_sessions": 0,
                "focus_hours": 0,
                "forgotten_app": "None",
                "wtf_spike_day": (None, 0),
                "personality": "Mac User",
                "command_count": 0,
                "file_stats": {"total": 0, "top_types": []},
                "power_events": {"sleeps": 0, "wakes": 0, "reboots": 0},
                "error": error_msg
            }
        self.dark = True
        self.push_screen(IntroScreen())
