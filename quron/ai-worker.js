// Qur'on Viktorinasi — "Savol bering" uchun ChatGPT (OpenAI) ko'prigi
// Cloudflare Workers'ga joylanadi. OpenAI kaliti shu yerda yashirin saqlanadi,
// saytning o'zida (brauzerda) hech qachon ko'rinmaydi.
//
// Sozlamalar (Cloudflare → Worker → Settings → Variables and Secrets):
//   OPENAI_API_KEY  (Secret)  — OpenAI kalitingiz, majburiy
//   MODEL           (ixtiyoriy) — standart: gpt-4o-mini
//   ALLOWED_ORIGIN  (ixtiyoriy) — standart: https://muzaffarkarshiev.github.io

const LANGS = { uz: "Uzbek (Latin script)", ru: "Russian", tr: "Turkish", ar: "Arabic" };

function systemPrompt(lang) {
  return `You are a careful, respectful Islamic knowledge assistant on a Qur'an learning website.
Always answer in ${LANGS[lang] || LANGS.uz}, whatever language the question is in.
Rules:
- Base answers on the Qur'an and authentic (sahih/hasan) hadith. Quote the meaning, and give the reference: surah name and ayah number, or hadith collection and number.
- Only cite a reference you are sure of. Never invent ayahs, hadith, numbers or scholars. If unsure, say so plainly.
- The site's visitors are mostly from Uzbekistan, Turkey and Russia, where the Hanafi madhhab is common: give the Hanafi view on fiqh questions and briefly note when other madhhabs differ.
- For personal rulings (divorce, inheritance shares, debts, medical, business contracts) give the general principle, then advise asking a local imam or the official muftiate (muslim.uz, Diyanet, DUM RF).
- Be kind and encouraging. Never insult other faiths or groups. Avoid politics.
- If the question is not about Islam, the Qur'an, hadith or Muslim life, answer in one short sentence that you only help with these topics.
- Keep the answer clear and short: at most about 200 words. Use **bold** for references.`;
}

export default {
  async fetch(request, env) {
    const allow = env.ALLOWED_ORIGIN || "https://muzaffarkarshiev.github.io";
    const origin = request.headers.get("Origin") || "";
    const cors = {
      "Access-Control-Allow-Origin": allow,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Vary": "Origin",
    };
    const json = (obj, status = 200) =>
      new Response(JSON.stringify(obj), { status, headers: { ...cors, "Content-Type": "application/json; charset=utf-8" } });

    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method !== "POST") return json({ error: "POST only" }, 405);
    if (origin !== allow) return json({ error: "forbidden" }, 403);
    if (!env.OPENAI_API_KEY) return json({ error: "OPENAI_API_KEY is not set" }, 500);

    let body;
    try { body = await request.json(); } catch { return json({ error: "bad json" }, 400); }
    const q = String(body.q || "").trim().slice(0, 600);
    const lang = LANGS[body.lang] ? body.lang : "uz";
    if (q.length < 2) return json({ error: "empty question" }, 400);

    const r = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: { "Authorization": `Bearer ${env.OPENAI_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        model: env.MODEL || "gpt-4o-mini",
        temperature: 0.3,
        max_tokens: 700,
        messages: [
          { role: "system", content: systemPrompt(lang) },
          { role: "user", content: q },
        ],
      }),
    });
    if (!r.ok) return json({ error: "openai " + r.status }, 502);
    const data = await r.json();
    const answer = data.choices?.[0]?.message?.content?.trim();
    return answer ? json({ answer }) : json({ error: "empty answer" }, 502);
  },
};
