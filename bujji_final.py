import subprocess
import time
import os
import re
from core.brain_router import BrainRouter

BASE = "/storage/emulated/0/BUJJI"
brain_router = BrainRouter()
AAC = os.path.join(BASE, "final_wake.aac")
WAV = os.path.join(BASE, "final_wake_16k.wav")
SCAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_bujji.py")
MODEL = os.path.join(BASE, "models", "gemma3_1b.gguf")


def speak(text):
    if not text:
        return

    print("🤖 BUJJI:", text, flush=True)

    subprocess.Popen(
        [
            "termux-tts-speak",
            "-e", "com.google.android.tts",
            "-s", "ALARM",
            "-r", "1.3",
            text
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def record_wake():
    os.makedirs(BASE, exist_ok=True)

    for f in (AAC, WAV):
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass

    subprocess.run(
        ["termux-microphone-record", "-q"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    r = subprocess.run(
        [
            "termux-microphone-record",
            "-l", "3",
            "-e", "aac",
            "-b", "128",
            "-r", "16000",
            "-c", "1",
            "-f", AAC
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if r.returncode != 0:
        return False

    time.sleep(3.3)

    return os.path.exists(AAC)


def convert_audio():
    r = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel", "quiet",
            "-i", AAC,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            WAV
        ]
    )

    return r.returncode == 0 and os.path.exists(WAV)


def detect_bujji():
    r = subprocess.run(
        ["python", SCAN, WAV],
        capture_output=True,
        text=True
    )

    return "BUJJI TRIGGER" in r.stdout


def listen_command():
    try:
        cmd = [
            "/data/data/com.termux/files/usr/libexec/termux-api",
            "SpeechToText"
        ]

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )

        latest = ""

        for line in p.stdout:
            text = line.strip().lower()

            if not text:
                continue

            print("👤 BOSS VOICE:", text, flush=True)

            text = text.replace("hey bujji", "", 1).strip()
            text = text.replace("hey booji", "", 1).strip()
            text = text.replace("hey budgie", "", 1).strip()
            text = text.replace("bujji", "", 1).strip()

            if not text:
                continue

            latest = text
            print("👤 BOSS:", text, flush=True)

            # ⚡ Partial-result fast path
            action_words = [
                "open", "launch", "start", "close",
                "whatsapp", "instagram", "phonepe",
                "youtube", "free fire", "chatgpt",
                "ludo", "snapchat", "meesho", "docs"
            ]

            app_words = [
                "whatsapp", "instagram", "phonepe", "youtube",
                "free fire", "chatgpt", "ludo", "snapchat",
                "meesho", "docs"
            ]
            action_verbs = ["open", "launch", "start", "close"]

            has_app = any(app in text for app in app_words)
            has_action = any(verb in text.split() for verb in action_verbs)

            if has_app and has_action:
                try:
                    p.terminate()
                except:
                    pass
                return text

        return latest

    except Exception as e:
        print("⚠️ STT ERROR:", e, flush=True)
        return ""

def open_app(package):
    try:
        subprocess.Popen(
            [
                "am", "start",
                "-a", "android.intent.action.MAIN",
                "-c", "android.intent.category.LAUNCHER",
                "-p", package
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        print("⚠️ APP OPEN ERROR:", e, flush=True)
        return False


def normalize_command(text):
    if not text:
        return ""

    text = text.lower().strip()

    replacements = {
        "phone per": "phonepe",
        "phone pay": "phonepe",
        "phone pe": "phonepe",
        "phone per": "phonepe",
        "ఫోన్ పే": "phonepe",
        "ఫోన్‌పే": "phonepe",
        "వాట్సాప్": "whatsapp",
        "వాట్సప్": "whatsapp",
        "ఇన్స్టాగ్రామ్": "instagram",
        "యూట్యూబ్": "youtube"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


def handle_command(command):
    if not command:
        speak("Boss, మళ్ళీ చెప్పండి")
        return

    command = normalize_command(command)

    # 🧠 BUJJI BRAIN ROUTER
    route = brain_router.route(command)
    print("🧠 BRAIN ROUTE:", route)

    print("⚙️ COMMAND:", command)

    if command in ["hello", "hi", "hey"]:
        speak("హలో Boss")
        return

    if "how are you" in command:
        speak("నేను బాగున్నాను Boss")
        return

    if "your name" in command or "who are you" in command:
        speak("నేను BUJJI, మీ personal assistant")
        return

    if "thank" in command:
        speak("మీకు స్వాగతం Boss")
        return

    apps = {
        "whatsapp": "com.whatsapp",
        "instagram": "com.instagram.android",
        "phonepe": "com.phonepe.app",
        "free fire": "com.dts.freefiremax",
        "freefire": "com.dts.freefiremax",
        "chatgpt": "com.openai.chatgpt",
        "ludo": "com.ludo.king",
        "ludo king": "com.ludo.king",
        "snapchat": "com.snapchat.android",
        "meesho": "com.meesho.supply",
        "docs": "com.google.android.apps.docs"
    }

    for name, package in apps.items():

        open_commands = [
            "open " + name,
            name + " open",
            "launch " + name,
            name + " launch",
            "start " + name,
            name + " start"
        ]

        words = command.split()
        if command == name or command in open_commands or (
            name in words and any(x in words for x in ["open", "launch", "start"])
        ):
            open_app(package)
            speak("సరే Boss, " + name + " ఓపెన్ చేస్తున్నాను")
            return

    if command == "close" or command.startswith("close ") or command.endswith(" close"):
        subprocess.run(["am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        speak("App close చేశాను Boss")
        return

    if "youtube" in command:
        subprocess.run(
            [
                "termux-open-url",
                "https://www.youtube.com"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        speak("YouTube ఓపెన్ చేస్తున్నాను Boss")
        return

    if command in [
        "stop",
        "exit",
        "bye",
        "goodbye",
        "బయ్",
        "ఆపు"
    ]:
        speak("సరే Boss")
        return

    reply = ask_ai(command)
    speak(reply)


def main():

    print("")
    print("================================")
    print("       🤖 BUJJI ONLINE")
    print("       👑 BOSS READY")
    print("================================")
    print("")

    print("🤖 BUJJI: BUJJI online Boss", flush=True)
    speak("BUJJI online Boss")

    while True:
        try:

            if not record_wake():
                continue

            if not convert_audio():
                continue

            if detect_bujji():

                print("")
                print("🔥 BUJJI TRIGGERED! 🔥")

                speak("Yes Boss, చెప్పండి")

                command = listen_command()

                handle_command(command)

                time.sleep(0.05)

        except KeyboardInterrupt:

            print("")
            speak("BUJJI offline")
            break

        except:

            time.sleep(1)


if __name__ == "__main__":
    main()
