#!/usr/bin/env python3

import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from textual import events, on
from textual.app import App
from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.containers import Center, Middle

def get_screen_time_db_path():
    """Find the Screen Time database on macOS"""
    home = Path.home()
    db_path = home / "Library" / "Application Support" / "Knowledge" / "knowledgeC.db"
    return db_path if db_path.exists() else None

def get_command_history():
    """Get shell command history stats"""
    history_files = [
        Path.home() / ".zsh_history",
        Path.home() / ".bash_history",
        Path.home() / ".history"
    ]
    
    total_commands = 0
    for hist_file in history_files:
        if hist_file.exists():
            try:
                with open(hist_file, 'r', errors='ignore') as f:
                    total_commands += len(f.readlines())
            except:
                pass
    
    return total_commands

def get_file_creation_stats(year=2025):
    """Get file creation statistics for the year"""
    try:
        start_date = f"{year}-01-01"
        end_date = f"{year+1}-01-01"
        
        # Use mdfind to find files created in the year
        result = subprocess.run(
            ['mdfind', f'kMDItemFSCreationDate >= $time.iso({start_date}) && kMDItemFSCreationDate < $time.iso({end_date})'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        files = result.stdout.strip().split('\n')
        total_files = len([f for f in files if f])
        
        # Count by type
        extensions = defaultdict(int)
        for file in files:
            if file:
                ext = Path(file).suffix.lower()
                if ext:
                    extensions[ext] += 1
        
        top_types = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total": total_files,
            "top_types": top_types
        }
    except:
        return {"total": 0, "top_types": []}

def get_power_events(year=2025):
    """Get power events (sleep, wake, boot, shutdown)"""
    try:
        result = subprocess.run(
            ['pmset', '-g', 'log'],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        lines = result.stdout.split('\n')
        sleep_count = sum(1 for line in lines if 'Sleep' in line and str(year) in line)
        wake_count = sum(1 for line in lines if 'Wake' in line and str(year) in line)
        
        return {
            "sleeps": sleep_count,
            "wakes": wake_count,
            "reboots": sleep_count // 10  # Estimate
        }
    except:
        return {"sleeps": 0, "wakes": 0, "reboots": 0}

def fetch_real_stats(year: int = 2025):
    """Fetch comprehensive usage statistics from macOS"""
    db_path = get_screen_time_db_path()
    
    if not db_path:
        return create_error_stats(year, "Screen Time database not found")
    
    try:
        import shutil
        import tempfile
        temp_db = Path(tempfile.gettempdir()) / "knowledgeC_temp.db"
        shutil.copy2(db_path, temp_db)
        
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        
        start_date = f"{year}-01-01"
        end_date = f"{year + 1}-01-01"
        
        # 1. Basic app usage with launch counts
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
        
        total_hours = 0
        total_launches = 0
        top_apps = []
        longest_session_app = ("", 0)
        
        for app_name, hours, launches, longest in app_data:
            if hours > 0:
                clean_name = app_name.split('.')[-1].replace('-', ' ').title()
                if len(clean_name) > 30:
                    clean_name = clean_name[:27] + "..."
                
                total_hours += hours
                total_launches += launches
                top_apps.append((clean_name, int(hours), launches, longest))
                
                if longest > longest_session_app[1]:
                    longest_session_app = (clean_name, longest)
        
        # 2. Daily usage patterns and streaks
        daily_query = """
        SELECT 
            date(datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch')) as usage_date,
            SUM((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as daily_hours,
            COUNT(DISTINCT ZOBJECT.ZVALUESTRING) as apps_used
        FROM ZOBJECT
        WHERE ZOBJECT.ZSTREAMNAME LIKE '/app/usage%'
            AND ZOBJECT.ZVALUESTRING IS NOT NULL
            AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') >= ?
            AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') < ?
        GROUP BY usage_date
        ORDER BY usage_date
        """
        
        cursor.execute(daily_query, (start_date, end_date))
        daily_data = cursor.fetchall()
        
        # Calculate streaks
        max_streak = 0
        current_streak = 0
        prev_date = None
        weekend_hours = 0
        weekday_hours = 0
        daily_hours_list = []
        wtf_spike_day = (None, 0)
        
        for date_str, hours, apps_used in daily_data:
            daily_hours_list.append(hours)
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check for WTF spike (3x average)
            if len(daily_hours_list) > 7:
                avg = sum(daily_hours_list[-7:]) / 7
                if hours > avg * 3:
                    if hours > wtf_spike_day[1]:
                        wtf_spike_day = (date_str, hours)
            
            # Streak calculation
            if prev_date is None or (current_date - prev_date).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
            
            prev_date = current_date
            
            # Weekend vs weekday
            if current_date.weekday() >= 5:
                weekend_hours += hours
            else:
                weekday_hours += hours
        
        # 3. Hourly heatmap
        hourly_query = """
        SELECT 
            CAST(strftime('%H', datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch')) AS INTEGER) as hour,
            SUM((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as total_hours
        FROM ZOBJECT
        WHERE ZOBJECT.ZSTREAMNAME LIKE '/app/usage%'
            AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') >= ?
            AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') < ?
        GROUP BY hour
        ORDER BY total_hours DESC
        """
        
        cursor.execute(hourly_query, (start_date, end_date))
        hourly_data = cursor.fetchall()
        
        hourly_breakdown = {h: 0 for h in range(24)}
        for hour, hours in hourly_data:
            hourly_breakdown[hour] = hours
        
        peak_hour = max(hourly_breakdown.items(), key=lambda x: x[1])[0] if hourly_data else 12
        
        # Late night hours (10pm - 4am)
        late_night_hours = sum(hourly_breakdown[h] for h in list(range(22, 24)) + list(range(0, 5)))
        
        # 4. Focus hours (continuous 2+ hour sessions)
        focus_query = """
        SELECT 
            COUNT(*) as focus_sessions,
            SUM((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as focus_hours
        FROM ZOBJECT
        WHERE ZOBJECT.ZSTREAMNAME LIKE '/app/usage%'
            AND (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0 >= 2
            AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') >= ?
            AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') < ?
        """
        
        cursor.execute(focus_query, (start_date, end_date))
        focus_result = cursor.fetchone()
        focus_sessions = focus_result[0] if focus_result and focus_result[0] else 0
        focus_hours = focus_result[1] if focus_result and focus_result[1] else 0
        
        # 5. Unused apps detector (apps with <1 hour total)
        unused_query = """
        SELECT 
            ZOBJECT.ZVALUESTRING as app_name,
            SUM((ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0) as hours
        FROM ZOBJECT
        WHERE ZOBJECT.ZSTREAMNAME LIKE '/app/usage%'
            AND ZOBJECT.ZVALUESTRING IS NOT NULL
            AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') >= ?
            AND datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') < ?
        GROUP BY app_name
        HAVING hours < 1 AND hours > 0
        ORDER BY hours ASC
        LIMIT 1
        """
        
        cursor.execute(unused_query, (start_date, end_date))
        unused_result = cursor.fetchone()
        forgotten_app = "None"
        if unused_result:
            forgotten_app = unused_result[0].split('.')[-1].replace('-', ' ').title()
        
        conn.close()
        temp_db.unlink()
        
        # Get system stats
        command_count = get_command_history()
        file_stats = get_file_creation_stats(year)
        power_events = get_power_events(year)
        
        personality = generate_personality(top_apps, total_hours, peak_hour, late_night_hours, focus_hours)
        
        return {
            "year": year,
            "total_hours": int(total_hours),
            "top_apps": top_apps[:5] if top_apps else [("No data", 0, 0, 0)],
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
            "personality": personality,
            "command_count": command_count,
            "file_stats": file_stats,
            "power_events": power_events,
        }
        
    except Exception as e:
        return create_error_stats(year, str(e))

def create_error_stats(year, error_msg):
    """Create error response with structure"""
    return {
        "year": year,
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

def generate_personality(top_apps, total_hours, peak_hour, late_night_hours, focus_hours):
    """Generate personality based on comprehensive usage patterns"""
    if not top_apps or total_hours == 0:
        return "Digital Minimalist"
    
    top_app = top_apps[0][0].lower()
    
    personalities = {
        "chrome": "Professional Tab Hoarder",
        "safari": "Apple Ecosystem Devotee",
        "firefox": "Privacy-Conscious Browser",
        "vscode": "Code Wizard",
        "xcode": "Apple Developer",
        "terminal": "Command Line Warrior",
        "iterm": "Terminal Power User",
        "slack": "Communication Champion",
        "zoom": "Meeting Marathon Runner",
        "spotify": "Music-Powered Worker",
        "photoshop": "Creative Visionary",
        "figma": "Design Perfectionist",
        "notion": "Organization Guru",
        "discord": "Community Builder",
    }
    
    personality = "Digital Professional"
    for key, value in personalities.items():
        if key in top_app:
            personality = value
            break
    
    # Modifiers
    if focus_hours > 500:
        personality = f"Deep Focus {personality}"
    elif total_hours > 2000:
        personality = f"Hardcore {personality}"
    
    if late_night_hours > total_hours * 0.3:
        personality = f"Night Owl {personality}"
    elif peak_hour >= 5 and peak_hour <= 8:
        personality = f"Early Bird {personality}"
    
    return personality

# Fetch stats
stats = fetch_real_stats(2025)

class IntroScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                yield Static("[bold magenta]macwrap[/bold magenta]\n[cyan]Your Mac. Your 2025.[/cyan]", id="title")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#title")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=2.0, easing="out_quad")
        self.set_timer(3.5, lambda: self.app.push_screen(LoadingScreen()))

class LoadingScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                yield Static(
                    "[bold yellow]Unwrapping your Mac year...[/bold yellow]\n\n"
                    "[yellow]Analyzing your digital footprint...[/yellow]",
                    id="loading"
                )
        yield Footer()

    def on_mount(self):
        w = self.query_one("#loading")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)
        self.set_timer(3, lambda: self.app.push_screen(TotalTimeScreen()))

class TotalTimeScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                if stats.get("error"):
                    content = (
                        "[bold red]Unable to read Screen Time data[/bold red]\n\n"
                        f"[yellow]Error: {stats['error']}[/yellow]\n\n"
                        "[dim]Try running with sudo or enable Screen Time[/dim]"
                    )
                elif stats['total_hours'] == 0:
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
                        f"[green]{stats['total_launches']:,} total app launches[/green]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                yield Static(content, id="total")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#total")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=2.0)

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(TopAppsScreen())

class TopAppsScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                content = "[bold magenta]Your Top 5 Apps of 2025[/bold magenta]\n\n"
                if stats['total_hours'] > 0:
                    for i, (app, hrs, launches, _) in enumerate(stats["top_apps"], 1):
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

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(StreakScreen())

class StreakScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                if stats['max_streak'] > 0:
                    content = (
                        f"[bold yellow]🔥 Your Longest Streak 🔥[/bold yellow]\n\n"
                        f"[bold white]{stats['max_streak']} days[/bold white]\n"
                        "of consecutive Mac usage\n\n"
                        "[green]Dedication level: Expert[/green]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = "[yellow]No streak data available[/yellow]\n\n[dim]Press SPACE or ENTER[/dim]"
                yield Static(content, id="streak")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#streak")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(FocusHoursScreen())

class FocusHoursScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                if stats['focus_hours'] > 0:
                    content = (
                        f"[bold cyan]Deep Focus Time[/bold cyan]\n\n"
                        f"[bold white]{stats['focus_hours']} hours[/bold white]\n"
                        f"across {stats['focus_sessions']} sessions\n\n"
                        "[italic]Sessions of 2+ hours each[/italic]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = "[yellow]No deep focus sessions detected[/yellow]\n\n[dim]Press SPACE or ENTER[/dim]"
                yield Static(content, id="focus")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#focus")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(WeekendVsWeekdayScreen())

class WeekendVsWeekdayScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                total = stats['weekend_hours'] + stats['weekday_hours']
                if total > 0:
                    weekend_pct = int((stats['weekend_hours'] / total) * 100)
                    weekday_pct = 100 - weekend_pct
                    
                    winner = "Weekends" if weekend_pct > 50 else "Weekdays"
                    
                    content = (
                        f"[bold magenta]Weekend vs Weekday[/bold magenta]\n\n"
                        f"[yellow]Weekends:[/yellow] {stats['weekend_hours']} hrs ({weekend_pct}%)\n"
                        f"[cyan]Weekdays:[/cyan] {stats['weekday_hours']} hrs ({weekday_pct}%)\n\n"
                        f"[bold green]Winner: {winner}[/bold green]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = "[yellow]No usage data[/yellow]\n\n[dim]Press SPACE or ENTER[/dim]"
                yield Static(content, id="weekend")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#weekend")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(HourlyHeatmapScreen())

class HourlyHeatmapScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                content = "[bold cyan]Your Hourly Heatmap[/bold cyan]\n\n"
                
                hourly = stats['hourly_breakdown']
                if sum(hourly.values()) > 0:
                    max_hours = max(hourly.values())
                    
                    for hour in range(24):
                        hours = hourly[hour]
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

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(ForgottenAppScreen())

class ForgottenAppScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                content = (
                    f"[bold yellow]The App You Forgot You Had[/bold yellow]\n\n"
                    f"[bold white]{stats['forgotten_app']}[/bold white]\n\n"
                    "[italic]Less than 1 hour total usage[/italic]\n\n"
                    "[dim]Maybe it's time to uninstall?[/dim]\n\n"
                    "[dim]Press SPACE or ENTER to continue[/dim]"
                )
                yield Static(content, id="forgotten")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#forgotten")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(WTFSpikeScreen())

class WTFSpikeScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                if stats['wtf_spike_day'][0]:
                    date_str = stats['wtf_spike_day'][0]
                    hours = int(stats['wtf_spike_day'][1])
                    content = (
                        f"[bold red]The 'WTF' Spike Day[/bold red]\n\n"
                        f"[bold white]{date_str}[/bold white]\n"
                        f"{hours} hours in a single day!\n\n"
                        "[italic]3x your weekly average[/italic]\n\n"
                        "[dim]What happened that day?[/dim]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = (
                        "[yellow]No extreme spike days detected[/yellow]\n\n"
                        "[green]Your usage was consistent![/green]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                yield Static(content, id="spike")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#spike")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(LateNightScreen())

class LateNightScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                if stats['late_night_hours'] > 0:
                    pct = int((stats['late_night_hours'] / stats['total_hours']) * 100) if stats['total_hours'] > 0 else 0
                    content = (
                        f"[bold magenta]🌙 Late Night Sessions 🌙[/bold magenta]\n\n"
                        f"[bold white]{stats['late_night_hours']} hours[/bold white]\n"
                        "between 10pm - 4am\n\n"
                        f"[yellow]That's {pct}% of your total time![/yellow]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                else:
                    content = (
                        "[green]No late night sessions![/green]\n\n"
                        "[italic]Healthy sleep schedule detected[/italic]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                yield Static(content, id="latenight")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#latenight")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(LongestSessionScreen())

class LongestSessionScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                app, hours = stats['longest_session']
                if hours > 0:
                    content = (
                        f"[bold cyan]Longest Single Session[/bold cyan]\n\n"
                        f"[bold white]{app}[/bold white]\n"
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

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(CommandLineScreen())

class CommandLineScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                if stats['command_count'] > 0:
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

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(FileCreationScreen())

class FileCreationScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                if stats['file_stats']['total'] > 0:
                    content = (
                        f"[bold magenta]📁 File Creation Stats[/bold magenta]\n\n"
                        f"[bold white]{stats['file_stats']['total']:,}[/bold white]\n"
                        "new files created in 2025\n\n"
                    )
                    
                    if stats['file_stats']['top_types']:
                        content += "Top file types:\n"
                        for ext, count in stats['file_stats']['top_types'][:3]:
                            content += f"  {ext}: {count:,}\n"
                    
                    content += "\n[dim]Press SPACE or ENTER to continue[/dim]"
                else:
                    content = (
                        "[yellow]No file creation data[/yellow]\n\n"
                        "[dim]Press SPACE or ENTER to continue[/dim]"
                    )
                yield Static(content, id="files")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#files")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(PowerEventsScreen())

class PowerEventsScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                pe = stats['power_events']
                content = (
                    f"[bold yellow]⚡ Power Events[/bold yellow]\n\n"
                    f"Sleeps: [bold]{pe['sleeps']}[/bold]\n"
                    f"Wakes: [bold]{pe['wakes']}[/bold]\n"
                    f"Reboots: [bold]{pe['reboots']}[/bold]\n\n"
                    "[italic]Your Mac's sleep cycle[/italic]\n\n"
                    "[dim]Press SPACE or ENTER to continue[/dim]"
                )
                yield Static(content, id="power")
        yield Footer()

    def on_mount(self):
        w = self.query_one("#power")
        w.styles.opacity = 0
        w.styles.animate("opacity", value=1.0, duration=1.8)

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(PersonalityScreen())

class PersonalityScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                yield Static(
                    f"[bold italic cyan]Your 2025 Mac Personality:[/bold italic cyan]\n\n"
                    f"[bold yellow]{stats['personality']}[/bold yellow]\n\n"
                    "[dim]Press SPACE or ENTER for finale[/dim]",
                    id="personality"
                )
        yield Footer()

    def on_mount(self):
        w = self.query_one("#personality")
        w.styles.opacity = 0
        w.styles.rotate = -8
        w.styles.animate("opacity", value=1.0, duration=2.0)
        w.styles.animate("rotate", value=0, duration=2.0, easing="out_back")

    @on(events.Key)
    def on_key(self, event):
        if event.key in ("space", "enter"):
            self.app.push_screen(FinaleScreen())

class FinaleScreen(Screen):
    def compose(self):
        yield Header()
        with Center():
            with Middle():
                if stats['total_hours'] > 0 and stats['top_apps']:
                    share_text = (
                        f"> {stats['total_hours']:,} hrs - "
                        f"{stats['total_launches']:,} launches - "
                        f"{stats['max_streak']} day streak\n"
                        f"> Top: {stats['top_apps'][0][0]} - "
                        f"{stats['personality']}\n"
                    )
                else:
                    share_text = "> Enable Screen Time to see your stats!\n"
                
                share = (
                    "[bold magenta]Happy end of 2025![/bold magenta]\n\n"
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
        self.dark = True
        self.push_screen(IntroScreen())

if __name__ == "__main__":
    MacWrap().run()