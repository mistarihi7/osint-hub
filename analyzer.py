import os
import json
import re
import time
import requests
from groq import Groq

# ── API Keys ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# ── Telegram Config ───────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID   = "YOUR_TELEGRAM_CHAT_ID"

client = Groq(api_key=GROQ_API_KEY)

# ══════════════════════════════════════════════════════════════════════════════
# المرحلة 1 — فلترة سريعة بنموذج صغير (العنوان فقط)
# ══════════════════════════════════════════════════════════════════════════════
FILTER_PROMPT = """You are a geopolitical news triage agent.
Given a news headline, score its geopolitical importance from 1 to 10.
Rules:
- 8-10: Major crisis, war, sanctions, nuclear, coup, terror, major elections, significant military move
- 5-7:  Diplomacy, trade disputes, protests, political tensions, energy deals
- 1-4:  Sports, entertainment, minor local news, weather, celebrity

Output ONLY a raw JSON object. No extra text:
{"score": 7, "reason": "one short sentence in English"}"""


def triage_article(title: str) -> int:
    """
    المرحلة 1: يقيّم أهمية الخبر من 1-10 بناءً على العنوان فقط.
    يرجع النقطة — الأخبار أقل من 6 تُحذف.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # نموذج صغير وسريع
            messages=[
                {"role": "system", "content": FILTER_PROMPT},
                {"role": "user",   "content": f"Headline: {title}"}
            ],
            temperature=0.1,
            max_tokens=80
        )
        raw = response.choices[0].message.content.strip()
        if "```" in raw:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            raw = match.group(0) if match else raw
        data = json.loads(raw)
        return int(data.get("score", 5))
    except Exception:
        return 5  # في حال الفشل نعطيه نقطة وسطى


# ══════════════════════════════════════════════════════════════════════════════
# المرحلة 2 — تحليل عميق بنموذج كبير (النص الكامل)
# ══════════════════════════════════════════════════════════════════════════════
DEEP_ANALYSIS_PROMPT = """You are a senior geopolitical intelligence analyst with 20 years of experience in strategic studies, military affairs, and international relations. You have deep knowledge of:
- The hidden power games behind official statements (realpolitik)
- Intelligence community tradecraft and signaling
- Military strategy and alliance dynamics
- Economic warfare, sanctions, and resource control
- Proxy conflicts and non-state actors
- Historical precedents and cyclical patterns in geopolitics

Your task: Analyze the provided news article with clinical precision and strategic depth. Go BEYOND the surface narrative. Identify who REALLY benefits, what is NOT being said, and what comes next.

Output ONLY raw valid JSON with EXACTLY this structure. No markdown, no preamble, no extra text:

{
  "category": "one of: Military / Diplomacy / Intelligence / Economic Warfare / Energy & Resources / Proxy Conflict / Cyber & Tech War / Humanitarian Crisis / Elections & Democracy",
  "threat_level": "one of: Low / Medium / High / Critical",
  "countries_involved": ["primary actors"],
  "hidden_actors": ["non-obvious players: intelligence agencies, corporations, lobbies, militias"],
  "arabic_summary": "ملخص تكتيكي دقيق في جملتين يصف الحدث والسياق الحقيقي بدون علامات اقتباس مزدوجة",
  "real_driver": "الدافع الحقيقي وراء الحدث وليس الرواية الرسمية - جملة واحدة بالعربية",
  "geopolitical_impact": "الأثر الجيوسياسي المستقبلي على المدى القريب والبعيد - جملة بالعربية",
  "strategic_forecast": "توقع استراتيجي: ماذا سيحدث بعد 30-90 يوماً بناءً على هذا الحدث - جملة بالعربية",
  "intel_signal": "one of: WATCH / ESCALATING / STABLE / CRISIS / OPPORTUNITY"
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
        f"{'─' * 30}\n"
        f"📰 *{title}*\n\n"
        f"📡 المصدر: `{source_name}`\n"
        f"⚠️ الخطورة: `{threat_level}` | {signal_map.get(intel_signal,'🔵')} الإشارة: `{intel_signal}`\n\n"
        f"📝 *الملخص التكتيكي:*\n{summary}"
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
    """
    المرحلة 1: تقييم سريع للعنوان — إذا النقطة أقل من 6 يُحذف الخبر.
    المرحلة 2: تحليل عميق للأخبار المهمة فقط.
    """

    # ── المرحلة 1: الفلترة السريعة ───────────────────────────────────────────
    score = triage_article(title)
    time.sleep(0.5)  # delay خفيف بين المرحلتين

    if score < 6:
        # خبر غير مهم — نرجع بيانات فارغة بدون تحليل عميق
        return {
            "category": "—",
            "threat_level": "Low",
            "countries_involved": [],
            "hidden_actors": [],
            "arabic_summary": f"تم تصفية هذا الخبر (أهمية جيوسياسية منخفضة — النقطة: {score}/10)",
            "real_driver": "—",
            "geopolitical_impact": "—",
            "strategic_forecast": "—",
            "intel_signal": "STABLE",
            "triage_score": score,
            "filtered": True
        }

    # ── المرحلة 2: التحليل العميق ────────────────────────────────────────────
    truncated_text = full_text[:3000] if len(full_text) > 3000 else full_text

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": DEEP_ANALYSIS_PROMPT},
                {"role": "user",   "content": f"Article Title: {title}\n\nFull Text:\n{truncated_text}"}
            ],
            temperature=0.15,
            max_tokens=700
        )

        raw = response.choices[0].message.content.strip()
        if "```" in raw:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            raw = match.group(0) if match else raw

        result = json.loads(raw)
        result["triage_score"] = score
        result["filtered"] = False

        # ── Telegram Alert ────────────────────────────────────────────────────
        threat  = result.get("threat_level", "Low")
        signal  = result.get("intel_signal", "WATCH")
        summary = result.get("arabic_summary", "")
        if threat in ("Critical", "High") or signal == "CRISIS":
            send_telegram_alert(title, summary, threat, signal, source_name)

        return result

    except json.JSONDecodeError:
        return {
            "category": "Diplomacy",
            "threat_level": "Medium",
            "countries_involved": ["Unknown"],
            "hidden_actors": [],
            "arabic_summary": f"خبر بعنوان: {title}",
            "real_driver": "يجري التحليل...",
            "geopolitical_impact": "يجري التقييم...",
            "strategic_forecast": "لا توقعات متاحة حالياً.",
            "intel_signal": "WATCH",
            "triage_score": score,
            "filtered": False
        }
    except Exception as e:
        return {
            "category": "Error",
            "threat_level": "Low",
            "countries_involved": [],
            "hidden_actors": [],
            "arabic_summary": f"فشل التحليل: {str(e)}",
            "real_driver": "—",
            "geopolitical_impact": "—",
            "strategic_forecast": "—",
            "intel_signal": "STABLE",
            "triage_score": score,
            "filtered": False
        }
