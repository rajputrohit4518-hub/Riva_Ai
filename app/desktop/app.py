class RivaDesktopApp:
    def __init__(self):
        self.running = False
        self.history = []
        self.voice_active = False
    def start(self):
        self.running = True
    def stop(self):
        self.running = False
    def add_message(self, sender: str, text: str):
        if text.strip():
            self.history.append({'sender': sender, 'text': text})
    def toggle_voice(self):
        self.voice_active = not self.voice_active
        return self.voice_active
    def clear_history(self):
        self.history.clear()

