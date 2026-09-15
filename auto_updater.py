import subprocess
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / ".bujji_backup"

def run(cmd):
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True
    )

def backup():
    BACKUP.mkdir(exist_ok=True)

    for name in ["bujji_final.py", "core", "features"]:
        src = ROOT / name
        dst = BACKUP / name

        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        elif src.exists():
            shutil.copy2(src, dst)

    (BACKUP / "timestamp").write_text(
        datetime.now().isoformat()
    )

def rollback():
    if not BACKUP.exists():
        return False

    for name in ["bujji_final.py", "core", "features"]:
        src = BACKUP / name
        dst = ROOT / name

        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        elif src.exists():
            shutil.copy2(src, dst)

    return True

def test():
    result = run([
        "python",
        "-m",
        "py_compile",
        "bujji_final.py"
    ])
    return result.returncode == 0

def update():
    print("🔄 BUJJI AUTO UPDATE CHECK...")

    backup()

    fetch = run(["git", "fetch", "origin", "main"])

    if fetch.returncode != 0:
        print("⚠️ GitHub check failed")
        return False

    local = run(["git", "rev-parse", "HEAD"])
    remote = run(["git", "rev-parse", "origin/main"])

    if local.stdout.strip() == remote.stdout.strip():
        print("✅ BUJJI already up to date")
        return True

    print("⬇️ New BUJJI update found")

    pull = run(["git", "pull", "--ff-only", "origin", "main"])

    if pull.returncode != 0:
        print("❌ Update failed — rolling back")
        rollback()
        return False

    if not test():
        print("❌ New version failed test — rolling back")
        rollback()
        return False

    print("✅ BUJJI updated successfully")
    return True

if __name__ == "__main__":
    update()
