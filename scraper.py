import feedparser
import requests
import re
import html

def get_intel_reports(limit_per_source=3):
    """
    محرك رصد استخباراتي متطور ومقاوم للحجب السحابي 
    يجمع بين قنوات التلفزة العالمية، الصحف، ومراكز صناعة القرار العسكري
    """
    # شبكة رصد متنوعة (صحافة، قنوات، ومراكز أبحاث قرار)
    sources = {
        "مركز الدراسات الاستراتيجية (CSIS)": "https://www.csis.org/blogs/rss.xml",
        "محللي كواليس الحرب (War on the Rocks)": "https://warontherocks.com/feed/",
        "وكالة رويترز الدولية (Reuters)": "https://www.reutersagency.com/feed/",
        "قناة الجزيرة العالمية (Al Jazeera)": "https://www.aljazeera.com/xml/rss/all.xml",
        "شبكة سي إن إن الدولية (CNN)": "http://rss.cnn.com/rss/edition_world.rss",
        "روسيا اليوم العالمية (RT News)": "https://www.rt.com/rss/news/"
    }
    
    articles_pool = []
    
    # بناء جلسة اتصال متطورة تخدع أنظمة الحماية الجيوسياسية للمواقع
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    })

    for name, url in sources.items():
        try:
            # جلب محتوى الـ RSS بأمان وسرعة وبمهلة 8 ثوانٍ
            response = session.get(url, timeout=8)
            if response.status_code != 200:
                continue
                
            # فك تشفير المحتوى وقراءته بنجاح
            feed = feedparser.parse(response.text)
            
            count = 0
            for entry in feed.entries:
                if count >= limit_per_source:
                    break
                    
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                
                # جلب الملخص وتطهيره تماماً من كود الـ HTML المكسور
                summary = entry.get("summary", entry.get("description", ""))
                if "<" in summary:
                    summary = re.sub(r'<[^>]+>', '', summary)
                summary = html.unescape(summary).strip()
                
                if not title or not link:
                    continue
                
                # صياغة نص متكامل ودسم يحتوي على السياق لصناعة تحليل ذكي جداً
                full_text = f"المصدر الأصلي: {name}. العنوان الاستراتيجي: {title}. التفاصيل والمضمون: {summary}"
                
                articles_pool.append({
                    "title": title,
                    "link": link,
                    "source_name": name,
                    "full_text": full_text[:1500] # اقتطاع الحجم بدقة لضمان سرعة معالجة الطلب الموحد
                })
                count += 1
                
        except Exception as e:
            # في حال حجب سيرفر معين، يتخطاه الكود بمرونة للمصدر الذي يليه
            print(f"تخطي المصدر {name} بسبب جدار الحماية: {e}")
            continue
            
    return articles_pool
