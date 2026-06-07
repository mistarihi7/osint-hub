import feedparser
from newspaper import Article
import datetime
from typing import List, Dict, Any

# ======================================================
# 15+ مصدر من أقوى الصحف العالمية ذات المصداقية العالية
# ======================================================
DEFAULT_FEEDS = {
    # ---- أمريكية ----
    "Reuters":              "https://feeds.reuters.com/reuters/worldNews",
    "AP News":              "https://rsshub.app/apnews/topics/world-news",
    "The New York Times":   "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "The Washington Post":  "https://feeds.washingtonpost.com/rss/world",
    "Wall Street Journal":  "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "Foreign Policy":       "https://foreignpolicy.com/feed/",
    "Foreign Affairs":      "https://www.foreignaffairs.com/rss.xml",
    "Politico":             "https://www.politico.com/rss/politicopicks.xml",
    "NPR World":            "https://feeds.npr.org/1004/rss.xml",
    # ---- بريطانية ----
    "BBC World":            "http://feeds.bbci.co.uk/news/world/rss.xml",
    "The Guardian World":   "https://www.theguardian.com/world/rss",
    "The Economist":        "https://www.economist.com/international/rss.xml",
    "Financial Times":      "https://www.ft.com/world?format=rss",
    "The Times UK":         "https://www.thetimes.co.uk/rss/world",
    "The Telegraph":        "https://www.telegraph.co.uk/rss.xml",
    # ---- دولية رفيعة المصداقية ----
    "Al Jazeera English":   "https://www.aljazeera.com/xml/rss/all.xml",
    "DW (Deutsche Welle)":  "https://rss.dw.com/rdf/rss-en-all",
    "France 24":            "https://www.france24.com/en/rss",
    "Defense News":         "https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml",
    "Geopolitical Monitor": "https://www.geopoliticalmonitor.com/feed/",
}

def fetch_rss_articles(feed_url: str, source_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    articles = []
    try:
        feed = feedparser.parse(feed_url)
        entries = feed.entries[:limit]
        for entry in entries:
            articles.append({
                "title":     entry.get("title", "No Title"),
                "link":      entry.get("link", ""),
                "published": entry.get("published", str(datetime.datetime.now())),
                "source":    feed.feed.get("title", source_name),
                "source_name": source_name,
            })
    except Exception as e:
        print(f"[Error] فشل RSS من {source_name}: {e}")
    return articles

def scrape_full_article(url: str) -> str:
    if not url:
        return ""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"[Warning] فشل كشط: {url}: {e}")
        return ""

def get_intel_reports(limit_per_source: int = 5) -> List[Dict[str, Any]]:
    all_reports = []
    for source_name, feed_url in DEFAULT_FEEDS.items():
        print(f"[Info] جلب: {source_name}...")
        raw_articles = fetch_rss_articles(feed_url, source_name, limit=limit_per_source)
        for art in raw_articles:
            full_text = scrape_full_article(art["link"])
            art["full_text"] = full_text.strip() if full_text.strip() else art["title"]
            all_reports.append(art)
    print(f"[Done] إجمالي الأخبار المجلوبة: {len(all_reports)}")
    return all_reports

if __name__ == "__main__":
    reports = get_intel_reports(limit_per_source=1)
    print(f"تم جلب {len(reports)} مقالات.")
