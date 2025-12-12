import sqlite3
from pathlib import Path
import shutil
import tempfile
from datetime import datetime
from collections import defaultdict

def get_screen_time_db_path():
    home = Path.home()
    db_path = home / "Library" / "Application Support" / "Knowledge" / "knowledgeC.db"
    return db_path if db_path.exists() else None

def fetch_screen_time_stats(year=2025):
    db_path = get_screen_time_db_path()
    if not db_path:
        return {"error": "Screen Time DB not found", "year": year}

    temp_db = Path(tempfile.gettempdir()) / "knowledgeC_temp.db"
    shutil.copy2(db_path, temp_db)
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()

    start_date = f"{year}-01-01"
    end_date = f"{year+1}-01-01"

    # Basic app usage
    app_query = """
    SELECT
      ZOBJECT.ZVALUESTRING as app_name,
      SUM((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as hours,
      COUNT(*) as launch_count,
      MAX((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as longest_session
    FROM ZOBJECT
    WHERE ZOBJECT.ZSTREAMNAME LIKE '/app/usage%'
      AND ZOBJECT.ZVALUESTRING IS NOT NULL
      AND ZOBJECT.ZSTARTDATE IS NOT NULL
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') >= ?
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') < ?
    GROUP BY app_name
    ORDER BY hours DESC
    """
    cursor.execute(app_query, (start_date, end_date))
    app_data = cursor.fetchall()

    total_hours = 0.0
    total_launches = 0
    top_apps = []
    longest_session_app = ("", 0)

    for app_name, hours, launches, longest in app_data:
        if hours and hours > 0:
            clean_name = app_name.split('.')[-1].replace('-', ' ').title()
            total_hours += hours
            total_launches += launches
            top_apps.append((clean_name, int(hours), launches, longest))
            if longest and longest > longest_session_app[1]:
                longest_session_app = (clean_name, longest)

    # daily patterns
    daily_query = """
    SELECT date(datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch')) as usage_date,
           SUM((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as daily_hours
    FROM ZOBJECT
    WHERE ZOBJECT.ZSTREAMNAME LIKE '/app/usage%'
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') >= ?
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') < ?
    GROUP BY usage_date
    ORDER BY usage_date
    """
    cursor.execute(daily_query, (start_date, end_date))
    daily_data = cursor.fetchall()

    max_streak = 0
    current_streak = 0
    prev_date = None
    weekend_hours = 0
    weekday_hours = 0
    daily_hours_list = []
    wtf_spike_day = (None, 0)

    for date_str, hours in daily_data:
        current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        daily_hours_list.append(hours)
        if prev_date is None or (current_date - prev_date).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
        prev_date = current_date
        if current_date.weekday() >= 5:
            weekend_hours += hours
        else:
            weekday_hours += hours
        # detect spike using 7-day lookback
        if len(daily_hours_list) > 7:
            avg = sum(daily_hours_list[-7:]) / 7
            if hours > avg * 3 and hours > wtf_spike_day[1]:
                wtf_spike_day = (date_str, hours)

    # hourly breakdown
    hourly_query = """
    SELECT CAST(strftime('%H', datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch')) AS INTEGER) as hour,
           SUM((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as total_hours
    FROM ZOBJECT
    WHERE ZOBJECT.ZSTREAMNAME LIKE '/app/usage%'
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') >= ?
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') < ?
    GROUP BY hour
    """
    cursor.execute(hourly_query, (start_date, end_date))
    hourly_rows = cursor.fetchall()
    hourly_breakdown = {h: 0 for h in range(24)}
    for hour, hrs in hourly_rows:
        hourly_breakdown[int(hour)] = hrs

    peak_hour = max(hourly_breakdown.items(), key=lambda x: x[1])[0] if any(hourly_breakdown.values()) else 12
    late_night_hours = sum(hourly_breakdown[h] for h in list(range(22, 24)) + list(range(0, 5)))

    # focus sessions
    focus_query = """
    SELECT COUNT(*) as focus_sessions,
           SUM((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as focus_hours
    FROM ZOBJECT
    WHERE ZOBJECT.ZSTREAMNAME LIKE '/app/usage%'
      AND (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0 >= 2
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') >= ?
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') < ?
    """
    cursor.execute(focus_query, (start_date, end_date))
    focus_row = cursor.fetchone() or (0, 0)
    focus_sessions = int(focus_row[0] or 0)
    focus_hours = float(focus_row[1] or 0)

    # forgotten app
    unused_query = """
    SELECT ZOBJECT.ZVALUESTRING as app_name,
           SUM((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as hours
    FROM ZOBJECT
    WHERE ZOBJECT.ZSTREAMNAME LIKE '/app/usage%'
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') >= ?
      AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') < ?
    GROUP BY app_name
    HAVING hours < 1 AND hours > 0
    ORDER BY hours ASC
    LIMIT 1
    """
    cursor.execute(unused_query, (start_date, end_date))
    unused = cursor.fetchone()
    forgotten_app = unused[0].split('.')[-1].replace('-', ' ').title() if unused else "None"

    conn.close()
    temp_db.unlink()

    return {
        "year": year,
        "total_hours": int(total_hours),
        "top_apps": top_apps,
        "total_launches": total_launches,
        "longest_session": longest_session_app,
        "max_streak": max_streak,
        "weekend_hours": int(weekend_hours),
        "weekday_hours": int(weekday_hours),
        "hourly_breakdown": hourly_breakdown,
        "peak_hour": peak_hour,
        "late_night_hours": int(late_night_hours),
        "focus_sessions": focus_sessions,
        "focus_hours": int(focus_hours),
        "forgotten_app": forgotten_app,
        "wtf_spike_day": wtf_spike_day,
    }
