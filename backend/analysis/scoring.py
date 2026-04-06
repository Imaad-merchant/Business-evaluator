from typing import Optional


def calculate_investment_score(
    ratios: dict,
    dcf: dict,
    debt: dict,
    burn_rate: dict,
    sentiment: dict,
    insider_data: dict,
    comps: dict,
) -> dict:
    scores = {}

    # 1. Profitability (25%)
    prof = ratios.get("profitability", {})
    prof_score = 50  # Base

    net_margin = prof.get("net_margin")
    if net_margin is not None:
        if net_margin > 20:
            prof_score = 90
        elif net_margin > 10:
            prof_score = 75
        elif net_margin > 5:
            prof_score = 60
        elif net_margin > 0:
            prof_score = 45
        else:
            prof_score = 20

    roe = prof.get("roe")
    if roe is not None:
        if roe > 20:
            prof_score = min(100, prof_score + 10)
        elif roe > 10:
            prof_score = min(100, prof_score + 5)
        elif roe < 0:
            prof_score = max(0, prof_score - 15)

    scores["profitability"] = {"score": prof_score, "weight": 0.25}

    # 2. Growth (25%)
    growth = ratios.get("growth", {})
    growth_score = 50

    rev_growth = growth.get("revenue_growth")
    if rev_growth is not None:
        if rev_growth > 30:
            growth_score = 95
        elif rev_growth > 15:
            growth_score = 80
        elif rev_growth > 5:
            growth_score = 65
        elif rev_growth > 0:
            growth_score = 50
        elif rev_growth > -10:
            growth_score = 35
        else:
            growth_score = 15

    ni_growth = growth.get("net_income_growth")
    if ni_growth is not None:
        if ni_growth > 20:
            growth_score = min(100, growth_score + 10)
        elif ni_growth < -20:
            growth_score = max(0, growth_score - 10)

    scores["growth"] = {"score": growth_score, "weight": 0.25}

    # 3. Valuation (20%)
    val_score = 50

    dcf_upside = dcf.get("upside_percent")
    if dcf_upside is not None:
        if dcf_upside > 30:
            val_score = 90
        elif dcf_upside > 15:
            val_score = 75
        elif dcf_upside > 0:
            val_score = 60
        elif dcf_upside > -15:
            val_score = 45
        elif dcf_upside > -30:
            val_score = 30
        else:
            val_score = 15

    comps_premium = comps.get("premium_discount_percent")
    if comps_premium is not None:
        if comps_premium < -20:
            val_score = min(100, val_score + 10)
        elif comps_premium > 30:
            val_score = max(0, val_score - 10)

    scores["valuation"] = {"score": val_score, "weight": 0.20}

    # 4. Financial Health (20%)
    health_score = 50

    debt_risk = debt.get("risk_level", "MODERATE")
    if debt_risk == "LOW":
        health_score = 85
    elif debt_risk == "MODERATE":
        health_score = 60
    elif debt_risk == "HIGH":
        health_score = 35
    elif debt_risk == "CRITICAL":
        health_score = 15

    liq = ratios.get("liquidity", {})
    current_ratio = liq.get("current_ratio")
    if current_ratio is not None:
        if current_ratio > 2:
            health_score = min(100, health_score + 10)
        elif current_ratio < 1:
            health_score = max(0, health_score - 15)

    # Burn rate impact
    if burn_rate.get("is_burning_cash"):
        runway = burn_rate.get("runway_months")
        if runway is not None and runway < 12:
            health_score = max(0, health_score - 20)
        elif runway is not None and runway < 24:
            health_score = max(0, health_score - 10)

    scores["financial_health"] = {"score": health_score, "weight": 0.20}

    # 5. Momentum (10%)
    momentum_score = 50

    sent_score = sentiment.get("overall_score", 0)
    if sent_score > 0.3:
        momentum_score = 80
    elif sent_score > 0.1:
        momentum_score = 65
    elif sent_score < -0.3:
        momentum_score = 20
    elif sent_score < -0.1:
        momentum_score = 35

    # Insider buying is bullish
    cluster = insider_data.get("cluster_buys", {})
    if cluster.get("detected"):
        momentum_score = min(100, momentum_score + 15)

    scores["momentum"] = {"score": momentum_score, "weight": 0.10}

    # Calculate weighted total
    total = sum(s["score"] * s["weight"] for s in scores.values())
    total = round(total)

    grade = _score_to_grade(total)
    bull_case = _generate_bull_case(ratios, dcf, debt, sentiment, insider_data)
    bear_case = _generate_bear_case(ratios, dcf, debt, burn_rate, sentiment)

    return {
        "overall_score": total,
        "grade": grade,
        "components": scores,
        "bull_case": bull_case,
        "bear_case": bear_case,
    }


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    elif score >= 45:
        return "D+"
    elif score >= 40:
        return "D"
    elif score >= 35:
        return "D-"
    else:
        return "F"


def _generate_bull_case(ratios, dcf, debt, sentiment, insider_data) -> list[str]:
    points = []

    prof = ratios.get("profitability", {})
    if prof.get("net_margin", 0) > 15:
        points.append(f"Strong profitability with {prof['net_margin']}% net margin")
    if prof.get("roe", 0) > 15:
        points.append(f"High return on equity at {prof['roe']}%")

    growth = ratios.get("growth", {})
    if growth.get("revenue_growth", 0) > 10:
        points.append(f"Revenue growing at {growth['revenue_growth']}% YoY")

    if dcf.get("upside_percent", 0) > 15:
        points.append(f"DCF suggests {dcf['upside_percent']}% upside potential")

    if debt.get("risk_level") == "LOW":
        points.append("Conservative balance sheet with low debt risk")

    if sentiment.get("overall_label") == "positive":
        points.append("Positive market sentiment and news flow")

    cluster = insider_data.get("cluster_buys", {})
    if cluster.get("detected"):
        points.append("Multiple insiders buying — strong confidence signal")

    if not points:
        points.append("Limited positive catalysts identified")

    return points[:5]


def _generate_bear_case(ratios, dcf, debt, burn_rate, sentiment) -> list[str]:
    points = []

    prof = ratios.get("profitability", {})
    if prof.get("net_margin", 0) < 0:
        points.append(f"Company is unprofitable with {prof['net_margin']}% net margin")

    growth = ratios.get("growth", {})
    if growth.get("revenue_growth", 0) < -5:
        points.append(f"Revenue declining at {growth['revenue_growth']}% YoY")

    if dcf.get("upside_percent", 0) < -15:
        points.append(f"DCF suggests {abs(dcf['upside_percent'])}% overvaluation")

    if debt.get("risk_level") in ("HIGH", "CRITICAL"):
        points.append(f"Debt risk is {debt['risk_level'].lower()} — watch leverage ratios")

    if burn_rate.get("is_burning_cash") and burn_rate.get("runway_months", 100) < 18:
        points.append(f"Burning cash with only {burn_rate['runway_months']:.0f} months of runway")

    if sentiment.get("overall_label") == "negative":
        points.append("Negative market sentiment — potential headwinds")

    if not points:
        points.append("No major risks identified")

    return points[:5]
