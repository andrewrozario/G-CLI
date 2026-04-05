import logging
from typing import Optional
from gaia_cmd.core.voice.provider import STTProvider, TTSProvider, DarwinTTSProvider, SpeechRecognitionProvider

class VoiceManager:
    """
    Main interface for Voice Interaction in Gaia CLI.
    Manages Speech-to-Text and Text-to-Speech.
    """
    def __init__(self, stt: Optional[STTProvider] = None, tts: Optional[TTSProvider] = None):
        self.stt = stt or SpeechRecognitionProvider()
        self.tts = tts or DarwinTTSProvider()
        self.logger = logging.getLogger("VoiceManager")

    def listen_for_command(self) -> Optional[str]:
        """Listens for a voice command and returns the text."""
        self.logger.info("Awaiting voice command...")
        return self.stt.listen()

    def speak(self, text: str):
        """Speaks the provided text."""
        self.logger.info(f"Speaking: {text}")
        self.tts.speak(text)

    def feedback(self, text: str):
        """Unified method for UI logging and voice feedback."""
        # This could be integrated into GaiaUI
        print(f"Gaia: {text}")
        self.speak(text)
