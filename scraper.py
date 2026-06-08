import feedparser
import requests
import re
import html
import random

def get_intel_reports(limit_per_source=4):
    """
    استخدام Google News RSS كمجمع أساسي.
    هذه الطريقة تخترق الحظر السحابي 100% وتجلب أحدث أخبار (CNN, Reuters, BBC, الجزيرة) كل دقيقة.
    """
    sources = {
        "الرصد العالمي (Global)": "https://news.google.com/rss/search?q=geopolitics+OR+military+OR+pentagon+when:1d&hl=en-US&gl=US&ceid=US:en",
        "رصد الشرق الأوسط (ME)": "https://news.google.com/rss/search?q=تصعيد+OR+حرب+OR+عسكري+OR+استخبارات+when:1d&hl=ar&gl=EG&ceid=EG:ar",
        "سكاي نيوز عربية (Sky News)": "https://www.skynewsarabia.com/rss",
        "روسيا اليوم (RT)": "https://arabic.rt.com/rss/news/"
    }
    
    articles_pool = []
    session = requests.Session()
    
    for name, url in sources.items():
        try:
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            response = session.get(url, timeout=10)
            if response.status_code != 200: continue
                
            feed = feedparser.parse(response.text)
            count = 0
            
            for entry in feed.entries:
                if count >= limit_per_source: break
                    
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", entry.get("description", ""))
                
                if "<" in summary:
                    summary = re.sub(r'<[^>]+>', '', summary)
                summary = html.unescape(summary).strip()
                
                if not title: continue
                
                # تنظيف العنوان من اسم المصدر الذي يضيفه جوجل أوتوماتيكياً
                clean_title = title.split(" - ")[0]
                
                full_text = f"العنوان: {clean_title}. التفاصيل: {summary}"
                
                articles_pool.append({
                    "title": clean_title,
                    "link": link,
                    "source_name": name,
                    "full_text": full_text[:1500]
                })
                count += 1
        except Exception as e:
            continue
            
    return articles_pool
            }
        ]
        
    return articles_pool
