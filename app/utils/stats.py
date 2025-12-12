from app.utils.screen_time import fetch_screen_time_stats
from app.utils.history import get_command_history
from app.utils.filesystem import get_file_creation_stats
from app.utils.power import get_power_events
from app.utils.personality import generate_personality

def get_all_stats(year=2025):
    st = fetch_screen_time_stats(year)
    if "error" in st:
        res = {
            **st,
            "command_count": 0,
            "file_stats": {"total": 0, "top_types": []},
            "power_events": {"sleeps": 0, "wakes": 0, "reboots": 0},
            "personality": "Mac User"
        }
        return res

    command_count = get_command_history()
    file_stats = get_file_creation_stats(year)
    power_events = get_power_events(year)
    personality = generate_personality(
        st.get("top_apps", []),
        st.get("total_hours", 0),
        st.get("peak_hour", 12),
        st.get("late_night_hours", 0),
        st.get("focus_hours", 0)
    )
    merged = {
        **st,
        "command_count": command_count,
        "file_stats": file_stats,
        "power_events": power_events,
        "personality": personality
    }
    return merged
