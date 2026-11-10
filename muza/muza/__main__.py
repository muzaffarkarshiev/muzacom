"""Ishga tushirish: python -m muza  (ovozli)   yoki   python -m muza --text  (yozma)."""
import argparse
import datetime as dt
import sys

from . import config
from .brain import Brain
from .voice import Voice

EXIT_WORDS = {"xayr", "chiqish", "exit", "quit", "tamom", "o'chir"}
RESET_WORDS = {"yangi suhbat", "unut", "reset"}


def greeting() -> str:
    h = dt.datetime.now().hour
    if h < 5:
        part = "Xayrli tun"
    elif h < 12:
        part = "Xayrli tong"
    elif h < 18:
        part = "Xayrli kun"
    else:
        part = "Xayrli kech"
    return f"{part}, {config.USER_NAME}. Muza xizmatingizda. Nima qilamiz?"


def strip_wake_word(text: str) -> str | None:
    """Agar gapda uyg'otuvchi so'z bo'lsa, undan keyingi buyruqni qaytaradi."""
    low = text.lower()
    for w in config.WAKE_WORDS:
        if w in low:
            return text[low.index(w) + len(w):].strip(" ,.!?")
    return None


def handle(brain: Brain, voice: Voice, text: str) -> bool:
    """Buyruqni bajaradi. False qaytsa — dastur to'xtaydi."""
    low = text.lower().strip()
    if low in EXIT_WORDS:
        voice.speak(f"Xayr, {config.USER_NAME}. Kerak bo'lsam chaqiring.")
        return False
    if low in RESET_WORDS:
        brain.reset()
        voice.speak("Suhbat tozalandi.")
        return True
    try:
        voice.speak(brain.ask(text))
    except Exception as e:
        voice.speak(f"Kechirasiz, xatolik yuz berdi: {e}")
    return True


def text_loop(brain: Brain, voice: Voice) -> None:
    print("Yozma rejim. Chiqish uchun 'xayr' deb yozing.\n")
    while True:
        try:
            text = input("👤 Siz: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if text and not handle(brain, voice, text):
            break


def voice_loop(brain: Brain, voice: Voice) -> None:
    print(f"Ovozli rejim. Murojaat uchun '{config.WAKE_WORDS[0].capitalize()}' deb boshlang. "
          "(Ctrl+C — chiqish)\n")
    while True:
        try:
            heard = voice.listen(timeout=None)
            if not heard:
                continue
            command = strip_wake_word(heard)
            if command is None:
                continue
            if not command:
                voice.speak("Ha, janob?")
                command = voice.listen()
                if not command:
                    continue
            if not handle(brain, voice, command):
                break
        except KeyboardInterrupt:
            print()
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Muza — shaxsiy AI yordamchi")
    parser.add_argument("--text", action="store_true", help="mikrofonsiz, yozma rejim")
    args = parser.parse_args()

    try:
        brain = Brain()
    except RuntimeError as e:
        print(e)
        sys.exit(1)
    voice = Voice()
    voice.speak(greeting())

    if args.text or not voice.mic_available:
        if not args.text:
            print("(Mikrofon topilmadi — yozma rejimga o'tildi.)")
        text_loop(brain, voice)
    else:
        voice_loop(brain, voice)


if __name__ == "__main__":
    main()
