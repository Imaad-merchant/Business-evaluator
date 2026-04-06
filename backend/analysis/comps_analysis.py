import httpx
from typing import Optional
from services import edgar
from services.xbrl_parser import parse_financial_statements
from services.yahoo_finance import get_quote_summary


# Common industry peer mappings for well-known companies
KNOWN_PEERS = {
    "TSLA": ["RIVN", "LCID", "NIO", "F", "GM"],
    "AAPL": ["MSFT", "GOOGL", "AMZN", "META", "SAMSUNG"],
    "MSFT": ["AAPL", "GOOGL", "AMZN", "CRM", "ORCL"],
    "GOOGL": ["META", "MSFT", "AMZN", "SNAP", "PINS"],
    "AMZN": ["WMT", "SHOP", "EBAY", "TGT", "BABA"],
    "META": ["GOOGL", "SNAP", "PINS", "TWTR", "RBLX"],
    "NVDA": ["AMD", "INTC", "AVGO", "QCOM", "TSM"],
    "JPM": ["BAC", "WFC", "GS", "MS", "C"],
    "JNJ": ["PFE", "MRK", "ABBV", "LLY", "UNH"],
    "V": ["MA", "PYPL", "SQ", "AXP", "DFS"],
}


async def find_comparable_companies(
    ticker: str, sic_code: str, client: httpx.AsyncClient, limit: int = 5
) -> list[str]:
    ticker_upper = ticker.upper()

    # Check known peers first
    if ticker_upper in KNOWN_PEERS:
        return KNOWN_PEERS[ticker_upper][:limit]

    # Fall back to SIC code search from the ticker map
    ticker_map = await edgar.load_ticker_map(client)

    # Get all companies, then filter by SIC from EDGAR
    # For now, return empty — SIC-based peer finding requires
    # fetching each company's submissions which is expensive
    # TODO: Build a local SIC-to-ticker index
    return []


async def run_comps_analysis(
    ticker: str,
    target_financials: dict,
    target_stock: Optional[dict],
    sic_code: str,
    client: httpx.AsyncClient,
) -> dict:
    peers = await find_comparable_companies(ticker, sic_code, client)
    if not peers:
        return {"error": "No comparable companies found", "peers": []}

    peer_data = []
    for peer_ticker in peers:
        try:
            quote = await get_quote_summary(peer_ticker, client)
            if not quote:
                continue

            peer_data.append({
                "ticker": peer_ticker,
                "market_cap": quote.get("market_cap"),
                "pe_ratio": quote.get("pe_ratio"),
                "forward_pe": quote.get("forward_pe"),
                "price_to_book": quote.get("price_to_book"),
                "ev_to_revenue": quote.get("ev_to_revenue"),
                "ev_to_ebitda": quote.get("ev_to_ebitda"),
                "profit_margin": quote.get("profit_margin"),
                "revenue_growth": quote.get("revenue_growth"),
            })
        except Exception as e:
            print(f"Comps failed for {peer_ticker}: {e}")
            continue

    if not peer_data:
        return {"error": "Could not fetch peer data", "peers": []}

    # Calculate median multiples
    def _median(values):
        clean = [v for v in values if v is not None and v > 0]
        if not clean:
            return None
        clean.sort()
        n = len(clean)
        if n % 2 == 0:
            return (clean[n // 2 - 1] + clean[n // 2]) / 2
        return clean[n // 2]

    median_pe = _median([p.get("pe_ratio") for p in peer_data])
    median_ev_rev = _median([p.get("ev_to_revenue") for p in peer_data])
    median_ev_ebitda = _median([p.get("ev_to_ebitda") for p in peer_data])
    median_pb = _median([p.get("price_to_book") for p in peer_data])

    # Calculate implied valuations for target
    implied = {}
    target_revenue = target_financials.get("revenue")
    target_ni = target_financials.get("net_income")
    target_ebitda = target_financials.get("ebitda")
    target_equity = target_financials.get("stockholders_equity")
    target_shares = target_financials.get("shares_outstanding") or target_financials.get("shares_diluted")
    target_mc = target_stock.get("market_cap") if target_stock else None

    if median_pe and target_ni and target_shares:
        implied["pe_implied_value"] = round(median_pe * target_ni / target_shares, 2)

    if median_ev_rev and target_revenue and target_shares:
        implied["ev_rev_implied_value"] = round(median_ev_rev * target_revenue / target_shares, 2)

    if median_ev_ebitda and target_ebitda and target_shares:
        implied["ev_ebitda_implied_value"] = round(median_ev_ebitda * target_ebitda / target_shares, 2)

    if median_pb and target_equity and target_shares:
        implied["pb_implied_value"] = round(median_pb * target_equity / target_shares, 2)

    # Average implied value
    implied_values = [v for v in implied.values() if v and v > 0]
    avg_implied = round(sum(implied_values) / len(implied_values), 2) if implied_values else None

    current_price = target_stock.get("current_price") if target_stock else None
    premium_discount = None
    if avg_implied and current_price:
        premium_discount = round((current_price / avg_implied - 1) * 100, 2)

    return {
        "ticker": ticker,
        "peers": peer_data,
        "median_multiples": {
            "pe_ratio": round(median_pe, 2) if median_pe else None,
            "ev_to_revenue": round(median_ev_rev, 2) if median_ev_rev else None,
            "ev_to_ebitda": round(median_ev_ebitda, 2) if median_ev_ebitda else None,
            "price_to_book": round(median_pb, 2) if median_pb else None,
        },
        "implied_valuations": implied,
        "average_implied_value": avg_implied,
        "current_price": current_price,
        "premium_discount_percent": premium_discount,
        "verdict": _comps_verdict(premium_discount) if premium_discount is not None else "N/A",
    }


def _comps_verdict(premium: float) -> str:
    if premium > 30:
        return "TRADING AT SIGNIFICANT PREMIUM TO PEERS"
    elif premium > 10:
        return "TRADING AT PREMIUM TO PEERS"
    elif premium > -10:
        return "IN LINE WITH PEERS"
    elif premium > -30:
        return "TRADING AT DISCOUNT TO PEERS"
    else:
        return "TRADING AT SIGNIFICANT DISCOUNT TO PEERS"
