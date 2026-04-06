from typing import Optional
import math


def calculate_dcf(
    statements: list[dict],
    current_price: Optional[float] = None,
    shares_outstanding: Optional[int] = None,
    market_cap: Optional[int] = None,
) -> dict:
    if len(statements) < 2:
        return {"error": "Insufficient financial data for DCF (need at least 2 years)"}

    # Get FCF history
    fcf_history = []
    for s in reversed(statements):
        fcf = s.get("free_cash_flow")
        if fcf is not None:
            fcf_history.append({"year": s.get("fiscal_year"), "fcf": fcf})

    if len(fcf_history) < 2:
        return {"error": "Insufficient free cash flow data"}

    latest_fcf = fcf_history[-1]["fcf"]
    if latest_fcf <= 0:
        # Company has negative FCF — use operating cash flow instead
        ocf_history = []
        for s in reversed(statements):
            ocf = s.get("operating_cash_flow")
            if ocf is not None:
                ocf_history.append({"year": s.get("fiscal_year"), "fcf": ocf})

        if len(ocf_history) >= 2 and ocf_history[-1]["fcf"] > 0:
            fcf_history = ocf_history
            latest_fcf = fcf_history[-1]["fcf"]
        else:
            return {
                "error": "Negative free cash flow — DCF not applicable",
                "latest_fcf": latest_fcf,
                "note": "Consider using comps valuation instead",
            }

    # Calculate growth rate (CAGR)
    first_fcf = fcf_history[0]["fcf"]
    years = len(fcf_history) - 1

    if first_fcf > 0 and latest_fcf > 0 and years > 0:
        growth_rate = (latest_fcf / first_fcf) ** (1 / years) - 1
    else:
        growth_rate = 0.05  # Default 5%

    # Cap growth rate
    growth_rate = min(growth_rate, 0.25)  # Max 25%
    growth_rate = max(growth_rate, -0.05)  # Min -5%

    # Determine discount rate (WACC proxy)
    latest_stmt = statements[0]
    wacc = 0.10  # Base 10%

    # Adjust for leverage
    equity = latest_stmt.get("stockholders_equity") or 1
    debt = latest_stmt.get("long_term_debt") or latest_stmt.get("total_debt") or 0
    if equity > 0:
        de_ratio = debt / equity
        if de_ratio > 2:
            wacc += 0.02
        elif de_ratio > 1:
            wacc += 0.01

    # Adjust for size
    if market_cap:
        if market_cap < 2_000_000_000:  # Small cap
            wacc += 0.02
        elif market_cap < 10_000_000_000:  # Mid cap
            wacc += 0.01
        elif market_cap > 200_000_000_000:  # Mega cap
            wacc -= 0.01

    terminal_growth = 0.025  # 2.5%

    # Project FCF for 10 years
    projections = []
    current_growth = growth_rate
    growth_decay = 0.10  # Growth declines 10% per year toward terminal

    for year in range(1, 11):
        projected_fcf = latest_fcf * (1 + current_growth) ** year
        discount_factor = (1 + wacc) ** year
        pv = projected_fcf / discount_factor

        projections.append({
            "year": year,
            "projected_fcf": round(projected_fcf),
            "growth_rate": round(current_growth * 100, 2),
            "discount_factor": round(discount_factor, 4),
            "present_value": round(pv),
        })

        # Decay growth toward terminal rate
        current_growth = current_growth - (current_growth - terminal_growth) * growth_decay

    # Terminal value (Gordon Growth Model)
    terminal_fcf = projections[-1]["projected_fcf"] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)
    terminal_pv = terminal_value / (1 + wacc) ** 10

    # Sum of present values
    sum_pv_fcf = sum(p["present_value"] for p in projections)
    enterprise_value = sum_pv_fcf + terminal_pv

    # Subtract net debt
    cash = latest_stmt.get("cash_and_equivalents") or 0
    net_debt = debt - cash
    equity_value = enterprise_value - net_debt

    # Per share value
    shares = shares_outstanding or latest_stmt.get("shares_outstanding") or latest_stmt.get("shares_diluted")
    if not shares or shares == 0:
        return {"error": "No shares outstanding data available"}

    intrinsic_value = equity_value / shares

    # Upside/downside
    upside = None
    if current_price and current_price > 0:
        upside = round((intrinsic_value / current_price - 1) * 100, 2)

    return {
        "intrinsic_value_per_share": round(intrinsic_value, 2),
        "current_price": current_price,
        "upside_percent": upside,
        "verdict": _get_verdict(upside) if upside is not None else "N/A",
        "enterprise_value": round(enterprise_value),
        "equity_value": round(equity_value),
        "assumptions": {
            "initial_growth_rate": round(growth_rate * 100, 2),
            "terminal_growth_rate": round(terminal_growth * 100, 2),
            "discount_rate_wacc": round(wacc * 100, 2),
            "projection_years": 10,
            "latest_fcf": latest_fcf,
            "net_debt": round(net_debt),
            "shares_outstanding": shares,
        },
        "projections": projections,
        "terminal_value": round(terminal_value),
        "terminal_pv": round(terminal_pv),
        "sum_pv_fcf": round(sum_pv_fcf),
    }


def _get_verdict(upside: float) -> str:
    if upside > 30:
        return "SIGNIFICANTLY UNDERVALUED"
    elif upside > 15:
        return "UNDERVALUED"
    elif upside > 0:
        return "SLIGHTLY UNDERVALUED"
    elif upside > -15:
        return "FAIRLY VALUED"
    elif upside > -30:
        return "OVERVALUED"
    else:
        return "SIGNIFICANTLY OVERVALUED"
