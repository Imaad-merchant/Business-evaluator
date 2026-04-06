from fastapi import APIRouter, Query
import httpx
from services.edgar import resolve_ticker, get_company_facts
from services.xbrl_parser import parse_financial_statements
from analysis.financial_ratios import calculate_ratios

router = APIRouter()


@router.get("/financials/{ticker}")
async def get_financials(ticker: str, years: int = Query(5, le=10)):
    async with httpx.AsyncClient() as client:
        cik = await resolve_ticker(ticker, client)
        if not cik:
            return {"error": f"Ticker '{ticker}' not found"}

        facts = await get_company_facts(cik, client)
        if not facts:
            return {"error": "Failed to fetch financial data from SEC EDGAR"}

        statements = parse_financial_statements(facts, num_years=years)
        if not statements:
            return {"error": "No financial statements found in XBRL data"}

        ratios = calculate_ratios(statements)

        return {
            "ticker": ticker.upper(),
            "cik": cik,
            "statements": statements,
            "ratios": ratios,
            "years_available": len(statements),
        }
