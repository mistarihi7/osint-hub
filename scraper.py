import feedparser
import requests
import html

def get_intel_reports(limit_per_source=2):
    """
    محرك جلب خفيف وسريع جداً، يعتمد على الـ RSS مباشرة لتفادي التعليق والحظر
    """
    sources = {
        "Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.xml",
        "BBC International": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "CNN World": "http://rss.cnn.com/rss/edition_world.rss",
        "RT World": "https://www.rt.com/rss/news/"
    }
    
    articles_pool = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for name, url in sources.items():
        try:
            # جلب سريع جداً للنص
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                continue
                
            feed = feedparser.parse(response.text)
            
            count = 0
            for entry in feed.entries:
                if count >= limit_per_source:
                    break
                    
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                # نأخذ الملخص المتاح مباشرة في الـ RSS وننظفه من أي وسم HTML
                summary = entry.get("summary", "")
                if "<" in summary:
                    # تنظيف سريع لإزالة أي كود HTML مكسور قد يخرب الـ JSON
                    summary = re.sub(r'<[^>]+>', '', summary)
                
                if not title or not link:
                    continue
                
                # ندمج العنوان والملخص المتاح ليكون هو النص الممرر للـ AI
                full_text = f"Title: {title}. Summary: {summary}"
                
                articles_pool.append({
                    "title": title,
                    "link": link,
                    "source_name": name,
                    "full_text": full_text[:1000] # تحديد الحجم تماماً لضمان السرعة القصوى
                })
                count += 1
                
        except Exception as e:
            print(f"خطأ في مصدر {name}: {e}")
            continue
            
    return articles_pool
