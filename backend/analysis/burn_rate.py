from typing import Optional


def calculate_burn_rate(statements: list[dict]) -> dict:
    if not statements:
        return {"error": "No financial data available"}

    latest = statements[0]

    cash = latest.get("cash_and_equivalents") or 0
    short_investments = latest.get("short_term_investments") or 0
    total_cash = cash + short_investments

    operating_cf = latest.get("operating_cash_flow")
    net_income = latest.get("net_income")
    fcf = latest.get("free_cash_flow")

    # Calculate quarterly burn rate
    # Positive operating_cf means the company generates cash
    # Negative means it burns cash
    if operating_cf is not None:
        quarterly_burn = -operating_cf / 4 if operating_cf < 0 else 0
        monthly_burn = -operating_cf / 12 if operating_cf < 0 else 0
        annual_burn = -operating_cf if operating_cf < 0 else 0
    elif net_income is not None:
        quarterly_burn = -net_income / 4 if net_income < 0 else 0
        monthly_burn = -net_income / 12 if net_income < 0 else 0
        annual_burn = -net_income if net_income < 0 else 0
    else:
        return {
            "error": "Insufficient data to calculate burn rate",
            "total_cash": total_cash,
        }

    # Calculate runway
    if monthly_burn > 0:
        runway_months = total_cash / monthly_burn
    else:
        runway_months = float("inf")  # Company is profitable

    # Cash trend over years
    cash_trend = []
    for s in statements:
        year_cash = (s.get("cash_and_equivalents") or 0) + (s.get("short_term_investments") or 0)
        cash_trend.append({
            "year": s.get("fiscal_year"),
            "cash": year_cash,
            "operating_cf": s.get("operating_cash_flow"),
            "fcf": s.get("free_cash_flow"),
        })

    # Determine health level
    if runway_months == float("inf"):
        health = "PROFITABLE"
        health_color = "green"
    elif runway_months > 24:
        health = "HEALTHY"
        health_color = "green"
    elif runway_months > 12:
        health = "ADEQUATE"
        health_color = "yellow"
    elif runway_months > 6:
        health = "WARNING"
        health_color = "orange"
    else:
        health = "CRITICAL"
        health_color = "red"

    is_burning = monthly_burn > 0

    return {
        "is_burning_cash": is_burning,
        "total_cash": total_cash,
        "monthly_burn_rate": round(monthly_burn) if is_burning else 0,
        "quarterly_burn_rate": round(quarterly_burn) if is_burning else 0,
        "annual_burn_rate": round(annual_burn) if is_burning else 0,
        "runway_months": round(runway_months, 1) if runway_months != float("inf") else None,
        "runway_years": round(runway_months / 12, 1) if runway_months != float("inf") and is_burning else None,
        "health": health,
        "health_color": health_color,
        "cash_trend": cash_trend,
        "revenue": latest.get("revenue"),
        "operating_cash_flow": operating_cf,
        "net_income": net_income,
        "note": _generate_note(health, runway_months, is_burning, total_cash),
    }


def _generate_note(health: str, runway_months: float, is_burning: bool, total_cash: int) -> str:
    if not is_burning:
        return "Company is cash flow positive and not burning cash."

    cash_str = f"${total_cash / 1_000_000:,.0f}M" if total_cash > 1_000_000 else f"${total_cash:,}"

    if health == "CRITICAL":
        return f"CRITICAL: At current burn rate, the company has approximately {runway_months:.0f} months of runway ({cash_str} in cash). May need to raise capital imminently."
    elif health == "WARNING":
        return f"WARNING: Company has {runway_months:.0f} months of runway ({cash_str} in cash). Should be actively seeking funding or path to profitability."
    elif health == "ADEQUATE":
        return f"Company has approximately {runway_months:.0f} months of runway ({cash_str} in cash). Position is adequate but should monitor burn rate."
    else:
        return f"Company has {runway_months:.0f} months of runway ({cash_str} in cash). Healthy cash position."
