import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = "/data/data/com.termux/files/usr/bin/python"

while True:
    print("🛡️ BUJJI SUPERVISOR ONLINE", flush=True)

    updater = subprocess.run(
        [PYTHON, str(ROOT / "auto_updater.py")],
        cwd=ROOT
    )

    print("🚀 Starting BUJJI...", flush=True)

    process = subprocess.Popen(
        [PYTHON, str(ROOT / "bujji_final.py")],
        cwd=ROOT
    )

    process.wait()

    print("⚠️ BUJJI stopped. Restarting...", flush=True)
    time.sleep(2)
