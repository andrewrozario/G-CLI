import abc
import logging
import subprocess
from typing import Optional

class STTProvider(abc.ABC):
    """Abstract Base Class for Speech-to-Text Providers."""
    @abc.abstractmethod
    def listen(self) -> Optional[str]:
        """Listens to the microphone and returns recognized text."""
        pass

class TTSProvider(abc.ABC):
    """Abstract Base Class for Text-to-Speech Providers."""
    @abc.abstractmethod
    def speak(self, text: str):
        """Converts text to speech and plays it."""
        pass

class DarwinTTSProvider(TTSProvider):
    """macOS native 'say' command TTS."""
    def speak(self, text: str):
        try:
            subprocess.run(["say", text], check=True)
        except Exception as e:
            logging.error(f"Darwin TTS failed: {e}")

class SpeechRecognitionProvider(STTProvider):
    """Wrapper for the SpeechRecognition library."""
    def __init__(self):
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        except ImportError:
            logging.error("speech_recognition or pyaudio not installed. Voice input will not work.")
            self.recognizer = None

    def listen(self) -> Optional[str]:
        if not self.recognizer:
            return None
            
        import speech_recognition as sr
        with self.microphone as source:
            logging.info("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
        try:
            text = self.recognizer.recognize_google(audio)
            logging.info(f"Voice recognized: {text}")
            return text
        except sr.UnknownValueError:
            logging.warning("Speech recognition could not understand audio.")
            return None
        except sr.RequestError as e:
            logging.error(f"Speech recognition service error: {e}")
            return None
