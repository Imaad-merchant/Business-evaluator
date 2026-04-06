import httpx
import asyncio
import time
from typing import Optional
from config import get_settings

settings = get_settings()

HEADERS = {
    "User-Agent": settings.sec_user_agent,
    "Accept": "application/json",
}

BASE_URL = "https://data.sec.gov"
SEC_URL = "https://www.sec.gov"
EFTS_URL = "https://efts.sec.gov/LATEST"

_ticker_map: dict[str, str] = {}
_last_request_time = 0.0
_lock = asyncio.Lock()


async def _rate_limit():
    global _last_request_time
    async with _lock:
        now = time.monotonic()
        elapsed = now - _last_request_time
        if elapsed < 0.12:
            await asyncio.sleep(0.12 - elapsed)
        _last_request_time = time.monotonic()


async def _get(url: str, client: httpx.AsyncClient) -> dict | list | None:
    await _rate_limit()
    try:
        resp = await client.get(url, headers=HEADERS, timeout=30.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"EDGAR request failed: {url} - {e}")
        return None


async def load_ticker_map(client: httpx.AsyncClient) -> dict[str, str]:
    global _ticker_map
    if _ticker_map:
        return _ticker_map

    data = await _get(f"{SEC_URL}/files/company_tickers.json", client)
    if not data:
        return {}

    for entry in data.values():
        ticker = str(entry.get("ticker", "")).upper()
        cik = str(entry.get("cik_str", ""))
        if ticker and cik:
            _ticker_map[ticker] = cik.zfill(10)

    return _ticker_map


async def resolve_ticker(ticker: str, client: httpx.AsyncClient) -> Optional[str]:
    ticker_map = await load_ticker_map(client)
    return ticker_map.get(ticker.upper())


async def search_companies(query: str, client: httpx.AsyncClient, limit: int = 10) -> list[dict]:
    ticker_map = await load_ticker_map(client)
    query_upper = query.upper()
    results = []

    for t, cik in ticker_map.items():
        if query_upper in t:
            results.append({"ticker": t, "cik": cik})
            if len(results) >= limit:
                break

    if len(results) < limit:
        data = await _get(
            f"{EFTS_URL}/search-index?q={query}&dateRange=custom&startdt=2020-01-01&forms=10-K&hits.hits.total.value=true&hits.hits._source=entity_name,ticker,file_date",
            client
        )
        if data and "hits" in data:
            for hit in data["hits"].get("hits", [])[:limit]:
                src = hit.get("_source", {})
                t = src.get("ticker", [""])[0] if isinstance(src.get("ticker"), list) else src.get("ticker", "")
                if t and t.upper() not in [r["ticker"] for r in results]:
                    cik = ticker_map.get(t.upper(), "")
                    results.append({
                        "ticker": t.upper(),
                        "cik": cik,
                        "name": src.get("entity_name", ""),
                    })

    return results[:limit]


async def get_company_submissions(cik: str, client: httpx.AsyncClient) -> Optional[dict]:
    return await _get(f"{BASE_URL}/submissions/CIK{cik}.json", client)


async def get_company_facts(cik: str, client: httpx.AsyncClient) -> Optional[dict]:
    return await _get(f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json", client)


async def get_company_concept(
    cik: str, taxonomy: str, concept: str, client: httpx.AsyncClient
) -> Optional[dict]:
    return await _get(
        f"{BASE_URL}/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{concept}.json",
        client
    )


async def get_filing_document(accession: str, primary_doc: str, client: httpx.AsyncClient) -> Optional[str]:
    await _rate_limit()
    accession_clean = accession.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{accession_clean[:10]}/{accession_clean}/{primary_doc}"
    try:
        resp = await client.get(url, headers=HEADERS, timeout=30.0)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


def extract_company_info(submissions: dict) -> dict:
    return {
        "cik": submissions.get("cik", ""),
        "name": submissions.get("name", ""),
        "ticker": submissions.get("tickers", [""])[0] if submissions.get("tickers") else "",
        "sic_code": submissions.get("sic", ""),
        "sic_description": submissions.get("sicDescription", ""),
        "exchange": submissions.get("exchanges", [""])[0] if submissions.get("exchanges") else "",
        "state": submissions.get("stateOfIncorporation", ""),
        "fiscal_year_end": submissions.get("fiscalYearEnd", ""),
        "website": submissions.get("website", ""),
        "description": submissions.get("description", ""),
        "ein": submissions.get("ein", ""),
        "category": submissions.get("category", ""),
    }


def extract_recent_filings(submissions: dict, form_types: list[str] | None = None, limit: int = 50) -> list[dict]:
    recent = submissions.get("filings", {}).get("recent", {})
    if not recent:
        return []

    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    descriptions = recent.get("primaryDocDescription", [])
    report_dates = recent.get("reportDate", [])

    filings = []
    for i in range(min(len(forms), len(dates))):
        form = forms[i] if i < len(forms) else ""
        if form_types and form not in form_types:
            continue

        accession = accessions[i] if i < len(accessions) else ""
        accession_clean = accession.replace("-", "")
        cik = submissions.get("cik", "")
        primary_doc = primary_docs[i] if i < len(primary_docs) else ""

        filings.append({
            "form_type": form,
            "filed_date": dates[i] if i < len(dates) else "",
            "accession_number": accession,
            "reporting_date": report_dates[i] if i < len(report_dates) else "",
            "description": descriptions[i] if i < len(descriptions) else "",
            "document_url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{primary_doc}" if primary_doc else "",
            "filing_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form}&dateb=&owner=include&count=40",
        })

        if len(filings) >= limit:
            break

    return filings
