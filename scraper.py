import feedparser
import requests
from newspaper import Article
import datetime
from typing import List, Dict, Any

# ══════════════════════════════════════════════════════════════════════════════
# مصادر موثوقة ومفتوحة — تم اختيارها لأنها لا تحجب الـ scraping
# ══════════════════════════════════════════════════════════════════════════════
DEFAULT_FEEDS = {
    "Reuters":              "https://feeds.reuters.com/reuters/worldNews",
    "AP News":              "https://rsshub.app/apnews/topics/world-news",
    "BBC World":            "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Al Jazeera English":   "https://www.aljazeera.com/xml/rss/all.xml",
    "DW (Deutsche Welle)":  "https://rss.dw.com/rdf/rss-en-all",
    "France 24":            "https://www.france24.com/en/rss",
    "NPR World":            "https://feeds.npr.org/1004/rss.xml",
    "The Guardian World":   "https://www.theguardian.com/world/rss",
    "Foreign Policy":       "https://foreignpolicy.com/feed/",
    "Geopolitical Monitor": "https://www.geopoliticalmonitor.com/feed/",
    "Defense News":         "https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml",
    "Middle East Eye":      "https://www.middleeasteye.net/rss",
    "The Intercept":        "https://theintercept.com/feed/?rss",
    "Asia Times":           "https://asiatimes.com/feed/",
    "Euronews":             "https://feeds.feedburner.com/euronews/en/news/",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_rss_articles(feed_url: str, source_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """جلب المقالات من RSS مع استخراج الوصف كنص احتياطي."""
    articles = []
    try:
        feed = feedparser.parse(feed_url, request_headers=HEADERS)
        for entry in feed.entries[:limit]:
            # نستخرج الوصف من RSS مباشرة كنص احتياطي
            rss_summary = ""
            for field in ["summary", "description", "content"]:
                val = entry.get(field, "")
                if isinstance(val, list) and val:
                    val = val[0].get("value", "")
                if val and len(str(val)) > 50:
                    rss_summary = str(val)
                    break

            articles.append({
                "title":       entry.get("title", "No Title"),
                "link":        entry.get("link", ""),
                "published":   entry.get("published", str(datetime.datetime.now())),
                "source_name": source_name,
                "rss_summary": rss_summary,
            })
    except Exception as e:
        print(f"[RSS Error] {source_name}: {e}")
    return articles


def scrape_full_article(url: str) -> str:
    """
    محاولة كشط النص الكامل — مع fallback آمن.
    يرجع النص أو سلسلة فارغة إذا فشل.
    """
    if not url:
        return ""
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text.strip()
        # إذا النص أقل من 100 حرف = المقال محجوب أو فارغ
        return text if len(text) > 100 else ""
    except Exception:
        return ""


def get_intel_reports(limit_per_source: int = 5) -> List[Dict[str, Any]]:
    """
    المحرك الرئيسي:
    1. يجلب من RSS
    2. يحاول كشط النص الكامل
    3. إذا فشل الكشط يستخدم وصف RSS
    4. إذا فشل كل شيء يستخدم العنوان فقط
    """
    all_reports = []

    for source_name, feed_url in DEFAULT_FEEDS.items():
        print(f"[Fetching] {source_name}...")
        articles = fetch_rss_articles(feed_url, source_name, limit=limit_per_source)

        for art in articles:
            full_text = scrape_full_article(art["link"])

            if len(full_text) > 100:
                text_source = "full_article"
            elif len(art.get("rss_summary", "")) > 50:
                full_text   = art["rss_summary"]
                text_source = "rss_summary"
            else:
                full_text   = art["title"]
                text_source = "title_only"

            art["full_text"]   = full_text
            art["text_source"] = text_source
            all_reports.append(art)

    print(f"[Done] إجمالي: {len(all_reports)} خبر")
    return all_reports
