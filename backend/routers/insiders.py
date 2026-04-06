from fastapi import APIRouter, Query
import httpx
from services.edgar import resolve_ticker, get_company_submissions
from services.insider_tracker import get_insider_trades, detect_cluster_buys

router = APIRouter()


@router.get("/insiders/{ticker}")
async def get_insider_trading(ticker: str, limit: int = Query(50, le=100)):
    async with httpx.AsyncClient() as client:
        cik = await resolve_ticker(ticker, client)
        if not cik:
            return {"error": f"Ticker '{ticker}' not found"}

        submissions = await get_company_submissions(cik, client)
        if not submissions:
            return {"error": "Failed to fetch SEC submissions"}

        trades = await get_insider_trades(cik, submissions, client, limit=limit)
        cluster_buys = detect_cluster_buys(trades)

        # Summary stats
        purchases = [t for t in trades if t.get("transaction_code") == "P"]
        sales = [t for t in trades if t.get("transaction_code") == "S"]

        return {
            "ticker": ticker.upper(),
            "cik": cik,
            "trades": trades,
            "total_trades": len(trades),
            "summary": {
                "total_purchases": len(purchases),
                "total_sales": len(sales),
                "total_purchase_value": sum(t.get("total_value", 0) for t in purchases),
                "total_sale_value": sum(t.get("total_value", 0) for t in sales),
                "net_activity": "NET BUYING" if len(purchases) > len(sales) else "NET SELLING" if len(sales) > len(purchases) else "NEUTRAL",
            },
            "cluster_buys": cluster_buys,
        }
