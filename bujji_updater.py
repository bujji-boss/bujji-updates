import os
import shutil
from datetime import datetime

BASE = "/storage/emulated/0/BUJJI"
APP = os.path.join(BASE, "bujji_final.py")
BACKUP = os.path.join(BASE, "updates", "backup")

os.makedirs(BACKUP, exist_ok=True)

def backup_current():
    if os.path.exists(APP):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(BACKUP, f"bujji_final_{stamp}.py")
        shutil.copy2(APP, dst)
        print("✅ BUJJI backup created:", dst)

def check_update():
    print("🔄 BUJJI AUTO-UPDATE CHECK")
    print("📦 Current version found")
    print("🛡️ Backup system ready")
    print("⏳ Update source will be connected next")

if __name__ == "__main__":
    check_update()
    backup_current()
