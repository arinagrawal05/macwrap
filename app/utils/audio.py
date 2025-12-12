import subprocess
import threading
from pathlib import Path

def play_sound(name):
    sound_path = Path(__file__).parent.parent / "assets" / "sounds" / f"{name}.mp3"
    if sound_path.exists():
        threading.Thread(target=lambda: subprocess.call(["afplay", str(sound_path)]), daemon=True).start()
