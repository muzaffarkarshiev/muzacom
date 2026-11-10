"""Muza sozlamalari. Qiymatlar .env faylidan o'qiladi."""
import os

from dotenv import load_dotenv

load_dotenv()

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("MUZA_MODEL", "claude-sonnet-5-5")

# Uyg'otuvchi so'z (wake word)
WAKE_WORDS = [w.strip().lower() for w in os.getenv("MUZA_WAKE_WORDS", "muza,муза").split(",")]

# Nutqni tanish tili (Google Speech Recognition)
STT_LANGUAGE = os.getenv("MUZA_STT_LANGUAGE", "uz-UZ")

# Ovoz (edge-tts). O'zbekcha: uz-UZ-MadinaNeural (ayol), uz-UZ-SardorNeural (erkak)
TTS_VOICE = os.getenv("MUZA_TTS_VOICE", "uz-UZ-MadinaNeural")

# Foydalanuvchi ismi
USER_NAME = os.getenv("MUZA_USER_NAME", "Muzaffar")

# Shahar (ob-havo uchun)
DEFAULT_CITY = os.getenv("MUZA_CITY", "Tashkent")

# Xotira fayli
MEMORY_FILE = os.getenv("MUZA_MEMORY_FILE", os.path.expanduser("~/.muza_memory.json"))

SYSTEM_PROMPT = f"""Sen — Muza, {USER_NAME}ning shaxsiy sun'iy intellekt yordamchisisan.
Temir odamdagi J.A.R.V.I.S. kabi: aqlli, xushmuomala, biroz hazilkash, doim tayyor.
Qoidalar:
- Har doim o'zbek tilida (lotin yozuvida) javob ber, agar foydalanuvchi boshqa tilda gapirmasa.
- Javoblaring qisqa va aniq bo'lsin — ular ovoz chiqarib o'qiladi. Markdown, ro'yxat belgilari va emoji ishlatma.
- {USER_NAME}ga hurmat bilan murojaat qil ("janob" yoki ismi bilan).
- Kompyuterda biror ish bajarish kerak bo'lsa, berilgan vositalardan (tools) foydalan.
- Bilmagan narsangni o'ylab topma; kerak bo'lsa internetdan qidir.
"""
