"""Ovoz: eshitish (speech-to-text) va gapirish (text-to-speech)."""
import asyncio
import os
import tempfile

from . import config

try:
    import speech_recognition as sr
except ImportError:  # mikrofon kutubxonasi o'rnatilmagan bo'lsa
    sr = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame
except ImportError:
    pygame = None


class Voice:
    def __init__(self):
        self.recognizer = sr.Recognizer() if sr else None
        self.mic_available = False
        if sr:
            try:
                sr.Microphone()
                self.mic_available = True
            except Exception:
                self.mic_available = False
        if pygame:
            try:
                pygame.mixer.init()
            except Exception:
                pass

    # ---------- Gapirish ----------
    def speak(self, text: str) -> None:
        print(f"\n🤖 Muza: {text}\n")
        if not (edge_tts and pygame and pygame.mixer.get_init()):
            return
        try:
            path = os.path.join(tempfile.gettempdir(), "muza_tts.mp3")
            asyncio.run(edge_tts.Communicate(text, config.TTS_VOICE).save(path))
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(20)
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"(Ovoz chiqarishda xato: {e})")

    # ---------- Eshitish ----------
    def listen(self, timeout: float = 6, phrase_limit: float = 15) -> str | None:
        """Mikrofondan bitta gapni eshitib, matnga aylantiradi."""
        if not self.mic_available:
            return None
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            except sr.WaitTimeoutError:
                return None
        try:
            text = self.recognizer.recognize_google(audio, language=config.STT_LANGUAGE)
            print(f"🎤 Siz: {text}")
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"(Nutqni tanish xizmatida xato: {e})")
            return None
