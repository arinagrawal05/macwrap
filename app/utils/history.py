from pathlib import Path

def get_command_history():
    history_files = [
        Path.home() / ".zsh_history",
        Path.home() / ".bash_history",
        Path.home() / ".history"
    ]
    count = 0
    for f in history_files:
        if f.exists():
            try:
                count += sum(1 for _ in open(f, 'r', errors='ignore'))
            except:
                pass
    return count
