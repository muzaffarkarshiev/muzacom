# 🤖 Muza — shaxsiy AI yordamchi

Muza — Temir odamdagi **J.A.R.V.I.S.** ga o'xshash, o'zbek tilida gapiradigan va eshitadigan shaxsiy sun'iy intellekt yordamchisi. Miyasi — Claude (Anthropic).

## Imkoniyatlari

- 🎤 **Ovozli boshqaruv** — "Muza, ..." deb murojaat qilasiz (o'zbek tilida nutqni tanish)
- 🗣️ **O'zbekcha ovoz** — tabiiy ovoz bilan javob beradi (Madina yoki Sardor)
- 🧠 **Aqlli suhbat** — har qanday savolga javob, suhbat kontekstini eslab qoladi
- 🕐 Vaqt va sana
- 🌤️ Ob-havo (istalgan shahar)
- 🔎 Internetdan qidirish, saytlarni ochish
- ▶️ YouTube'da musiqa/video qo'yish
- 💻 Dasturlarni ishga tushirish (Chrome, Telegram, Notepad...)
- 📊 Kompyuter holati (CPU, RAM, disk, batareya)
- 💾 Doimiy xotira — "Muza, eslab qol: ..." 
- ⌨️ Yozma rejim — mikrofonsiz ham ishlaydi

## O'rnatish

```bash
git clone https://github.com/muzaffarkarshiev/muzacom.git
cd muzacom/muza
python -m venv venv
# Windows:  venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

> **PyAudio** o'rnatishda muammo bo'lsa:
> - Windows: `pip install pipwin && pipwin install pyaudio`
> - macOS: `brew install portaudio && pip install pyaudio`
> - Linux: `sudo apt install portaudio19-dev && pip install pyaudio`

Keyin `.env.example` faylini `.env` deb nusxalang va API kalitingizni yozing
(kalitni https://console.anthropic.com dan olasiz):

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Ishga tushirish

```bash
python -m muza          # ovozli rejim
python -m muza --text   # yozma rejim
```

## Misol buyruqlar

- "Muza, soat necha?"
- "Muza, Samarqandda ob-havo qanday?"
- "Muza, YouTube'da Sherali Jo'rayev qo'shiqlarini qo'y"
- "Muza, Telegramni och"
- "Muza, kompyuter holati qanday?"
- "Muza, eslab qol: tug'ilgan kunim 5-may"
- "Muza, xayr" — chiqish

## Tuzilishi

```
muza/
├── __main__.py   # asosiy sikl (ovozli / yozma)
├── brain.py      # Claude bilan muloqot va vositalar
├── skills.py     # ko'nikmalar: vaqt, ob-havo, qidiruv, dasturlar...
├── voice.py      # eshitish va gapirish
└── config.py     # sozlamalar
```

Yangi ko'nikma qo'shish uchun `skills.py` ga funksiya yozing va uni `TOOLS` hamda `HANDLERS` ro'yxatlariga qo'shing — Muza uni o'zi ishlata boshlaydi.

---
Muallif: Muzaffar
