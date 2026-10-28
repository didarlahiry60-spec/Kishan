import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Any
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

# প্রধান বাংলা কৃষি ও বাজার সংবাদ আরএসএস ফিডস
LIVE_NEWS_FEEDS = [
    "https://news.google.com/rss/search?q=%E0%A6%AC%E0%A6%BE%E0%A6%9C%E0%A6%BE%E0%A6%B0%E0%A6%A6%E0%A6%B0+%E0%A6%95%E0%A7%83%E0%A6%B7%E0%A6%BF+%E0%A6%A6%E0%A6%BE%E0%A6%AE&hl=bn&gl=BD&ceid=BD:bn",
    "https://news.google.com/rss/search?q=%E0%A6%86%E0%A6%B2%E0%A7%81%E0%A6%B0+%E0%A6%A6%E0%A6%BE%E0%A6%AE+%E0%A6%AA%E0%A7%87%E0%A6%81%E0%A6%AF%E0%A6%BC%E0%A6%BE%E0%A6%9C%E0%A7%87%E0%A6%B0+%E0%A6%A6%E0%A6%BE%E0%A6%AE+%E0%A6%B8%E0%A6%AC%E0%A6%9C%E0%A6%BF&hl=bn&gl=BD&ceid=BD:bn",
    "https://news.google.com/rss/search?q=%E0%A6%A7%E0%A6%BE%E0%A6%A8%E0%A7%87%E0%A6%B0+%E0%A6%A6%E0%A6%BE%E0%A6%AE+%E0%A6%9A%E0%A6%BE%E0%A6%B2%E0%A7%87%E0%A6%B0+%E0%A6%A6%E0%A6%BE%E0%A6%AE+%E0%A6%95%E0%A6%BE%E0%A6%93%E0%A6%B0%E0%A6%BE%E0%A6%A8+%E0%A6%AC%E0%A6%BE%E0%A6%9C%E0%A6%BE%E0%A6%B0&hl=bn&gl=BD&ceid=BD:bn"
]

class LiveMarketCrawler:
    """
    Autonomous Multi-Source Live Web Crawler & Market Signal Extractor.
    Fetches real-time market updates, newspaper reports, and spot commodity prices.
    """

    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*"
        }

    async def crawl_live_market_signals(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        ইন্টারনেট থেকে সরাসরি লাইভ বাজারদর সংবাদের ফিড সংগ্রহ ও সিগন্যাল এক্সট্রাক্ট করা
        """
        all_articles = []
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            for feed_url in LIVE_NEWS_FEEDS:
                try:
                    resp = await client.get(feed_url)
                    if resp.status_code == 200:
                        articles = self._parse_rss(resp.text)
                        all_articles.extend(articles)
                except Exception as e:
                    logger.warning(f"[LiveMarketCrawler] Error crawling feed: {e}")

        # ডুপ্লিকেট বাদ দেওয়া ও সিগন্যাল অ্যানালাইসিস
        unique_articles = {}
        for a in all_articles:
            key = a["title"].strip()
            if key not in unique_articles:
                unique_articles[key] = a

        sorted_signals = list(unique_articles.values())[:limit]
        return sorted_signals

    def _parse_rss(self, xml_content: str) -> List[Dict[str, Any]]:
        results = []
        try:
            root = ET.fromstring(xml_content)
            for item in root.findall(".//item"):
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                source_el = item.find("source")
                source_name = source_el.text if source_el is not None else "জাতীয় দৈনিক"

                # পণ্য ও ট্রেন্ড ডিটেকশন
                detected_crops = self._detect_crops(title)
                trend, sentiment = self._detect_trend(title)

                results.append({
                    "title": title,
                    "link": link,
                    "pub_date": pub_date,
                    "source": source_name,
                    "detected_crops": detected_crops,
                    "trend": trend,           # up, down, stable
                    "sentiment": sentiment,   # bullish, bearish, neutral
                    "crawled_at": datetime.now(timezone.utc).isoformat()
                })
        except Exception as e:
            logger.error(f"[LiveMarketCrawler] XML parsing error: {e}")
        return results

    def _detect_crops(self, text: str) -> List[str]:
        known_crops = ["চাল", "ধান", "আলু", "পেঁয়াজ", "রসুন", "মরিচ", "কাঁচা মরিচ", "বেগুন", "টমেটো", "ডাল", "সরিষা", "সবজি", "ডিম", "মুরগি"]
        found = []
        for c in known_crops:
            if c in text:
                found.append(c)
        return found if found else ["কৃষি পণ্য"]

    def _detect_trend(self, text: str) -> tuple[str, str]:
        if any(w in text for w in ["বাড়ল", "বাড়ল", "বৃদ্ধি", "ঊর্ধ্বমুখী", "চড়া", "বাড়তি", "বেড়েছে", "বেড়েছে", "উত্তাপ"]):
            return "up", "bullish"
        elif any(w in text for w in ["কমল", "কমলো", "হ্রাস", "নিম্নমুখী", "কমতির দিকে", "পতন", "স্বস্তি"]):
            return "down", "bearish"
        else:
            return "stable", "neutral"

live_market_crawler = LiveMarketCrawler()
