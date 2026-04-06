from fastapi import APIRouter, Query
import httpx
from services.edgar import resolve_ticker, get_company_submissions, extract_company_info
from services.news_scraper import scrape_news
from services.sentiment import analyze_articles

router = APIRouter()


@router.get("/news/{ticker}")
async def get_news(ticker: str, limit: int = Query(20, le=50)):
    async with httpx.AsyncClient() as client:
        cik = await resolve_ticker(ticker, client)
        company_name = ticker.upper()

        if cik:
            submissions = await get_company_submissions(cik, client)
            if submissions:
                info = extract_company_info(submissions)
                company_name = info.get("name", ticker.upper())

        articles = await scrape_news(company_name, ticker.upper(), client, limit=limit)
        sentiment = analyze_articles(articles)

        return {
            "ticker": ticker.upper(),
            "company_name": company_name,
            "sentiment": {
                "overall_score": sentiment["overall_score"],
                "overall_label": sentiment["overall_label"],
                "positive_count": sentiment["positive_count"],
                "negative_count": sentiment["negative_count"],
                "neutral_count": sentiment["neutral_count"],
            },
            "articles": sentiment["articles"],
            "total": len(sentiment["articles"]),
        }
