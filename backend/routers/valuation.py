from fastapi import APIRouter
import httpx
from services.edgar import resolve_ticker, get_company_facts, get_company_submissions, extract_company_info
from services.xbrl_parser import parse_financial_statements
from services.yahoo_finance import get_stock_price, get_quote_summary
from analysis.dcf_model import calculate_dcf
from analysis.comps_analysis import run_comps_analysis

router = APIRouter()


@router.get("/valuation/{ticker}")
async def get_valuation(ticker: str):
    async with httpx.AsyncClient() as client:
        cik = await resolve_ticker(ticker, client)
        if not cik:
            return {"error": f"Ticker '{ticker}' not found"}

        # Fetch data in parallel
        import asyncio
        facts_task = get_company_facts(cik, client)
        submissions_task = get_company_submissions(cik, client)
        price_task = get_stock_price(ticker, client)
        quote_task = get_quote_summary(ticker, client)

        facts, submissions, price_data, quote_data = await asyncio.gather(
            facts_task, submissions_task, price_task, quote_task
        )

        if not facts:
            return {"error": "Failed to fetch financial data"}

        statements = parse_financial_statements(facts, num_years=5)
        if not statements:
            return {"error": "No financial statements found"}

        # Get stock info
        current_price = None
        market_cap = None
        shares = statements[0].get("shares_outstanding") or statements[0].get("shares_diluted")

        if price_data:
            current_price = price_data.get("current_price")
        if quote_data:
            market_cap = quote_data.get("market_cap")

        # DCF Valuation
        dcf = calculate_dcf(
            statements=statements,
            current_price=current_price,
            shares_outstanding=shares,
            market_cap=market_cap,
        )

        # Comps Analysis
        company_info = extract_company_info(submissions) if submissions else {}
        sic_code = company_info.get("sic_code", "")

        stock_data = {"current_price": current_price, "market_cap": market_cap}
        comps = await run_comps_analysis(
            ticker=ticker.upper(),
            target_financials=statements[0],
            target_stock=stock_data,
            sic_code=sic_code,
            client=client,
        )

        return {
            "ticker": ticker.upper(),
            "dcf": dcf,
            "comps": comps,
            "current_price": current_price,
            "market_cap": market_cap,
        }
