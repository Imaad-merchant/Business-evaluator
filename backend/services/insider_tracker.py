import httpx
from lxml import etree
from typing import Optional
from datetime import datetime, timedelta
from services.edgar import _rate_limit, HEADERS


async def get_insider_trades(cik: str, submissions: dict, client: httpx.AsyncClient, limit: int = 50) -> list[dict]:
    # Extract Form 4 filings from submissions
    recent = submissions.get("filings", {}).get("recent", {})
    if not recent:
        return []

    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    form4_filings = []
    for i in range(len(forms)):
        if forms[i] == "4" and i < len(accessions):
            form4_filings.append({
                "accession": accessions[i],
                "filed_date": dates[i] if i < len(dates) else "",
                "primary_doc": primary_docs[i] if i < len(primary_docs) else "",
            })
            if len(form4_filings) >= limit:
                break

    # Parse each Form 4 XML
    trades = []
    for filing in form4_filings[:20]:  # Limit to 20 to avoid too many requests
        trade_data = await _parse_form4(cik, filing, client)
        if trade_data:
            trades.extend(trade_data)

    trades.sort(key=lambda x: x.get("transaction_date", ""), reverse=True)
    return trades[:limit]


async def _parse_form4(cik: str, filing: dict, client: httpx.AsyncClient) -> list[dict]:
    await _rate_limit()

    accession_clean = filing["accession"].replace("-", "")
    primary_doc = filing.get("primary_doc", "")

    # Try to find the XML document
    if not primary_doc.endswith(".xml"):
        # Look for the XML version
        primary_doc = primary_doc.replace(".htm", ".xml").replace(".html", ".xml")

    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{primary_doc}"

    try:
        resp = await client.get(url, headers=HEADERS, timeout=15.0)
        if resp.status_code != 200:
            # Try the index page to find XML
            index_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/"
            idx_resp = await client.get(index_url, headers=HEADERS, timeout=15.0)
            if idx_resp.status_code != 200:
                return []
            # Look for XML file in the index
            text = idx_resp.text
            import re
            xml_files = re.findall(r'href="([^"]*\.xml)"', text)
            if not xml_files:
                return []
            primary_doc = xml_files[0]
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{primary_doc}"
            resp = await client.get(url, headers=HEADERS, timeout=15.0)
            if resp.status_code != 200:
                return []

        content = resp.text
        if not content.strip().startswith("<?xml") and "<ownershipDocument" not in content:
            return []

        root = etree.fromstring(content.encode())

        # Extract insider info
        owner = root.find(".//reportingOwner")
        if owner is None:
            return []

        owner_id = owner.find("reportingOwnerId")
        name = owner_id.findtext("rptOwnerName", "") if owner_id is not None else ""

        relationship = owner.find("reportingOwnerRelationship")
        title = ""
        if relationship is not None:
            title = relationship.findtext("officerTitle", "")
            if not title:
                if relationship.findtext("isDirector", "") == "1":
                    title = "Director"
                elif relationship.findtext("isTenPercentOwner", "") == "1":
                    title = "10% Owner"

        # Extract transactions
        trades = []
        for txn in root.findall(".//nonDerivativeTransaction"):
            security = txn.findtext(".//securityTitle/value", "")
            date = txn.findtext(".//transactionDate/value", "")
            code = txn.findtext(".//transactionCoding/transactionCode", "")
            shares = txn.findtext(".//transactionAmounts/transactionShares/value", "")
            price = txn.findtext(".//transactionAmounts/transactionPricePerShare/value", "")
            acquired = txn.findtext(".//transactionAmounts/transactionAcquiredDisposedCode/value", "")
            shares_after = txn.findtext(".//postTransactionAmounts/sharesOwnedFollowingTransaction/value", "")
            direct = txn.findtext(".//ownershipNature/directOrIndirectOwnership/value", "D")

            try:
                shares_num = float(shares) if shares else 0
                price_num = float(price) if price else 0
            except ValueError:
                shares_num = 0
                price_num = 0

            # Determine transaction type
            if code == "P":
                txn_type = "Purchase"
            elif code == "S":
                txn_type = "Sale"
            elif code == "A":
                txn_type = "Award"
            elif code == "M":
                txn_type = "Option Exercise"
            elif code == "G":
                txn_type = "Gift"
            else:
                txn_type = code or "Unknown"

            trades.append({
                "insider_name": name,
                "insider_title": title,
                "transaction_type": txn_type,
                "transaction_code": code,
                "transaction_date": date,
                "shares": int(shares_num),
                "price_per_share": round(price_num, 2),
                "total_value": int(shares_num * price_num),
                "acquired_disposed": "Acquired" if acquired == "A" else "Disposed",
                "shares_owned_after": int(float(shares_after)) if shares_after else None,
                "is_direct": direct == "D",
                "filing_date": filing.get("filed_date", ""),
                "filing_url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{filing.get('primary_doc', '')}",
            })

        return trades
    except Exception as e:
        print(f"Form 4 parse failed: {e}")
        return []


def detect_cluster_buys(trades: list[dict], days: int = 30, min_insiders: int = 3) -> dict:
    if not trades:
        return {"detected": False, "clusters": []}

    purchases = [t for t in trades if t.get("transaction_code") == "P"]
    if len(purchases) < min_insiders:
        return {"detected": False, "clusters": []}

    # Group by date windows
    clusters = []
    for trade in purchases:
        try:
            trade_date = datetime.strptime(trade["transaction_date"], "%Y-%m-%d")
        except (ValueError, KeyError):
            continue

        window_start = trade_date - timedelta(days=days)
        window_trades = [
            t for t in purchases
            if t.get("transaction_date") and
            window_start <= datetime.strptime(t["transaction_date"], "%Y-%m-%d") <= trade_date
        ]

        unique_insiders = set(t["insider_name"] for t in window_trades)
        if len(unique_insiders) >= min_insiders:
            clusters.append({
                "end_date": trade["transaction_date"],
                "start_date": window_start.strftime("%Y-%m-%d"),
                "insider_count": len(unique_insiders),
                "insiders": list(unique_insiders),
                "total_shares": sum(t.get("shares", 0) for t in window_trades),
                "total_value": sum(t.get("total_value", 0) for t in window_trades),
            })

    # Deduplicate overlapping clusters
    unique_clusters = []
    seen = set()
    for c in clusters:
        key = frozenset(c["insiders"])
        if key not in seen:
            seen.add(key)
            unique_clusters.append(c)

    return {
        "detected": len(unique_clusters) > 0,
        "clusters": unique_clusters,
        "signal": "STRONG BUY SIGNAL" if unique_clusters else "No cluster detected",
    }
