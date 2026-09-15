import json
from pathlib import Path

class BrainRouter:
    def __init__(self):
        path = Path(__file__).parent / "capabilities.json"
        self.data = json.loads(path.read_text())
        self.capabilities = set(self.data.get("capabilities", []))

    def route(self, text):
        text = text.lower().strip()

        if any(x in text for x in ["whatsapp", "వాట్సాప్", "వాట్సప్"]):
            return "whatsapp"

        if any(x in text for x in ["instagram", "ఇన్స్టాగ్రామ్"]):
            return "instagram"

        if any(x in text for x in ["phonepe", "phone pe", "phone pay", "phone per"]):
            return "phonepe"

        if "youtube" in text or "యూట్యూబ్" in text:
            return "youtube"

        return "ai_chat"
