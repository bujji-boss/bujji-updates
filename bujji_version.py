from pathlib import Path

VERSION_FILE = Path("/storage/emulated/0/BUJJI/version.txt")
CURRENT_VERSION = "1.0.0"

if VERSION_FILE.exists():
    version = VERSION_FILE.read_text().strip()
else:
    VERSION_FILE.write_text(CURRENT_VERSION)
    version = CURRENT_VERSION

print("🤖 BUJJI VERSION:", version)
print("🔄 AUTO-UPDATE SYSTEM: READY")
