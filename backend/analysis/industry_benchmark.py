# Static industry benchmarks by SIC code group
# These are approximate medians for major industry groups

BENCHMARKS = {
    "73": {  # Computer Programming, Data Processing
        "industry_name": "Technology / Software",
        "median_gross_margin": 65.0,
        "median_operating_margin": 20.0,
        "median_net_margin": 15.0,
        "median_roe": 20.0,
        "median_roa": 10.0,
        "median_current_ratio": 2.5,
        "median_debt_to_equity": 0.5,
        "median_pe_ratio": 30.0,
        "median_ev_revenue": 8.0,
        "median_ev_ebitda": 25.0,
        "median_revenue_growth": 15.0,
    },
    "37": {  # Transportation Equipment (Auto)
        "industry_name": "Automotive / Transportation",
        "median_gross_margin": 20.0,
        "median_operating_margin": 6.0,
        "median_net_margin": 4.0,
        "median_roe": 12.0,
        "median_roa": 4.0,
        "median_current_ratio": 1.2,
        "median_debt_to_equity": 1.5,
        "median_pe_ratio": 12.0,
        "median_ev_revenue": 1.0,
        "median_ev_ebitda": 8.0,
        "median_revenue_growth": 5.0,
    },
    "28": {  # Chemicals and Allied Products (Pharma)
        "industry_name": "Pharmaceuticals / Biotech",
        "median_gross_margin": 70.0,
        "median_operating_margin": 15.0,
        "median_net_margin": 12.0,
        "median_roe": 18.0,
        "median_roa": 8.0,
        "median_current_ratio": 2.0,
        "median_debt_to_equity": 0.8,
        "median_pe_ratio": 20.0,
        "median_ev_revenue": 5.0,
        "median_ev_ebitda": 15.0,
        "median_revenue_growth": 8.0,
    },
    "60": {  # Depository Institutions (Banks)
        "industry_name": "Banking / Financial Services",
        "median_gross_margin": None,
        "median_operating_margin": 30.0,
        "median_net_margin": 25.0,
        "median_roe": 10.0,
        "median_roa": 1.0,
        "median_current_ratio": None,
        "median_debt_to_equity": 8.0,
        "median_pe_ratio": 12.0,
        "median_ev_revenue": 3.0,
        "median_ev_ebitda": None,
        "median_revenue_growth": 5.0,
    },
    "53": {  # General Merchandise Stores (Retail)
        "industry_name": "Retail",
        "median_gross_margin": 30.0,
        "median_operating_margin": 5.0,
        "median_net_margin": 3.0,
        "median_roe": 15.0,
        "median_roa": 6.0,
        "median_current_ratio": 1.5,
        "median_debt_to_equity": 1.0,
        "median_pe_ratio": 18.0,
        "median_ev_revenue": 1.5,
        "median_ev_ebitda": 12.0,
        "median_revenue_growth": 5.0,
    },
    "36": {  # Electronic Components (Semiconductors)
        "industry_name": "Semiconductors / Electronics",
        "median_gross_margin": 50.0,
        "median_operating_margin": 20.0,
        "median_net_margin": 18.0,
        "median_roe": 20.0,
        "median_roa": 12.0,
        "median_current_ratio": 3.0,
        "median_debt_to_equity": 0.4,
        "median_pe_ratio": 25.0,
        "median_ev_revenue": 7.0,
        "median_ev_ebitda": 20.0,
        "median_revenue_growth": 10.0,
    },
    "48": {  # Communications
        "industry_name": "Telecommunications",
        "median_gross_margin": 55.0,
        "median_operating_margin": 15.0,
        "median_net_margin": 10.0,
        "median_roe": 12.0,
        "median_roa": 5.0,
        "median_current_ratio": 1.0,
        "median_debt_to_equity": 1.5,
        "median_pe_ratio": 15.0,
        "median_ev_revenue": 3.0,
        "median_ev_ebitda": 10.0,
        "median_revenue_growth": 3.0,
    },
    "13": {  # Oil and Gas Extraction
        "industry_name": "Oil & Gas / Energy",
        "median_gross_margin": 45.0,
        "median_operating_margin": 15.0,
        "median_net_margin": 10.0,
        "median_roe": 12.0,
        "median_roa": 6.0,
        "median_current_ratio": 1.5,
        "median_debt_to_equity": 0.8,
        "median_pe_ratio": 10.0,
        "median_ev_revenue": 2.0,
        "median_ev_ebitda": 6.0,
        "median_revenue_growth": 5.0,
    },
    "default": {
        "industry_name": "All Industries Average",
        "median_gross_margin": 40.0,
        "median_operating_margin": 12.0,
        "median_net_margin": 8.0,
        "median_roe": 14.0,
        "median_roa": 6.0,
        "median_current_ratio": 1.8,
        "median_debt_to_equity": 1.0,
        "median_pe_ratio": 18.0,
        "median_ev_revenue": 3.0,
        "median_ev_ebitda": 12.0,
        "median_revenue_growth": 7.0,
    },
}


def get_benchmark(sic_code: str) -> dict:
    # Match by 2-digit SIC prefix
    prefix = sic_code[:2] if sic_code else ""
    return BENCHMARKS.get(prefix, BENCHMARKS["default"])


def compare_to_industry(ratios: dict, sic_code: str) -> dict:
    benchmark = get_benchmark(sic_code)
    comparison = {"industry": benchmark["industry_name"], "metrics": []}

    prof = ratios.get("profitability", {})
    val = ratios.get("valuation", {})
    lev = ratios.get("leverage", {})
    liq = ratios.get("liquidity", {})
    growth = ratios.get("growth", {})

    metrics = [
        ("Gross Margin", prof.get("gross_margin"), benchmark.get("median_gross_margin"), "%", True),
        ("Operating Margin", prof.get("operating_margin"), benchmark.get("median_operating_margin"), "%", True),
        ("Net Margin", prof.get("net_margin"), benchmark.get("median_net_margin"), "%", True),
        ("ROE", prof.get("roe"), benchmark.get("median_roe"), "%", True),
        ("ROA", prof.get("roa"), benchmark.get("median_roa"), "%", True),
        ("Current Ratio", liq.get("current_ratio"), benchmark.get("median_current_ratio"), "x", True),
        ("Debt/Equity", lev.get("debt_to_equity"), benchmark.get("median_debt_to_equity"), "x", False),
        ("P/E Ratio", val.get("pe_ratio"), benchmark.get("median_pe_ratio"), "x", False),
        ("EV/Revenue", val.get("ev_to_revenue"), benchmark.get("median_ev_revenue"), "x", False),
        ("EV/EBITDA", val.get("ev_to_ebitda"), benchmark.get("median_ev_ebitda"), "x", False),
        ("Revenue Growth", growth.get("revenue_growth"), benchmark.get("median_revenue_growth"), "%", True),
    ]

    for name, company_val, industry_val, unit, higher_is_better in metrics:
        if company_val is None or industry_val is None:
            continue

        diff = company_val - industry_val
        if higher_is_better:
            status = "above" if diff > 0 else "below" if diff < 0 else "inline"
        else:
            status = "below" if diff > 0 else "above" if diff < 0 else "inline"

        comparison["metrics"].append({
            "name": name,
            "company_value": company_val,
            "industry_median": industry_val,
            "difference": round(diff, 2),
            "unit": unit,
            "status": status,
            "higher_is_better": higher_is_better,
        })

    # Overall comparison
    above = sum(1 for m in comparison["metrics"] if m["status"] == "above")
    below = sum(1 for m in comparison["metrics"] if m["status"] == "below")
    total = len(comparison["metrics"])

    if total > 0:
        comparison["summary"] = {
            "above_average_count": above,
            "below_average_count": below,
            "total_metrics": total,
            "overall": "ABOVE AVERAGE" if above > below else "BELOW AVERAGE" if below > above else "AVERAGE",
        }

    return comparison
