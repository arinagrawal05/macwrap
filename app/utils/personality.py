def generate_personality(top_apps, total_hours, peak_hour, late_night_hours, focus_hours):
    if not top_apps or total_hours == 0:
        return "Digital Minimalist"

    top_app = top_apps[0][0].lower() if top_apps else ""

    personalities = {
        "chrome": "Professional Tab Hoarder",
        "safari": "Apple Ecosystem Devotee",
        "firefox": "Privacy-Conscious Browser",
        "vscode": "Code Wizard",
        "xcode": "Apple Developer",
        "terminal": "Command Line Warrior",
        "spotify": "Music-Powered Worker",
        "photoshop": "Creative Visionary",
        "figma": "Design Perfectionist",
        "notion": "Organization Guru",
    }

    personality = "Digital Professional"
    for key, value in personalities.items():
        if key in top_app:
            personality = value
            break

    if focus_hours > 500:
        personality = f"Deep Focus {personality}"
    elif total_hours > 2000:
        personality = f"Hardcore {personality}"

    if total_hours and late_night_hours > total_hours * 0.3:
        personality = f"Night Owl {personality}"
    elif 5 <= peak_hour <= 8:
        personality = f"Early Bird {personality}"

    return personality
