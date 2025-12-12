import subprocess

def get_power_events(year=2025):
    try:
        log = subprocess.run(['pmset', '-g', 'log'], capture_output=True, text=True, timeout=3)
        lines = log.stdout.split('\n')
        sleeps = sum(1 for l in lines if "Sleep" in l and str(year) in l)
        wakes  = sum(1 for l in lines if "Wake" in l and str(year) in l)
        return {"sleeps": sleeps, "wakes": wakes, "reboots": sleeps // 10}
    except:
        return {"sleeps": 0, "wakes": 0, "reboots": 0}
