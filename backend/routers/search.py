from fastapi import APIRouter, Query
import httpx
from services.edgar import search_companies, load_ticker_map

router = APIRouter()


@router.get("/search")
async def search(q: str = Query(..., min_length=1), limit: int = Query(10, le=20)):
    async with httpx.AsyncClient() as client:
        # Quick ticker match first
        ticker_map = await load_ticker_map(client)
        q_upper = q.upper().strip()

        results = []

        # Exact ticker match
        if q_upper in ticker_map:
            results.append({
                "ticker": q_upper,
                "cik": ticker_map[q_upper],
                "match_type": "exact",
            })

        # Prefix matches
        for ticker, cik in ticker_map.items():
            if ticker.startswith(q_upper) and ticker != q_upper:
                results.append({
                    "ticker": ticker,
                    "cik": cik,
                    "match_type": "prefix",
                })
                if len(results) >= limit:
                    break

        # If few results, do full-text search
        if len(results) < limit:
            full_results = await search_companies(q, client, limit - len(results))
            existing_tickers = {r["ticker"] for r in results}
            for r in full_results:
                if r["ticker"] not in existing_tickers:
                    results.append({**r, "match_type": "search"})

        return {"query": q, "results": results[:limit]}
