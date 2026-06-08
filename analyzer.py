import os
import json
import re
from groq import Groq

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def analyze_batch(chunk_articles: list) -> list:
    system_prompt = (
        "أنت محلل استخبارات عسكري. مهمتك قراءة الأخبار اليومية الحقيقية وصياغتها كتقارير أمنية تكتيكية باللغة العربية الفصحى.\n\n"
        "التعليمات الصارمة (اقرأها بعناية والتزم بها):\n"
        "1. ممنوع التكرار: إياك واستخدام نفس الديباجة أو الجمل المحفوظة في كل خبر. يجب أن يكون التحليل فريداً ومبنياً على ما ورد في النص فقط.\n"
        "2. الدقة: استخرج التفاصيل الحقيقية (أسماء دول، أسلحة، مواقع، شخصيات) من النص الأصلي. لا تخترع تحركات غير موجودة.\n"
        "3. الصياغة: لغة عربية فصحى قوية، بدون أي كلمات إنجليزية.\n\n"
        "يجب إخراج الناتج كمصفوفة JSON مطابقة للمفاتيح التالية:\n"
        "[\n  {\n"
        '    "arabic_title": "ترجمة أو صياغة العنوان بشكل دقيق وواقعي"،\n'
        '    "category": "عسكري أو سياسي أو أمني أو اقتصادي"،\n'
        '    "threat_level": "حرج أو عالي أو متوسط أو منخفض",\n'
        '    "intel_signal": "أزمة أو تصعيد أو مراقبة أو مستقر أو فرصة",\n'
        '    "countries_involved": ["الدول المذكورة فعلياً في الخبر"],\n'
        '    "arabic_summary": "ملخص تكتيكي حقيقي ومفصل لما حدث في الخبر المرفق. اذكر الأسماء والأماكن، وتجنب العبارات العامة.",\n'
        '    "real_driver": "تحليل واقعي للدافع الفعلي خلف هذا الحدث تحديداً.",\n'
        '    "strategic_forecast": "توقع استراتيجي واقعي مبني على معطيات هذا الخبر خلال الأسابيع القادمة.",\n'
        '    "geopolitical_impact": "الأثر الإقليمي أو الدولي الفعلي لهذا الحدث.",\n'
        '    "hidden_actors": ["جهات مستفيدة أو متورطة"]\n'
        "  }\n]\n"
    )

    user_content = "حلل هذه الأخبار الحقيقية فوراً، واجعل كل تحليل فريداً ومختلفاً عن الآخر:\n\n"
    for idx, art in enumerate(chunk_articles):
        user_content += f"--- الخبر {idx} ---\nالمصدر: {art['source_name']}\nالمضمون: {art['full_text']}\n\n"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3, # تم الرفع قليلاً ليصبح التحليل متجدداً وغير مكرر
            max_tokens=3200
        )
        
        raw_result = response.choices[0].message.content.strip()
        if "```" in raw_result:
            match = re.search(r'\[.*\]', raw_result, re.DOTALL)
            if match: raw_result = match.group(0)
                
        raw_result = raw_result.replace('\n', ' ').replace('\r', '')
        return json.loads(raw_result)
    except Exception as e:
        # نظام أمان يقرأ من العنوان الفعلي بدلاً من تثبيت نفس الجمل
        return [{
            "arabic_title": f"متابعة: {art['title'][:50]}...",
            "category": "أمني", "threat_level": "متوسط", "intel_signal": "مراقبة",
            "countries_involved": ["غير محدد"],
            "arabic_summary": f"الخبر يتناول: {art['title']}. يجري متابعة التفاصيل الميدانية الخاصة بهذا التطور.",
            "real_driver": "دوافع سياسية أو أمنية قيد التحليل حالياً.",
            "strategic_forecast": "قيد المتابعة والتحديث للأسابيع القادمة.",
            "geopolitical_impact": "تأثير محتمل على أمن المنطقة المستهدفة.",
            "hidden_actors": ["غير معلن"]
        } for art in chunk_articles]

def analyze_all_articles_at_once(articles: list) -> list:
    if not articles: return []
    final_reports = []
    chunk_size = 2
    for i in range(0, len(articles), chunk_size):
        chunk = articles[i:i+chunk_size]
        analysis_results = analyze_batch(chunk)
        for idx, art in enumerate(chunk):
            if isinstance(analysis_results, list) and idx < len(analysis_results):
                final_reports.append({**art, **analysis_results[idx]})
            else:
                final_reports.append({**art, "arabic_title": "خطأ معالجة", "category": "أمني", "threat_level": "متوسط", "intel_signal": "مراقبة", "countries_involved": [], "arabic_summary": "تعذر المعالجة.", "real_driver": "-", "strategic_forecast": "-", "geopolitical_impact": "-", "hidden_actors": []})
    return final_reports
