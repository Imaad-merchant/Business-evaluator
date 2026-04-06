import feedparser
import httpx
from datetime import datetime
from typing import Optional


async def scrape_news(company_name: str, ticker: str, client: httpx.AsyncClient, limit: int = 20) -> list[dict]:
    articles = []

    # Google News RSS
    google_articles = await _fetch_google_news(company_name, ticker, client)
    articles.extend(google_articles)

    # Yahoo Finance RSS
    yahoo_articles = await _fetch_yahoo_news(ticker, client)
    articles.extend(yahoo_articles)

    # Deduplicate by title similarity
    seen_titles = set()
    unique = []
    for a in articles:
        title_key = a["title"].lower()[:50]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique.append(a)

    # Sort by date, most recent first
    unique.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    return unique[:limit]


async def _fetch_google_news(company_name: str, ticker: str, client: httpx.AsyncClient) -> list[dict]:
    try:
        query = f"{company_name} {ticker} stock"
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        resp = await client.get(url, timeout=15.0, follow_redirects=True)
        resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        articles = []

        for entry in feed.entries[:15]:
            published = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6]).isoformat()
                except Exception:
                    published = entry.get("published", "")

            articles.append({
                "title": entry.get("title", ""),
                "source": entry.get("source", {}).get("title", "Google News") if hasattr(entry, "source") else "Google News",
                "url": entry.get("link", ""),
                "published_at": published,
                "summary": entry.get("summary", "")[:500],
            })

        return articles
    except Exception as e:
        print(f"Google News scrape failed: {e}")
        return []


async def _fetch_yahoo_news(ticker: str, client: httpx.AsyncClient) -> list[dict]:
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        resp = await client.get(url, timeout=15.0, follow_redirects=True)
        resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        articles = []

        for entry in feed.entries[:10]:
            published = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6]).isoformat()
                except Exception:
                    published = entry.get("published", "")

            articles.append({
                "title": entry.get("title", ""),
                "source": "Yahoo Finance",
                "url": entry.get("link", ""),
                "published_at": published,
                "summary": entry.get("summary", "")[:500],
            })

        return articles
    except Exception as e:
        print(f"Yahoo News scrape failed: {e}")
        return []
