"""Muzaning ko'nikmalari — Claude chaqira oladigan vositalar (tools)."""
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import urllib.parse
import webbrowser

import requests

from . import config

try:
    import psutil
except ImportError:
    psutil = None


# ---------- Xotira ----------
def _load_memory() -> dict:
    try:
        with open(config.MEMORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_memory(data: dict) -> None:
    with open(config.MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- Vositalar ----------
def get_time(**_) -> str:
    now = dt.datetime.now()
    oylar = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul",
             "avgust", "sentabr", "oktabr", "noyabr", "dekabr"]
    kunlar = ["dushanba", "seshanba", "chorshanba", "payshanba", "juma", "shanba", "yakshanba"]
    return f"{now:%H:%M}, {now.day}-{oylar[now.month - 1]} {now.year}-yil, {kunlar[now.weekday()]}"


def get_weather(city: str = "", **_) -> str:
    city = city or config.DEFAULT_CITY
    try:
        r = requests.get(f"https://wttr.in/{urllib.parse.quote(city)}?format=j1&lang=uz", timeout=10)
        r.raise_for_status()
        cur = r.json()["current_condition"][0]
        desc = (cur.get("lang_uz") or cur.get("weatherDesc") or [{"value": ""}])[0]["value"]
        return (f"{city}: {cur['temp_C']}°C, his qilinishi {cur['FeelsLikeC']}°C, {desc}, "
                f"namlik {cur['humidity']}%, shamol {cur['windspeedKmph']} km/soat")
    except Exception as e:
        return f"Ob-havoni olib bo'lmadi: {e}"


def web_search(query: str, **_) -> str:
    """DuckDuckGo orqali qisqa javob qidiradi."""
    try:
        r = requests.get("https://api.duckduckgo.com/",
                         params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                         timeout=10)
        data = r.json()
        parts = []
        if data.get("AbstractText"):
            parts.append(data["AbstractText"])
        for t in data.get("RelatedTopics", [])[:5]:
            if isinstance(t, dict) and t.get("Text"):
                parts.append(t["Text"])
        return "\n".join(parts) if parts else "Aniq natija topilmadi. Brauzerda qidirishni taklif qil."
    except Exception as e:
        return f"Qidiruvda xato: {e}"


def open_website(url: str = "", query: str = "", **_) -> str:
    if not url and query:
        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    if url and not url.startswith("http"):
        url = "https://" + url
    if not url:
        return "Manzil berilmadi."
    webbrowser.open(url)
    return f"Ochildi: {url}"


def play_youtube(query: str, **_) -> str:
    webbrowser.open("https://www.youtube.com/results?search_query=" + urllib.parse.quote(query))
    return f"YouTube'da qidirildi: {query}"


def open_app(name: str, **_) -> str:
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(name)  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", name])
        else:
            exe = shutil.which(name) or shutil.which(name.lower())
            if not exe:
                return f"'{name}' dasturi topilmadi."
            subprocess.Popen([exe])
        return f"'{name}' ishga tushirildi."
    except Exception as e:
        return f"'{name}' ni ochib bo'lmadi: {e}"


def system_status(**_) -> str:
    if not psutil:
        return f"Tizim: {platform.system()} {platform.release()}"
    bat = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    s = (f"Protsessor: {psutil.cpu_percent(interval=0.5)}%, "
         f"xotira (RAM): {psutil.virtual_memory().percent}%, "
         f"disk: {psutil.disk_usage(os.path.abspath(os.sep)).percent}%")
    if bat:
        s += f", batareya: {bat.percent:.0f}%{' (quvvatlanmoqda)' if bat.power_plugged else ''}"
    return s


def remember(key: str, value: str, **_) -> str:
    mem = _load_memory()
    mem[key] = value
    _save_memory(mem)
    return f"Eslab qoldim: {key} = {value}"


def recall(key: str = "", **_) -> str:
    mem = _load_memory()
    if not mem:
        return "Xotira bo'sh."
    if key:
        return mem.get(key, f"'{key}' haqida hech narsa eslab qolmaganman.")
    return json.dumps(mem, ensure_ascii=False)


# ---------- Claude uchun ta'riflar ----------
TOOLS = [
    {"name": "get_time", "description": "Hozirgi vaqt va sanani qaytaradi.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_weather", "description": "Shahar bo'yicha hozirgi ob-havo.",
     "input_schema": {"type": "object", "properties": {"city": {"type": "string", "description": "Shahar nomi (inglizcha yaxshiroq)"}}}},
    {"name": "web_search", "description": "Internetdan qisqa ma'lumot qidiradi.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "open_website", "description": "Brauzerda sayt ochadi yoki Google'da qidiradi.",
     "input_schema": {"type": "object", "properties": {"url": {"type": "string"}, "query": {"type": "string"}}}},
    {"name": "play_youtube", "description": "YouTube'da video/musiqa qidirib ochadi.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "open_app", "description": "Kompyuterda dastur ishga tushiradi (masalan: notepad, calc, chrome, telegram).",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "system_status", "description": "Protsessor, xotira, disk va batareya holati.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "remember", "description": "Foydalanuvchi so'ragan ma'lumotni doimiy xotiraga yozadi.",
     "input_schema": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]}},
    {"name": "recall", "description": "Xotiradan ma'lumot o'qiydi. key bo'sh bo'lsa hammasini qaytaradi.",
     "input_schema": {"type": "object", "properties": {"key": {"type": "string"}}}},
]

HANDLERS = {
    "get_time": get_time,
    "get_weather": get_weather,
    "web_search": web_search,
    "open_website": open_website,
    "play_youtube": play_youtube,
    "open_app": open_app,
    "system_status": system_status,
    "remember": remember,
    "recall": recall,
}


def run_tool(name: str, args: dict) -> str:
    fn = HANDLERS.get(name)
    if not fn:
        return f"Noma'lum vosita: {name}"
    try:
        return str(fn(**(args or {})))
    except Exception as e:
        return f"Xato: {e}"
