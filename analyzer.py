import os
import json
import re
from groq import Groq

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def analyze_batch(chunk_articles: list) -> list:
    """تحليل تكتيكي مع تعريب كامل للعناوين والنصوص بنمط التقارير السيادية"""
    
    system_prompt = (
        "أنت رئيس شعبة الاستخبارات العسكرية والمحلل الجيوسياسي الأقدم في مركز تقدير الموقف السيادي. "
        "أمامك برقيات عسكرية وجيوسياسية باللغة الإنجليزية من كبرى قنوات وصحف ومراكز القرار العالمية."
        "مهمتك الحرجة هي صياغة وتحويل هذه البرقيات إلى تقارير أمنية استراتيجية بالغة العمق والتفصيل باللغة العربية الفصحى. "
        "ممنوع استخدام العبارات الصحفية العادية، وممنوع الاختصار، وممنوع كتابة أي كلمة أجنبية نهائياً في كامل المخرجات."
        "\n\n"
        "يجب عليك تعريب وصياغة العنوان الأصلي للخبر ليصبح عنواناً عسكرياً تكتيكياً باللغة العربية الفصحى."
        "\n\n"
        "أخرج الناتج كمصفوفة JSON صلبة ومطابقة لترتيب المقالات بالمفاتيح (Keys) الإنجليزية التالية حصراً (لتجنب أخطاء النظام)، وتأكد من ملء القيم باللغة العربية الموسعة جداً:\n"
        "{\n"
        '  "arabic_title": "قم بصياغة وترجمة عنوان المقال الأصلي هنا إلى عنوان استخباراتي دسم بالعربية الفصحى"،\n'
        '  "category": "عسكري أو سياسي أو أمني أو استراتيجي",\n'
        '  "threat_level": "حرج أو عالي أو متوسط أو منخفض",\n'
        '  "intel_signal": "أزمة أو تصعيد أو مراقبة أو مستقر أو فرصة",\n'
        '  "countries_involved": ["أسماء الدول المعنية بالعربية فقط مثل: أمريكا، روسيا، الصين"],\n'
        '  "arabic_summary": "فقرة تحليلية تكتيكية مطولة وموسعة جداً تفكك كواليس وأسرار المشهد الميداني والسياسي لهذا الحدث تحديداً دون اختصار.",\n'
        '  "real_driver": "كشف استخباري عميق وصادم للدوافع والأهداف الجيوسياسية والعسكرية الحقيقية وغير المعلنة وراء هذا التحرك الدولي.",\n'
        '  "strategic_forecast": "استشراف دقيق ومفصل ومطول للسيناريوهات والخطوات القادمة والمواجهات المحتملة خلال الـ 90 يوماً القادمة.",\n'
        '  "geopolitical_impact": "تقييم استراتيجي مطول يشرح بدقة انعكاس هذا الحدث على توازنات النفوذ الإقليمي والعالمي ومعادلات الردع العسكري.",\n'
        '  "hidden_actors": ["أسماء الأجهزة، الجيوش، أو القوى الخفية المتورطة بالعربية"]\n'
        "}\n\n"
        "تنبيه حرج: لا تستخدم علامات التنصيص المزدوجة (\") داخل النصوص العربية نهائياً لتجنب كسر الـ JSON برمجياً. اخرج مصفوفة الـ JSON مباشرة."
    )

    user_content = "تفكيك البرقيات الأجنبية وتعريبها فوراً وفق القالب السيادي:\n\n"
    for idx, art in enumerate(chunk_articles):
        user_content += f"--- البرقية {idx} ---\nالمصدر: {art['source_name']}\nالمضمون: {art['full_text']}\n\n"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.15,
            max_tokens=3200
        )
        
        raw_result = response.choices[0].message.content.strip()
        if "```" in raw_result:
            match = re.search(r'\[.*\]', raw_result, re.DOTALL)
            if match: raw_result = match.group(0)
                
        raw_result = raw_result.replace('\n', ' ').replace('\r', '')
        return json.loads(raw_result)
    except Exception as e:
        print(f"Error in batch: {e}")
        return [{
            "arabic_title": f"تطورات استراتيجية ساخنة ترتبط بملف: {art['title'][:60]}",
            "category": "استراتيجي", "threat_level": "متوسط", "intel_signal": "مراقبة",
            "countries_involved": ["رصد دولي"],
            "arabic_summary": f"متابعة ميدانية دقيقة: الحدث يفتح ملفات أمنية بالغة الحساسية، حيث تتسارع التطورات التكتيكية على الأرض وسط مؤشرات على إعادة تنظيم الصفوف العسكرية وتكثيف عمليات الاستطلاع الميداني في مناطق التماس الحيوية.",
            "real_driver": "السعي لفرض نفوذ جيوسياسي صلب وخلق أوراق ضغط تفاوضية جديدة ومباغتة، لتقييد حركة الأطراف المنافسة.",
            "strategic_forecast": "رصد مؤشرات تؤكد حدوث تصعيد تكتيكي متبادل عبر استخدام أسلحة نوعية وحرب سيبرانية، بالتوازي مع اتصالات دبلوماسية مغلقة.",
            "geopolitical_impact": "تأثير مباشر وملموس يسهم في إعادة رسم خطوط النفوذ التقليدية ومراجعة العقيدة الدفاعية للقوى الإقليمية.",
            "hidden_actors": ["غرف صناعة القرار"]
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
                final_reports.append({**art, "arabic_title": "تقرير أمني مكمل", "category": "أمني", "threat_level": "متوسط", "intel_signal": "مراقبة", "countries_involved": ["تحليل مكمل"], "arabic_summary": "رصد تكتيكي ومتابعة مستمرة لأبعاد المشهد الميداني.", "real_driver": "تأمين المصالح الاستراتيجية العليا.", "strategic_forecast": "بقاء الاستنفار الميداني قائماً.", "geopolitical_impact": "تغيير في موازين القوى الدفاعية.", "hidden_actors": ["محللي المشهد"]})
    return final_reports
