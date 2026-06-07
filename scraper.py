import feedparser
from newspaper import Article
import requests

def get_intel_reports(limit_per_source=3):
    """
    مستودع جلب الأخبار المطور والمقاوم للحظر السحابي
    """
    # قائمة مصادر مستقرة جداً وتدعم السحاب (مزيج دولي وإقليمي)
    sources = {
        "Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.xml",
        "BBC International": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "CNN World": "http://rss.cnn.com/rss/edition_world.rss",
        "RT World": "https://www.rt.com/rss/news/"
    }
    
    articles_pool = []
    
    # إعداد الـ Headers لخدعة الحماية وإظهار الطلب كأنه متصفح عادي
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for name, url in sources.items():
        try:
            # جلب الرابط باستخدام requests أولاً لتفادي الحظر
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
                
            # قراءة الـ RSS feed من النص المجلوب
            feed = feedparser.parse(response.text)
            
            count = 0
            for entry in feed.entries:
                if count >= limit_per_source:
                    break
                    
                title = entry.get("title", "")
                link = entry.get("link", "")
                
                if not title or not link:
                    continue
                    
                # كشط النص الكامل للمقال
                try:
                    art = Article(link)
                    art.download()
                    art.parse()
                    full_text = art.text if art.text else title
                except:
                    # إذا فشل كشط النص الكامل بسبب حماية الموقع، نأخذ الملخص المتاح في الـ RSS
                    full_text = entry.get("summary", title)
                
                articles_pool.append({
                    "title": title,
                    "link": link,
                    "source_name": name,
                    "full_text": full_text[:1500] # نأخذ أول 1500 حرف فقط لتوفير الـ Tokens
                })
                count += 1
                
        except Exception as e:
            print(f"خطأ في جلب مصدر {name}: {e}")
            continue
            
    return articles_pool
