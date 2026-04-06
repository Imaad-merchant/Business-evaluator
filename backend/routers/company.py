import asyncio
from fastapi import APIRouter
import httpx
from services.edgar import resolve_ticker, get_company_submissions, get_company_facts, extract_company_info, extract_recent_filings
from services.xbrl_parser import parse_financial_statements
from services.yahoo_finance import get_stock_price, get_quote_summary, get_stock_history
from services.news_scraper import scrape_news
from services.sentiment import analyze_articles
from services.insider_tracker import get_insider_trades, detect_cluster_buys
from analysis.financial_ratios import calculate_ratios
from analysis.dcf_model import calculate_dcf
from analysis.comps_analysis import run_comps_analysis
from analysis.burn_rate import calculate_burn_rate
from analysis.debt_analysis import analyze_debt
from analysis.scoring import calculate_investment_score
from analysis.industry_benchmark import compare_to_industry

router = APIRouter()


@router.get("/company/{ticker}")
async def get_company_evaluation(ticker: str):
    ticker = ticker.upper()

    async with httpx.AsyncClient() as client:
        # Step 1: Resolve ticker to CIK
        cik = await resolve_ticker(ticker, client)
        if not cik:
            return {"error": f"Ticker '{ticker}' not found in SEC EDGAR"}

        # Step 2: Fetch all data in parallel
        submissions_task = get_company_submissions(cik, client)
        facts_task = get_company_facts(cik, client)
        price_task = get_stock_price(ticker, client)
        quote_task = get_quote_summary(ticker, client)
        history_task = get_stock_history(ticker, client, period="1y")

        submissions, facts, price_data, quote_data, price_history = await asyncio.gather(
            submissions_task, facts_task, price_task, quote_task, history_task,
            return_exceptions=True,
        )

        # Handle exceptions gracefully
        if isinstance(submissions, Exception):
            submissions = None
        if isinstance(facts, Exception):
            facts = None
        if isinstance(price_data, Exception):
            price_data = None
        if isinstance(quote_data, Exception):
            quote_data = None
        if isinstance(price_history, Exception):
            price_history = None

        # Step 3: Extract company info
        company_info = extract_company_info(submissions) if submissions else {"ticker": ticker, "cik": cik}

        # Step 4: Parse financial statements
        statements = []
        if facts:
            statements = parse_financial_statements(facts, num_years=5)

        # Step 5: Extract filings
        filings = []
        if submissions:
            filings = extract_recent_filings(submissions, form_types=["10-K", "10-Q", "8-K", "4"], limit=30)

        # Step 6: Fetch news + insiders in parallel
        company_name = company_info.get("name", ticker)
        news_task = scrape_news(company_name, ticker, client, limit=15)
        insider_task = get_insider_trades(cik, submissions, client, limit=30) if submissions else asyncio.coroutine(lambda: [])()

        try:
            news_articles, insider_trades = await asyncio.gather(
                news_task, insider_task, return_exceptions=True
            )
        except Exception:
            news_articles = []
            insider_trades = []

        if isinstance(news_articles, Exception):
            news_articles = []
        if isinstance(insider_trades, Exception):
            insider_trades = []

        # Step 7: Run analysis pipeline
        current_price = price_data.get("current_price") if price_data else None
        market_cap = quote_data.get("market_cap") if quote_data else None
        shares = None
        if statements:
            shares = statements[0].get("shares_outstanding") or statements[0].get("shares_diluted")

        stock_data = {}
        if price_data:
            stock_data.update(price_data)
        if quote_data:
            stock_data.update(quote_data)

        ratios = calculate_ratios(statements, stock_data) if statements else {}

        dcf = {}
        if statements:
            dcf = calculate_dcf(
                statements=statements,
                current_price=current_price,
                shares_outstanding=shares,
                market_cap=market_cap,
            )

        sic_code = company_info.get("sic_code", "")

        comps = await run_comps_analysis(
            ticker=ticker,
            target_financials=statements[0] if statements else {},
            target_stock=stock_data,
            sic_code=sic_code,
            client=client,
        )

        debt = analyze_debt(statements) if statements else {}
        burn = calculate_burn_rate(statements) if statements else {}
        sentiment = analyze_articles(news_articles)
        cluster_buys = detect_cluster_buys(insider_trades)
        industry = compare_to_industry(ratios, sic_code) if ratios else {}

        # Step 8: Calculate investment score
        score = {}
        if ratios:
            score = calculate_investment_score(
                ratios=ratios,
                dcf=dcf,
                debt=debt,
                burn_rate=burn,
                sentiment=sentiment,
                insider_data={"cluster_buys": cluster_buys, "trades": insider_trades},
                comps=comps,
            )

        # Step 9: Assemble response
        return {
            "ticker": ticker,
            "company": company_info,
            "score": score,
            "stock": {
                "current_price": current_price,
                "market_cap": market_cap,
                **({k: v for k, v in (quote_data or {}).items() if k not in ("market_cap",)}),
            },
            "price_history": price_history,
            "financials": {
                "statements": statements,
                "ratios": ratios,
            },
            "valuation": {
                "dcf": dcf,
                "comps": comps,
            },
            "debt_analysis": debt,
            "burn_rate": burn,
            "industry_comparison": industry,
            "insider_trading": {
                "trades": insider_trades[:20],
                "total_trades": len(insider_trades),
                "cluster_buys": cluster_buys,
            },
            "news": {
                "sentiment": {
                    "overall_score": sentiment.get("overall_score", 0),
                    "overall_label": sentiment.get("overall_label", "neutral"),
                    "positive_count": sentiment.get("positive_count", 0),
                    "negative_count": sentiment.get("negative_count", 0),
                    "neutral_count": sentiment.get("neutral_count", 0),
                },
                "articles": sentiment.get("articles", [])[:15],
            },
            "filings": filings[:20],
        }
