from typing import Optional

# XBRL tag fallback lists for each financial concept.
# Different companies use different tags for the same line item.
REVENUE_TAGS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
    "SalesRevenueServicesNet",
    "TotalRevenuesAndOtherIncome",
    "InterestAndDividendIncomeOperating",
    "RegulatedAndUnregulatedOperatingRevenue",
]

COST_OF_REVENUE_TAGS = [
    "CostOfRevenue",
    "CostOfGoodsAndServicesSold",
    "CostOfGoodsSold",
    "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
]

GROSS_PROFIT_TAGS = ["GrossProfit"]

OPERATING_INCOME_TAGS = [
    "OperatingIncomeLoss",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
]

OPERATING_EXPENSES_TAGS = [
    "OperatingExpenses",
    "CostsAndExpenses",
    "SellingGeneralAndAdministrativeExpense",
]

NET_INCOME_TAGS = [
    "NetIncomeLoss",
    "ProfitLoss",
    "NetIncomeLossAvailableToCommonStockholdersBasic",
    "IncomeLossFromContinuingOperations",
]

INTEREST_EXPENSE_TAGS = [
    "InterestExpense",
    "InterestExpenseDebt",
    "InterestPaid",
]

INCOME_TAX_TAGS = [
    "IncomeTaxExpenseBenefit",
    "IncomeTaxesPaidNet",
]

EPS_BASIC_TAGS = [
    "EarningsPerShareBasic",
]

EPS_DILUTED_TAGS = [
    "EarningsPerShareDiluted",
]

SHARES_OUTSTANDING_TAGS = [
    "CommonStockSharesOutstanding",
    "WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
    "EntityCommonStockSharesOutstanding",
    "WeightedAverageNumberOfSharesOutstandingBasic",
]

SHARES_DILUTED_TAGS = [
    "WeightedAverageNumberOfDilutedSharesOutstanding",
]

# Balance Sheet
CASH_TAGS = [
    "CashAndCashEquivalentsAtCarryingValue",
    "CashCashEquivalentsAndShortTermInvestments",
    "Cash",
]

SHORT_TERM_INVESTMENTS_TAGS = [
    "ShortTermInvestments",
    "MarketableSecuritiesCurrent",
    "AvailableForSaleSecuritiesDebtSecuritiesCurrent",
]

TOTAL_CURRENT_ASSETS_TAGS = ["AssetsCurrent"]

TOTAL_ASSETS_TAGS = ["Assets"]

TOTAL_CURRENT_LIABILITIES_TAGS = ["LiabilitiesCurrent"]

LONG_TERM_DEBT_TAGS = [
    "LongTermDebt",
    "LongTermDebtNoncurrent",
    "LongTermDebtAndCapitalLeaseObligations",
]

TOTAL_LIABILITIES_TAGS = ["Liabilities", "LiabilitiesAndStockholdersEquity"]

STOCKHOLDERS_EQUITY_TAGS = [
    "StockholdersEquity",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
]

TOTAL_DEBT_TAGS = [
    "DebtCurrent",
    "LongTermDebt",
]

# Cash Flow
OPERATING_CF_TAGS = [
    "NetCashProvidedByUsedInOperatingActivities",
    "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
]

CAPEX_TAGS = [
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsForCapitalImprovements",
    "CapitalExpendituresIncurredButNotYetPaid",
]

INVESTING_CF_TAGS = [
    "NetCashProvidedByUsedInInvestingActivities",
    "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
]

FINANCING_CF_TAGS = [
    "NetCashProvidedByUsedInFinancingActivities",
    "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
]

DEPRECIATION_TAGS = [
    "DepreciationDepletionAndAmortization",
    "DepreciationAndAmortization",
    "Depreciation",
]


def _extract_concept_value(
    facts: dict, tags: list[str], fiscal_period: str = "FY", year: Optional[int] = None
) -> Optional[int | float]:
    us_gaap = facts.get("facts", {}).get("us-gaap", {})

    for tag in tags:
        concept = us_gaap.get(tag, {})
        units = concept.get("units", {})

        # Try USD first, then USD/shares for EPS
        unit_data = units.get("USD") or units.get("USD/shares") or units.get("shares")
        if not unit_data:
            continue

        # Filter for the right period
        candidates = []
        for entry in unit_data:
            fp = entry.get("fp", "")
            form = entry.get("form", "")
            fy = entry.get("fy")

            if fiscal_period == "FY" and fp == "FY" and form in ("10-K", "10-K/A"):
                if year is None or fy == year:
                    candidates.append(entry)
            elif fiscal_period.startswith("Q") and fp == fiscal_period and form in ("10-Q", "10-Q/A"):
                if year is None or fy == year:
                    candidates.append(entry)

        if candidates:
            # Return most recent
            candidates.sort(key=lambda x: x.get("end", ""), reverse=True)
            return candidates[0].get("val")

    return None


def _get_all_annual_values(facts: dict, tags: list[str], num_years: int = 10) -> list[dict]:
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    results = {}

    for tag in tags:
        concept = us_gaap.get(tag, {})
        units = concept.get("units", {})
        unit_data = units.get("USD") or units.get("USD/shares") or units.get("shares")
        if not unit_data:
            continue

        for entry in unit_data:
            fp = entry.get("fp", "")
            form = entry.get("form", "")
            fy = entry.get("fy")

            if fp == "FY" and form in ("10-K", "10-K/A") and fy:
                if fy not in results:
                    results[fy] = {
                        "year": fy,
                        "value": entry.get("val"),
                        "end_date": entry.get("end", ""),
                        "filed": entry.get("filed", ""),
                    }
        if results:
            break  # Use first matching tag

    sorted_results = sorted(results.values(), key=lambda x: x["year"], reverse=True)
    return sorted_results[:num_years]


def parse_financial_statements(facts: dict, num_years: int = 5) -> list[dict]:
    statements = []

    revenue_history = _get_all_annual_values(facts, REVENUE_TAGS, num_years)
    years = [r["year"] for r in revenue_history]

    if not years:
        # Try to find any years from net income
        ni_history = _get_all_annual_values(facts, NET_INCOME_TAGS, num_years)
        years = [r["year"] for r in ni_history]

    for year in years:
        revenue = _extract_concept_value(facts, REVENUE_TAGS, "FY", year)
        cost_of_revenue = _extract_concept_value(facts, COST_OF_REVENUE_TAGS, "FY", year)
        gross_profit = _extract_concept_value(facts, GROSS_PROFIT_TAGS, "FY", year)
        operating_income = _extract_concept_value(facts, OPERATING_INCOME_TAGS, "FY", year)
        operating_expenses = _extract_concept_value(facts, OPERATING_EXPENSES_TAGS, "FY", year)
        net_income = _extract_concept_value(facts, NET_INCOME_TAGS, "FY", year)
        interest_expense = _extract_concept_value(facts, INTEREST_EXPENSE_TAGS, "FY", year)
        income_tax = _extract_concept_value(facts, INCOME_TAX_TAGS, "FY", year)
        eps_basic = _extract_concept_value(facts, EPS_BASIC_TAGS, "FY", year)
        eps_diluted = _extract_concept_value(facts, EPS_DILUTED_TAGS, "FY", year)
        shares = _extract_concept_value(facts, SHARES_OUTSTANDING_TAGS, "FY", year)
        shares_diluted = _extract_concept_value(facts, SHARES_DILUTED_TAGS, "FY", year)

        # Balance Sheet
        cash = _extract_concept_value(facts, CASH_TAGS, "FY", year)
        short_investments = _extract_concept_value(facts, SHORT_TERM_INVESTMENTS_TAGS, "FY", year)
        current_assets = _extract_concept_value(facts, TOTAL_CURRENT_ASSETS_TAGS, "FY", year)
        total_assets = _extract_concept_value(facts, TOTAL_ASSETS_TAGS, "FY", year)
        current_liabilities = _extract_concept_value(facts, TOTAL_CURRENT_LIABILITIES_TAGS, "FY", year)
        long_term_debt = _extract_concept_value(facts, LONG_TERM_DEBT_TAGS, "FY", year)
        total_liabilities = _extract_concept_value(facts, TOTAL_LIABILITIES_TAGS, "FY", year)
        equity = _extract_concept_value(facts, STOCKHOLDERS_EQUITY_TAGS, "FY", year)

        # Cash Flow
        operating_cf = _extract_concept_value(facts, OPERATING_CF_TAGS, "FY", year)
        capex = _extract_concept_value(facts, CAPEX_TAGS, "FY", year)
        investing_cf = _extract_concept_value(facts, INVESTING_CF_TAGS, "FY", year)
        financing_cf = _extract_concept_value(facts, FINANCING_CF_TAGS, "FY", year)
        dep_amort = _extract_concept_value(facts, DEPRECIATION_TAGS, "FY", year)

        # Computed fields
        if gross_profit is None and revenue and cost_of_revenue:
            gross_profit = revenue - cost_of_revenue

        ebitda = None
        if operating_income is not None and dep_amort is not None:
            ebitda = operating_income + dep_amort
        elif net_income is not None and interest_expense and income_tax and dep_amort:
            ebitda = net_income + (interest_expense or 0) + (income_tax or 0) + dep_amort

        fcf = None
        if operating_cf is not None and capex is not None:
            fcf = operating_cf - abs(capex)

        total_debt = None
        if long_term_debt is not None:
            total_debt = long_term_debt + (current_liabilities or 0)  # Rough approximation

        statements.append({
            "fiscal_year": year,
            "fiscal_period": "FY",
            "revenue": revenue,
            "cost_of_revenue": cost_of_revenue,
            "gross_profit": gross_profit,
            "operating_expenses": operating_expenses,
            "operating_income": operating_income,
            "interest_expense": interest_expense,
            "income_tax": income_tax,
            "net_income": net_income,
            "ebitda": ebitda,
            "eps_basic": eps_basic,
            "eps_diluted": eps_diluted,
            "shares_outstanding": shares,
            "shares_diluted": shares_diluted,
            "cash_and_equivalents": cash,
            "short_term_investments": short_investments,
            "total_current_assets": current_assets,
            "total_assets": total_assets,
            "total_current_liabilities": current_liabilities,
            "long_term_debt": long_term_debt,
            "total_liabilities": total_liabilities,
            "stockholders_equity": equity,
            "total_debt": total_debt,
            "operating_cash_flow": operating_cf,
            "capital_expenditures": capex,
            "free_cash_flow": fcf,
            "investing_cash_flow": investing_cf,
            "financing_cash_flow": financing_cf,
            "depreciation_amortization": dep_amort,
        })

    return statements
