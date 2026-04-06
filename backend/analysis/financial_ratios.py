from typing import Optional


def calculate_ratios(statements: list[dict], stock_data: Optional[dict] = None) -> dict:
    if not statements:
        return {}

    latest = statements[0]
    prior = statements[1] if len(statements) > 1 else None

    ratios = {
        "profitability": _profitability_ratios(latest),
        "liquidity": _liquidity_ratios(latest),
        "leverage": _leverage_ratios(latest),
        "efficiency": _efficiency_ratios(latest),
        "growth": _growth_ratios(latest, prior),
        "valuation": _valuation_ratios(latest, stock_data) if stock_data else {},
        "per_share": _per_share_metrics(latest, stock_data),
    }

    return ratios


def _profitability_ratios(s: dict) -> dict:
    revenue = s.get("revenue")
    ratios = {}

    if revenue and revenue != 0:
        if s.get("gross_profit") is not None:
            ratios["gross_margin"] = round(s["gross_profit"] / revenue * 100, 2)
        if s.get("operating_income") is not None:
            ratios["operating_margin"] = round(s["operating_income"] / revenue * 100, 2)
        if s.get("net_income") is not None:
            ratios["net_margin"] = round(s["net_income"] / revenue * 100, 2)
        if s.get("ebitda") is not None:
            ratios["ebitda_margin"] = round(s["ebitda"] / revenue * 100, 2)

    if s.get("net_income") and s.get("stockholders_equity") and s["stockholders_equity"] != 0:
        ratios["roe"] = round(s["net_income"] / s["stockholders_equity"] * 100, 2)

    if s.get("net_income") and s.get("total_assets") and s["total_assets"] != 0:
        ratios["roa"] = round(s["net_income"] / s["total_assets"] * 100, 2)

    return ratios


def _liquidity_ratios(s: dict) -> dict:
    ratios = {}
    cl = s.get("total_current_liabilities")

    if cl and cl != 0:
        if s.get("total_current_assets") is not None:
            ratios["current_ratio"] = round(s["total_current_assets"] / cl, 2)
        # Quick ratio: (current assets - inventory) / current liabilities
        # Approximate with cash + short-term investments
        cash = (s.get("cash_and_equivalents") or 0) + (s.get("short_term_investments") or 0)
        if cash:
            ratios["quick_ratio"] = round(cash / cl, 2)

    if s.get("operating_cash_flow") and s.get("total_current_liabilities") and s["total_current_liabilities"] != 0:
        ratios["cash_flow_ratio"] = round(s["operating_cash_flow"] / s["total_current_liabilities"], 2)

    return ratios


def _leverage_ratios(s: dict) -> dict:
    ratios = {}

    if s.get("total_liabilities") and s.get("stockholders_equity") and s["stockholders_equity"] != 0:
        ratios["debt_to_equity"] = round(s["total_liabilities"] / s["stockholders_equity"], 2)

    if s.get("total_liabilities") and s.get("total_assets") and s["total_assets"] != 0:
        ratios["debt_to_assets"] = round(s["total_liabilities"] / s["total_assets"], 2)

    if s.get("operating_income") and s.get("interest_expense") and s["interest_expense"] != 0:
        ratios["interest_coverage"] = round(s["operating_income"] / abs(s["interest_expense"]), 2)

    if s.get("long_term_debt") and s.get("ebitda") and s["ebitda"] != 0:
        ratios["net_debt_to_ebitda"] = round(
            (s["long_term_debt"] - (s.get("cash_and_equivalents") or 0)) / s["ebitda"], 2
        )

    return ratios


def _efficiency_ratios(s: dict) -> dict:
    ratios = {}

    if s.get("revenue") and s.get("total_assets") and s["total_assets"] != 0:
        ratios["asset_turnover"] = round(s["revenue"] / s["total_assets"], 2)

    return ratios


def _growth_ratios(current: dict, prior: Optional[dict]) -> dict:
    if not prior:
        return {}

    ratios = {}

    for key, label in [
        ("revenue", "revenue_growth"),
        ("net_income", "net_income_growth"),
        ("operating_income", "operating_income_growth"),
        ("ebitda", "ebitda_growth"),
        ("free_cash_flow", "fcf_growth"),
    ]:
        curr_val = current.get(key)
        prev_val = prior.get(key)
        if curr_val is not None and prev_val is not None and prev_val != 0:
            ratios[label] = round((curr_val - prev_val) / abs(prev_val) * 100, 2)

    return ratios


def _valuation_ratios(s: dict, stock: dict) -> dict:
    ratios = {}
    market_cap = stock.get("market_cap")

    if not market_cap or market_cap == 0:
        return ratios

    if s.get("net_income") and s["net_income"] != 0:
        ratios["pe_ratio"] = round(market_cap / s["net_income"], 2)

    if s.get("stockholders_equity") and s["stockholders_equity"] != 0:
        ratios["pb_ratio"] = round(market_cap / s["stockholders_equity"], 2)

    if s.get("revenue") and s["revenue"] != 0:
        ratios["ps_ratio"] = round(market_cap / s["revenue"], 2)

    ev = market_cap + (s.get("total_debt") or s.get("long_term_debt") or 0) - (s.get("cash_and_equivalents") or 0)
    ratios["enterprise_value"] = ev

    if s.get("revenue") and s["revenue"] != 0:
        ratios["ev_to_revenue"] = round(ev / s["revenue"], 2)

    if s.get("ebitda") and s["ebitda"] != 0:
        ratios["ev_to_ebitda"] = round(ev / s["ebitda"], 2)

    if s.get("free_cash_flow") and s["free_cash_flow"] != 0:
        ratios["price_to_fcf"] = round(market_cap / s["free_cash_flow"], 2)

    return ratios


def _per_share_metrics(s: dict, stock: Optional[dict]) -> dict:
    ratios = {}
    shares = s.get("shares_outstanding") or s.get("shares_diluted")

    if shares and shares != 0:
        if s.get("revenue"):
            ratios["revenue_per_share"] = round(s["revenue"] / shares, 2)
        if s.get("free_cash_flow"):
            ratios["fcf_per_share"] = round(s["free_cash_flow"] / shares, 2)
        if s.get("stockholders_equity"):
            ratios["book_value_per_share"] = round(s["stockholders_equity"] / shares, 2)

    return ratios
