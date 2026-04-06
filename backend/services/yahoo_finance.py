import httpx
from typing import Optional

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
QUOTE_URL = "https://query1.finance.yahoo.com/v10/finance/quoteSummary"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}


async def get_stock_price(ticker: str, client: httpx.AsyncClient) -> Optional[dict]:
    try:
        resp = await client.get(
            f"{CHART_URL}/{ticker}",
            params={"interval": "1d", "range": "5d"},
            headers=HEADERS,
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()

        result = data.get("chart", {}).get("result", [])
        if not result:
            return None

        meta = result[0].get("meta", {})
        return {
            "current_price": meta.get("regularMarketPrice"),
            "previous_close": meta.get("chartPreviousClose") or meta.get("previousClose"),
            "currency": meta.get("currency", "USD"),
            "exchange": meta.get("exchangeName", ""),
            "market_cap": None,  # Will be fetched from quote summary
        }
    except Exception as e:
        print(f"Yahoo Finance price failed for {ticker}: {e}")
        return None


async def get_stock_history(
    ticker: str, client: httpx.AsyncClient, period: str = "1y", interval: str = "1d"
) -> Optional[list[dict]]:
    try:
        resp = await client.get(
            f"{CHART_URL}/{ticker}",
            params={"interval": interval, "range": period},
            headers=HEADERS,
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()

        result = data.get("chart", {}).get("result", [])
        if not result:
            return None

        timestamps = result[0].get("timestamp", [])
        indicators = result[0].get("indicators", {})
        quotes = indicators.get("quote", [{}])[0]

        history = []
        for i, ts in enumerate(timestamps):
            history.append({
                "timestamp": ts,
                "open": quotes.get("open", [None])[i] if i < len(quotes.get("open", [])) else None,
                "high": quotes.get("high", [None])[i] if i < len(quotes.get("high", [])) else None,
                "low": quotes.get("low", [None])[i] if i < len(quotes.get("low", [])) else None,
                "close": quotes.get("close", [None])[i] if i < len(quotes.get("close", [])) else None,
                "volume": quotes.get("volume", [None])[i] if i < len(quotes.get("volume", [])) else None,
            })

        return history
    except Exception as e:
        print(f"Yahoo Finance history failed for {ticker}: {e}")
        return None


async def get_quote_summary(ticker: str, client: httpx.AsyncClient) -> Optional[dict]:
    try:
        resp = await client.get(
            f"{QUOTE_URL}/{ticker}",
            params={"modules": "summaryDetail,defaultKeyStatistics,financialData"},
            headers=HEADERS,
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()

        result = data.get("quoteSummary", {}).get("result", [])
        if not result:
            return None

        modules = result[0]
        summary = modules.get("summaryDetail", {})
        stats = modules.get("defaultKeyStatistics", {})
        fin = modules.get("financialData", {})

        def _val(d: dict, key: str):
            v = d.get(key, {})
            if isinstance(v, dict):
                return v.get("raw") or v.get("fmt")
            return v

        return {
            "market_cap": _val(summary, "marketCap"),
            "pe_ratio": _val(summary, "trailingPE"),
            "forward_pe": _val(summary, "forwardPE"),
            "price_to_book": _val(stats, "priceToBook"),
            "enterprise_value": _val(stats, "enterpriseValue"),
            "ev_to_revenue": _val(stats, "enterpriseToRevenue"),
            "ev_to_ebitda": _val(stats, "enterpriseToEbitda"),
            "beta": _val(stats, "beta"),
            "fifty_two_week_high": _val(summary, "fiftyTwoWeekHigh"),
            "fifty_two_week_low": _val(summary, "fiftyTwoWeekLow"),
            "dividend_yield": _val(summary, "dividendYield"),
            "payout_ratio": _val(summary, "payoutRatio"),
            "profit_margin": _val(fin, "profitMargins"),
            "revenue_growth": _val(fin, "revenueGrowth"),
            "target_mean_price": _val(fin, "targetMeanPrice"),
            "recommendation": _val(fin, "recommendationKey"),
        }
    except Exception as e:
        print(f"Yahoo Finance quote summary failed for {ticker}: {e}")
        return None
