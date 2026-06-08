import os
import json
import re
import time
import requests
from groq import Groq

# ── API Keys ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── Telegram Config ───────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID   = "YOUR_TELEGRAM_CHAT_ID"

client = Groq(api_key=GROQ_API_KEY)

# ══════════════════════════════════════════════════════════════════════════════
# المرحلة 1 — فلترة سريعة (نموذج صغير، العنوان فقط)
# ══════════════════════════════════════════════════════════════════════════════
TRIAGE_PROMPT = """You are a geopolitical news triage agent for a global intelligence platform.
Score this headline's relevance from 1 to 10. Be GENEROUS — when in doubt, score higher.

- 6-10: Anything related to: politics, diplomacy, military, economy, trade, energy, elections,
        international relations, sanctions, conflicts, terrorism, climate policy, tech policy,
        government decisions, central banks, treaties, protests, security, intelligence
- 1-5:  ONLY pure entertainment, celebrity gossip, sports scores, cooking, lifestyle

Most news from Reuters, BBC, Al Jazeera, Guardian = score 6 or above by default.

Output ONLY raw JSON. No extra text:
{"score": 7}"""


def triage_article(title: str) -> int:
    """المرحلة 1: يقيّم أهمية العنوان ويرجع نقطة 1-10."""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": TRIAGE_PROMPT},
                {"role": "user",   "content": f"Headline: {title}"}
            ],
            temperature=0.1,
            max_tokens=20
        )
        raw = response.choices[0].message.content.strip()
        raw = re.search(r'\{.*\}', raw, re.DOTALL)
        raw = raw.group(0) if raw else '{"score":5}'
        return int(json.loads(raw).get("score", 5))
    except Exception:
        return 5


# ══════════════════════════════════════════════════════════════════════════════
# المرحلة 2 — تحليل عميق (نموذج كبير، النص الكامل)
# ══════════════════════════════════════════════════════════════════════════════
DEEP_PROMPT = """You are a senior geopolitical intelligence analyst with 20 years of experience. You have deep knowledge of realpolitik, intelligence tradecraft, military strategy, economic warfare, proxy conflicts, and historical patterns.

Analyze the article with clinical precision. Go BEYOND the surface narrative. Identify who REALLY benefits, what is NOT being said, and what comes next.

Output ONLY raw valid JSON. No markdown, no preamble:

{
  "category": "Military / Diplomacy / Intelligence / Economic Warfare / Energy & Resources / Proxy Conflict / Cyber & Tech War / Humanitarian Crisis / Elections & Democracy",
  "threat_level": "Low / Medium / High / Critical",
  "countries_involved": ["list of countries"],
  "hidden_actors": ["intelligence agencies, corporations, lobbies, militias"],
  "arabic_summary": "ملخص تكتيكي دقيق في جملتين بدون علامات اقتباس مزدوجة",
  "real_driver": "الدافع الحقيقي وراء الحدث - جملة واحدة بالعربية",
  "geopolitical_impact": "الأثر الجيوسياسي المستقبلي - جملة بالعربية",
  "strategic_forecast": "توقع استراتيجي 30-90 يوماً - جملة بالعربية",
  "intel_signal": "WATCH / ESCALATING / STABLE / CRISIS / OPPORTUNITY"
}"""


# ══════════════════════════════════════════════════════════════════════════════
# Telegram Alert
# ══════════════════════════════════════════════════════════════════════════════
def send_telegram_alert(title: str, summary: str, threat_level: str,
                        intel_signal: str, source_name: str) -> None:
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        return
    emoji_map  = {"Critical": "🚨🚨", "High": "⚠️", "Medium": "🔵", "Low": "🟢"}
    signal_map = {"CRISIS": "🔴", "ESCALATING": "🟠", "WATCH": "🔵", "STABLE": "🟢", "OPPORTUNITY": "🟣"}
    message = (
        f"{emoji_map.get(threat_level,'⚠️')} *OSINT ALERT — {threat_level.upper()}*\n"
        f"{'─'*30}\n"
        f"📰 *{title}*\n\n"
        f"📡 المصدر: `{source_name}`\n"
        f"⚠️ الخطورة: `{threat_level}` | {signal_map.get(intel_signal,'🔵')} الإشارة: `{intel_signal}`\n\n"
        f"📝 *الملخص:*\n{summary}"
    )
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=5
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# الدالة الرئيسية — ثنائية المرحلة
# ══════════════════════════════════════════════════════════════════════════════
def analyze_article_intelligence(title: str, full_text: str,
                                  source_name: str = "") -> dict:
    # ── المرحلة 1: الفلترة السريعة ───────────────────────────────────────────
    score = triage_article(title)
    time.sleep(0.4)

    if score < 4:
        return {
            "category": "—", "threat_level": "Low",
            "countries_involved": [], "hidden_actors": [],
            "arabic_summary": f"تم تصفية هذا الخبر — أهمية جيوسياسية منخفضة ({score}/10)",
            "real_driver": "—", "geopolitical_impact": "—",
            "strategic_forecast": "—", "intel_signal": "STABLE",
            "triage_score": score, "filtered": True
        }

    # ── المرحلة 2: التحليل العميق ────────────────────────────────────────────
    truncated = full_text[:3000] if len(full_text) > 3000 else full_text

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": DEEP_PROMPT},
                {"role": "user",   "content": f"Title: {title}\n\nText:\n{truncated}"}
            ],
            temperature=0.15,
            max_tokens=700
        )
        raw = response.choices[0].message.content.strip()
        if "```" in raw:
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            raw = m.group(0) if m else raw

        result = json.loads(raw)
        result["triage_score"] = score
        result["filtered"]     = False

        threat  = result.get("threat_level", "Low")
        signal  = result.get("intel_signal", "WATCH")
        if threat in ("Critical", "High") or signal == "CRISIS":
            send_telegram_alert(title, result.get("arabic_summary",""), threat, signal, source_name)

        return result

    except json.JSONDecodeError:
        return {
            "category": "Diplomacy", "threat_level": "Medium",
            "countries_involved": [], "hidden_actors": [],
            "arabic_summary": f"تعذّر استخراج تحليل منظّم للخبر: {title[:80]}",
            "real_driver": "يجري التحليل...", "geopolitical_impact": "يجري التقييم...",
            "strategic_forecast": "—", "intel_signal": "WATCH",
            "triage_score": score, "filtered": False
        }
    except Exception as e:
        return {
            "category": "Error", "threat_level": "Low",
            "countries_involved": [], "hidden_actors": [],
            "arabic_summary": f"خطأ في التحليل: {str(e)[:100]}",
            "real_driver": "—", "geopolitical_impact": "—",
            "strategic_forecast": "—", "intel_signal": "STABLE",
            "triage_score": score, "filtered": False
        }
