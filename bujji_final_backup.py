import subprocess
import time
import os
import re

BASE = "/storage/emulated/0/BUJJI"
AAC = os.path.join(BASE, "final_wake.aac")
WAV = os.path.join(BASE, "final_wake_16k.wav")
SCAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_bujji.py")
MODEL = os.path.join(BASE, "models", "gemma3_1b.gguf")


def speak(text):
    if not text:
        return

    print("🤖 BUJJI:", text, flush=True)

    subprocess.run(
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
        r = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True,
            text=True,
            timeout=15
        )

        text = r.stdout.strip().lower()

        print("👤 BOSS VOICE:", text)

        text = text.replace("hey bujji", "", 1).strip()
        text = text.replace("hey booji", "", 1).strip()
        text = text.replace("hey budgie", "", 1).strip()
        text = text.replace("bujji", "", 1).strip()

        if text:
            print("👤 BOSS:", text)

        return text

    except:
        return ""


def open_app(package):
    activities = {
        "com.whatsapp": "com.whatsapp/.Main",
        "com.instagram.android":
            "com.instagram.android/.activity.MainTabActivity",
        "com.phonepe.app":
            "com.phonepe.app/.ui.activity.Navigator_MainActivity"
    }

    component = activities.get(package)

    if component:
        subprocess.run(
            ["am", "start", "-n", component],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        subprocess.run(
            [
                "am", "start",
                "-a", "android.intent.action.MAIN",
                "-c", "android.intent.category.LAUNCHER",
                "-p", package
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


def ask_ai(command):
    if not command or not os.path.exists(MODEL):
        return "Boss, నాకు అర్థం కాలేదు."

    prompt = f"""
You are BUJJI, Boss's personal AI assistant.

Rules:
1. Reply only in simple natural Telugu.
2. Call the user Boss.
3. Keep replies short.
4. Do not use unnecessary English.
5. Do not invent actions that you cannot perform.

User command:
{command}

BUJJI:
"""

    try:
        r = subprocess.run(
            [
                "llama-cli",
                "-m", MODEL,
                "-p", prompt,
                "-n", "60",
                "-st"
            ],
            capture_output=True,
            text=True,
            timeout=45
        )

        output = r.stdout.strip()

        if "BUJJI:" in output:
            output = output.split("BUJJI:", 1)[1]

        output = re.split(
            r"\[ Prompt:|\[ Generation:|Exiting\.\.\.",
            output,
            maxsplit=1
        )[0].strip()

        output = output.replace("<end_of_turn>", "").strip()

        if not output:
            return "Boss, చెప్పండి."

        return output

    except:
        return "Boss, AI brain ప్రస్తుతం స్పందించలేదు."


def normalize_command(command):
    command = command.lower().strip()

    replacements = {
        "వాట్సాప్": "whatsapp",
        "వాట్సప్": "whatsapp",
        "వాట్సాప్ ఓపెన్": "open whatsapp",
        "వాట్సాప్ ఓపెన్ చెయ్యి": "open whatsapp",
        "వాట్సప్ ఓపెన్": "open whatsapp",

        "ఇన్స్టాగ్రామ్": "instagram",
        "ఇన్‌స్టాగ్రామ్": "instagram",

        "ఫోన్ పే": "phonepe",
        "ఫోన్‌పే": "phonepe",

        "యూట్యూబ్": "youtube",
        "యూట్యూబు": "youtube",

        "చాట్ జిపిటి": "chatgpt",
        "చాట్‌జిపిటి": "chatgpt",

        "ఫ్రీ ఫైర్": "free fire",
        "లూడో": "ludo",
        "స్నాప్‌చాట్": "snapchat",
        "స్నాప్ చాట్": "snapchat",
        "మీషో": "meesho",
        "డాక్స్": "docs"
    }

    for telugu, english in replacements.items():
        if telugu in command:
            command = command.replace(telugu, english)

    command = re.sub(r"\s+", " ", command).strip()

    return command


def handle_command(command):
    if not command:
        speak("Boss, మళ్ళీ చెప్పండి")
        return

    command = normalize_command(command)

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

    subprocess.run(["termux-tts-speak", "-e", "com.google.android.tts", "-s", "ALARM", "-r", "1.3", ""], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("🤖 BUJJI: BUJJI online Boss", flush=True)
    subprocess.run(["termux-tts-speak", "-e", "com.google.android.tts", "-s", "ALARM", "-r", "1.3", "BUJJI online Boss"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
