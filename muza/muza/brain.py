"""Muzaning miyasi — Claude API bilan suhbat va vositalardan foydalanish."""
import anthropic

from . import config
from .skills import TOOLS, run_tool, _load_memory

MAX_HISTORY = 30  # xabarlar soni


class Brain:
    def __init__(self):
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY topilmadi. .env faylini to'ldiring.")
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.history: list[dict] = []

    def _system(self) -> str:
        mem = _load_memory()
        if mem:
            facts = "; ".join(f"{k}: {v}" for k, v in mem.items())
            return config.SYSTEM_PROMPT + f"\nFoydalanuvchi haqida eslab qolganlaring: {facts}"
        return config.SYSTEM_PROMPT

    def _trim(self) -> None:
        if len(self.history) <= MAX_HISTORY:
            return
        self.history = self.history[-MAX_HISTORY:]
        # Tarix foydalanuvchining oddiy matnli xabaridan boshlanishi kerak
        while self.history and not (
            self.history[0]["role"] == "user" and isinstance(self.history[0]["content"], str)
        ):
            self.history.pop(0)

    def ask(self, text: str) -> str:
        self.history.append({"role": "user", "content": text})
        for _ in range(6):  # vositalarni ketma-ket chaqirish chegarasi
            resp = self.client.messages.create(
                model=config.MODEL,
                max_tokens=1024,
                system=self._system(),
                tools=TOOLS,
                messages=self.history,
            )
            self.history.append({"role": "assistant", "content": resp.content})

            if resp.stop_reason != "tool_use":
                answer = "".join(b.text for b in resp.content if b.type == "text").strip()
                self._trim()
                return answer or "Bajarildi, janob."

            results = []
            for block in resp.content:
                if block.type == "tool_use":
                    print(f"   ⚙️  {block.name}({block.input})")
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": run_tool(block.name, block.input),
                    })
            self.history.append({"role": "user", "content": results})

        return "Kechirasiz, bu vazifa juda murakkab bo'lib qoldi."

    def reset(self) -> None:
        self.history.clear()
