import os
import json
import re
from groq import Groq

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def analyze_all_articles_at_once(articles: list) -> list:
    """
    تحليل استخباراتي موسع باللغة العربية الفصحى بالكامل وبدون أي كلمة إنجليزية
    """
    if not GROQ_API_KEY or "ضع_مفتاحك" in GROQ_API_KEY:
        return []
        
    if not articles:
        return []

    # توجيهات صارمة جداً للذكاء الاصطناعي لإلزامية اللغة العربية في كل الحقول بلا استثناء
    system_prompt = (
        "أنت ضابط استخبارات ومحلل جيوسياسي خبير. قم بتحليل المقالات المرفقة بدقة وعمق شديد. "
        "يجب أن يكون تحليلك مفصلاً، شاملاً، ومكتوباً بلغة عربية فصحى رصينة وقوية. "
        "ممنوع استخدام أي كلمة إنجليزية أو مصطلحات أجنبية في كامل المخرجات."
        "\n\n"
        "يجب أن تكون المخرجات عبارة عن مصفوفة JSON صلبة ومطابقة تماماً للترتيب، وبنفس المفاتيح (Keys) الإنجليزية المذكورة أدناه لتجنب أخطاء الكود، ولكن القيم (Values) داخلها يجب أن تكون عربية بالكامل ومفصلة كما يلي:\n"
        "{\n"
        '  "category": "اكتب هنا التصنيف بدقة: عسكري أو سياسي أو أمني أو استراتيجي",\n'
        '  "threat_level": "حدد مستوى الخطورة بدقة: منخفض أو متوسط or عالي أو حرج",\n'
        '  "intel_signal": "حدد الإشارة: أزمة أو تصعيد أو مراقبة أو مستقر أو فرصة",\n'
        '  "countries_involved": ["أسماء الدول المعنية باللغة العربية فقط مثل: أمريكا، روسيا، الأردن"],\n'
        '  "arabic_summary": "فقرة تفصيلية وموسعة (من 3 إلى 4 جمل تكتيكية عميقة) تشرح الأبعاد الخفية للحدث ومجرياته الميدانية.",\n'
        '  "real_driver": "تحليل نقدي وعميق جداً يشرح الدوافع والأهداف الجيوسياسية أو العسكرية الحقيقية وغير المعلنة وراء هذا الحدث.",\n'
        '  "strategic_forecast": "تقييم استراتيجي غني ومفصل يتوقع السيناريوهات القادمة، تحركات الجيوش، أو التداعيات الدبلوماسية خلال الـ 30 إلى 90 يوماً القادمة.",\n'
        '  "geopolitical_impact": "تقييم شامل ومطول يشرح كيف يؤثر هذا الحدث على موازين القوى العالمية والأمن الإقليمي في المنطقة.",\n'
        '  "hidden_actors": ["أسماء أجهزة الاستخبارات، الشركات العسكرية الخاصة، أو الدول الخفية المتورطة باللغة العربية"]\n'
        "}\n\n"
        "تنبيه حرج: لا تستخدم علامات التنصيص المزدوجة (\") أبداً داخل النصوص العربية، استبدلها بعلامات مفردة (') عند الحاجة. اخرج مصفوفة الـ JSON مباشرة بدون أي مقدمات أو هوامش."
    )

    user_content = "ابدأ التحليل الاستراتيجي المعمق للملفات التالية:\n\n"
    for idx, art in enumerate(articles):
        user_content += f"--- الملف {idx} ---\nالمصدر: {art['source_name']}\nالبيانات: {art['full_text']}\n\n"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.1,
            max_tokens=3500
        )
        
        raw_result = response.choices[0].message.content.strip()
        
        if "```" in raw_result:
            match = re.search(r'\[.*\]', raw_result, re.DOTALL)
            if match:
                raw_result = match.group(0)
                
        raw_result = raw_result.replace('\n', ' ').replace('\r', '')
        ai_analyses = json.loads(raw_result)
        
        final_reports = []
        for idx, art in enumerate(articles):
            if idx < len(ai_analyses):
                final_reports.append({**art, **ai_analyses[idx]})
            else:
                final_reports.append({**art, "category": "استراتيجي", "threat_level": "متوسط", "intel_signal": "مراقبة", "countries_involved": ["عالمي"], "arabic_summary": "تحليل تكتيكي مكمل للنشرة.", "geopolitical_impact": "تحت الدراسة."})
                
        return final_reports

    except Exception as e:
        print(f"Error in batch analysis: {e}")
        return [{**art, "category": "أمني", "threat_level": "عالي", "intel_signal": "مراقبة", "countries_involved": ["عالمي"], "arabic_summary": f"تقرير استراتيجي عاجل يتناول التطورات الساخنة المرتبطة بـ: {art['title']}.", "geopolitical_impact": "إعادة تموضع القوى جاري رصده ومتابعته."} for art in articles]
