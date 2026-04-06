from fastapi import APIRouter, Query
import httpx
from services.edgar import resolve_ticker, get_company_submissions, extract_recent_filings

router = APIRouter()


@router.get("/filings/{ticker}")
async def get_filings(
    ticker: str,
    form_types: str = Query(None, description="Comma-separated form types: 10-K,10-Q,8-K,4"),
    limit: int = Query(30, le=100),
):
    async with httpx.AsyncClient() as client:
        cik = await resolve_ticker(ticker, client)
        if not cik:
            return {"error": f"Ticker '{ticker}' not found"}

        submissions = await get_company_submissions(cik, client)
        if not submissions:
            return {"error": "Failed to fetch SEC submissions"}

        types = form_types.split(",") if form_types else None
        filings = extract_recent_filings(submissions, form_types=types, limit=limit)

        return {
            "ticker": ticker.upper(),
            "cik": cik,
            "filings": filings,
            "total": len(filings),
        }
