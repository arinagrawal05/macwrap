import subprocess
from collections import defaultdict
from pathlib import Path

def get_file_creation_stats(year=2025):
    try:
        start = f"{year}-01-01"
        end = f"{year+1}-01-01"

        result = subprocess.run(
            ['mdfind', f'kMDItemFSCreationDate >= $time.iso({start}) && kMDItemFSCreationDate < $time.iso({end})'],
            capture_output=True,
            text=True,
            timeout=5
        )

        files = [f for f in result.stdout.split("\n") if f]
        exts = defaultdict(int)

        for f in files:
            ext = Path(f).suffix.lower()
            if ext:
                exts[ext] += 1

        return {
            "total": len(files),
            "top_types": sorted(exts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    except:
        return {"total": 0, "top_types": []}
