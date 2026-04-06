def analyze_debt(statements: list[dict]) -> dict:
    if not statements:
        return {"error": "No financial data available"}

    latest = statements[0]

    total_debt = latest.get("total_debt") or latest.get("long_term_debt") or 0
    long_term_debt = latest.get("long_term_debt") or 0
    cash = latest.get("cash_and_equivalents") or 0
    net_debt = total_debt - cash
    equity = latest.get("stockholders_equity") or 0
    ebitda = latest.get("ebitda") or 0
    operating_income = latest.get("operating_income") or 0
    interest_expense = abs(latest.get("interest_expense") or 0)
    total_assets = latest.get("total_assets") or 0

    # Ratios
    de_ratio = round(total_debt / equity, 2) if equity and equity != 0 else None
    debt_to_assets = round(total_debt / total_assets, 2) if total_assets and total_assets != 0 else None
    interest_coverage = round(operating_income / interest_expense, 2) if interest_expense and interest_expense != 0 else None
    net_debt_to_ebitda = round(net_debt / ebitda, 2) if ebitda and ebitda != 0 else None

    # Debt trend
    debt_trend = []
    for s in statements:
        d = s.get("total_debt") or s.get("long_term_debt") or 0
        c = s.get("cash_and_equivalents") or 0
        debt_trend.append({
            "year": s.get("fiscal_year"),
            "total_debt": d,
            "cash": c,
            "net_debt": d - c,
        })

    # Risk assessment
    risk_level, risk_factors = _assess_risk(de_ratio, interest_coverage, net_debt_to_ebitda, debt_to_assets)

    return {
        "total_debt": total_debt,
        "long_term_debt": long_term_debt,
        "cash_and_equivalents": cash,
        "net_debt": net_debt,
        "stockholders_equity": equity,
        "ratios": {
            "debt_to_equity": de_ratio,
            "debt_to_assets": debt_to_assets,
            "interest_coverage": interest_coverage,
            "net_debt_to_ebitda": net_debt_to_ebitda,
        },
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "debt_trend": debt_trend,
    }


def _assess_risk(
    de_ratio, interest_coverage, net_debt_to_ebitda, debt_to_assets
) -> tuple[str, list[str]]:
    risk_score = 0
    factors = []

    if de_ratio is not None:
        if de_ratio > 3:
            risk_score += 3
            factors.append(f"High debt-to-equity ratio ({de_ratio}x)")
        elif de_ratio > 1.5:
            risk_score += 2
            factors.append(f"Elevated debt-to-equity ratio ({de_ratio}x)")
        elif de_ratio > 0.5:
            risk_score += 1
        else:
            factors.append(f"Conservative debt-to-equity ratio ({de_ratio}x)")

    if interest_coverage is not None:
        if interest_coverage < 1.5:
            risk_score += 3
            factors.append(f"Dangerously low interest coverage ({interest_coverage}x)")
        elif interest_coverage < 3:
            risk_score += 2
            factors.append(f"Low interest coverage ({interest_coverage}x)")
        elif interest_coverage > 10:
            factors.append(f"Strong interest coverage ({interest_coverage}x)")

    if net_debt_to_ebitda is not None:
        if net_debt_to_ebitda > 5:
            risk_score += 3
            factors.append(f"Very high net debt to EBITDA ({net_debt_to_ebitda}x)")
        elif net_debt_to_ebitda > 3:
            risk_score += 2
            factors.append(f"Elevated net debt to EBITDA ({net_debt_to_ebitda}x)")
        elif net_debt_to_ebitda < 0:
            factors.append("Net cash position (no net debt)")

    if risk_score >= 6:
        return "CRITICAL", factors
    elif risk_score >= 4:
        return "HIGH", factors
    elif risk_score >= 2:
        return "MODERATE", factors
    else:
        return "LOW", factors
