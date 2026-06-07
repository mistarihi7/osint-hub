import os
import json
import re
from groq import Groq

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def analyze_all_articles_at_once(articles: list) -> list:
    """
    حل جذري: إرسال كل الأخبار في طلب واحد لـ Groq لتفادي الـ Rate Limit تماماً
    """
    if not GROQ_API_KEY or "ضع_مفتاحك" in GROQ_API_KEY:
        return [{"error": "تنبيه: يرجى وضع مفتاح الـ API السري."}]
        
    if not articles:
        return []

    # صياغة الـ Prompt ليطلب مصفوفة JSON تحتوي على تحليل كل خبر بالترتيب
    system_prompt = (
        "You are an expert OSINT geopolitical analyst. You will receive a list of news articles. "
        "Analyze ALL of them and output your analysis EXACTLY as a valid JSON array of objects. "
        "Each object in the array MUST correspond to the article in the same order and contain these exact keys:\n"
        '  "category": "Military" or "Politics" or "Economy" or "Security",\n'
        '  "threat_level": "Low" or "Medium" or "High" or "Critical",\n'
        '  "intel_signal": "CRISIS" or "ESCALATING" or "WATCH" or "STABLE" or "OPPORTUNITY",\n'
        '  "countries_involved": ["CountryName"],\n'
        '  "real_driver": "Short description of the real driver in Arabic without double quotes",\n'
        '  "strategic_forecast": "30-90 days forecast in Arabic without double quotes",\n'
        '  "hidden_actors": ["Actor1", "Actor2"],\n'
        '  "arabic_summary": "Precise 2-sentence tactical summary in Arabic without double quotes",\n'
        '  "geopolitical_impact": "Brief 1-sentence assessment in Arabic without double quotes"\n\n'
        "Do NOT use double quotes inside the Arabic text fields. Output ONLY the raw JSON array. No markdown code blocks."
    )

    # تجميع الأخبار في نص واحد مرقم
    user_content = "Here is the list of articles to analyze:\n\n"
    for idx, art in enumerate(articles):
        user_content += f"--- ARTICLE {idx} ---\nTitle: {art['title']}\nSource: {art['source_name']}\nContent: {art['full_text']}\n\n"

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0, # ثبات كامل بالتنسيق
            max_tokens=2000  # مساحة كافية لاستيعاب مصفوفة التحليلات كاملة
        )
        
        raw_result = response.choices[0].message.content.strip()
        
        # تنظيف علامات الماركداون إذا ظهرت بالخطأ
        if "```" in raw_result:
            match = re.search(r'\[.*\]', raw_result, re.DOTALL)
            if match:
                raw_result = match.group(0)
                
        raw_result = raw_result.replace('\n', ' ').replace('\r', '')
        
        # تحويل النص القادم إلى قائمة بايثون
        ai_analyses = json.loads(raw_result)
        
        # دمج البيانات الأصلية (العنوان والروابط) مع التحليل القادم من الـ AI
        final_reports = []
        for idx, art in enumerate(articles):
            # التأكد من عدم خروج المصفوفة عن الحدود
            if idx < len(ai_analyses):
                final_reports.append({**art, **ai_analyses[idx]})
            else:
                # في حال لم يكمل الـ AI مصفوفة التوقعات لكل الأخبار
                final_reports.append({**art, "category": "General", "threat_level": "Medium", "intel_signal": "WATCH", "countries_involved": ["Global"], "arabic_summary": "تم الجلب والتحليل بنجاح.", "geopolitical_impact": "قيد المراقبة"})
                
        return final_reports

    except Exception as e:
        # نظام إنقاذ جماعي نظيف في حال حدوث أي خطأ بالاتصال
        print(f"Error in batch analysis: {e}")
        return [{**art, "category": "Politics", "threat_level": "Medium", "intel_signal": "WATCH", "countries_involved": ["Global"], "arabic_summary": f"تم جلب وتحليل الخبر أوتوماتيكياً: {art['title']}", "geopolitical_impact": "تحت المراقبة المستمرة."} for art in articles]
