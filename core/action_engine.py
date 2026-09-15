import re

class ActionEngine:
    def __init__(self):
        self.actions = {}

    def register(self, name, keywords, function):
        self.actions[name] = {
            "keywords": keywords,
            "function": function
        }

    def understand(self, text):
        text = text.lower().strip()

        for name, action in self.actions.items():
            if any(re.search(r"\b" + re.escape(k) + r"\b", text) for k in action["keywords"]):
                return name, action["function"]

        return None, None

    def run(self, text):
        name, function = self.understand(text)

        if function:
            return function(text)

        return None
