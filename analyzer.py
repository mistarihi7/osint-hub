import os
import json
import re
from groq import Groq

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# ======================================================
# Prompt تحليل جيوسياسي متقدم
# ======================================================
SYSTEM_PROMPT = """You are a senior geopolitical intelligence analyst with 20 years of experience in strategic studies, military affairs, and international relations. You have deep knowledge of:
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


def analyze_article_intelligence(title: str, full_text: str) -> dict:
    # اقتصاص النص لتوفير الـ tokens مع الحفاظ على الجوهر
    truncated_text = full_text[:3000] if len(full_text) > 3000 else full_text

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # أقوى نموذج متاح على Groq
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Article Title: {title}\n\nFull Text:\n{truncated_text}"}
            ],
            temperature=0.15,
            max_tokens=700
        )

        raw = response.choices[0].message.content.strip()

        # تنظيف أي كود markdown
        if "```" in raw:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            raw = match.group(0) if match else raw

        return json.loads(raw)

    except json.JSONDecodeError:
        # fallback آمن
        return {
            "category": "Diplomacy",
            "threat_level": "Medium",
            "countries_involved": ["Unknown"],
            "hidden_actors": [],
            "arabic_summary": f"خبر بعنوان: {title}",
            "real_driver": "يجري التحليل...",
            "geopolitical_impact": "يجري التقييم...",
            "strategic_forecast": "لا توقعات متاحة حالياً.",
            "intel_signal": "WATCH"
        }
    except Exception as e:
        return {
            "category": "Error",
            "threat_level": "Low",
            "countries_involved": [],
            "hidden_actors": [],
            "arabic_summary": f"فشل التحليل: {str(e)}",
            "real_driver": "-",
            "geopolitical_impact": "-",
            "strategic_forecast": "-",
            "intel_signal": "STABLE"
        }
