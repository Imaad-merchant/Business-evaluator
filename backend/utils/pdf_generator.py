from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime


def generate_one_pager(data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=20, textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#666666"),
        spaceAfter=8,
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        fontSize=12, textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=10, spaceAfter=4,
        borderWidth=0, borderPadding=0,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=9, leading=12,
    )
    small_style = ParagraphStyle(
        "Small", parent=styles["Normal"],
        fontSize=7, textColor=colors.HexColor("#999999"),
    )

    company = data.get("company", {})
    score = data.get("score", {})
    stock = data.get("stock", {})
    financials = data.get("financials", {})
    dcf = data.get("valuation", {}).get("dcf", {})
    comps = data.get("valuation", {}).get("comps", {})
    debt = data.get("debt_analysis", {})
    burn = data.get("burn_rate", {})
    sentiment = data.get("news", {}).get("sentiment", {})
    insider = data.get("insider_trading", {})

    ticker = data.get("ticker", "N/A")

    # Header
    elements.append(Paragraph(f"{company.get('name', ticker)} ({ticker})", title_style))
    exchange = company.get("exchange", "")
    sic = company.get("sic_description", "")
    elements.append(Paragraph(
        f"{exchange} | SIC: {company.get('sic_code', 'N/A')} - {sic} | Generated: {datetime.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a1a2e")))
    elements.append(Spacer(1, 8))

    # Score Section
    grade = score.get("grade", "N/A")
    overall = score.get("overall_score", "N/A")
    price = stock.get("current_price", "N/A")
    mcap = stock.get("market_cap")
    mcap_str = f"${mcap / 1e9:,.1f}B" if mcap and mcap > 1e9 else f"${mcap / 1e6:,.0f}M" if mcap else "N/A"

    score_data = [
        ["Investment Grade", "Score", "Current Price", "Market Cap"],
        [grade, f"{overall}/100", f"${price}" if isinstance(price, (int, float)) else price, mcap_str],
    ]
    score_table = Table(score_data, colWidths=[1.8 * inch] * 4)
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, 1), 14),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 8))

    # Key Financials
    elements.append(Paragraph("Key Financials", section_style))
    stmts = financials.get("statements", [])
    if stmts:
        latest = stmts[0]

        def _fmt(val):
            if val is None:
                return "N/A"
            if abs(val) >= 1e9:
                return f"${val / 1e9:,.1f}B"
            if abs(val) >= 1e6:
                return f"${val / 1e6:,.0f}M"
            return f"${val:,.0f}"

        fin_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Revenue", _fmt(latest.get("revenue")), "Net Income", _fmt(latest.get("net_income"))],
            ["EBITDA", _fmt(latest.get("ebitda")), "Free Cash Flow", _fmt(latest.get("free_cash_flow"))],
            ["Total Assets", _fmt(latest.get("total_assets")), "Total Debt", _fmt(latest.get("total_debt"))],
            ["Cash", _fmt(latest.get("cash_and_equivalents")), "Equity", _fmt(latest.get("stockholders_equity"))],
        ]
        fin_table = Table(fin_data, colWidths=[1.5 * inch, 1.3 * inch, 1.5 * inch, 1.3 * inch])
        fin_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(fin_table)

    # Ratios
    ratios = financials.get("ratios", {})
    prof = ratios.get("profitability", {})
    lev = ratios.get("leverage", {})
    if prof:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Profitability & Leverage", section_style))
        ratio_text = []
        if prof.get("gross_margin") is not None:
            ratio_text.append(f"Gross Margin: {prof['gross_margin']}%")
        if prof.get("operating_margin") is not None:
            ratio_text.append(f"Op Margin: {prof['operating_margin']}%")
        if prof.get("net_margin") is not None:
            ratio_text.append(f"Net Margin: {prof['net_margin']}%")
        if prof.get("roe") is not None:
            ratio_text.append(f"ROE: {prof['roe']}%")
        if lev.get("debt_to_equity") is not None:
            ratio_text.append(f"D/E: {lev['debt_to_equity']}x")
        if lev.get("interest_coverage") is not None:
            ratio_text.append(f"Interest Coverage: {lev['interest_coverage']}x")
        elements.append(Paragraph(" | ".join(ratio_text), body_style))

    # DCF Valuation
    if dcf and not dcf.get("error"):
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("DCF Valuation", section_style))
        iv = dcf.get("intrinsic_value_per_share", "N/A")
        upside = dcf.get("upside_percent", "N/A")
        verdict = dcf.get("verdict", "N/A")
        elements.append(Paragraph(
            f"Intrinsic Value: ${iv} | Upside: {upside}% | Verdict: <b>{verdict}</b>",
            body_style
        ))

    # Comps
    if comps and not comps.get("error"):
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Comparable Companies", section_style))
        peers = comps.get("peers", [])
        if peers:
            comp_data = [["Ticker", "Mkt Cap", "P/E", "EV/Rev", "EV/EBITDA"]]
            for p in peers[:5]:
                mc = p.get("market_cap")
                mc_str = f"${mc / 1e9:,.0f}B" if mc and mc > 1e9 else f"${mc / 1e6:,.0f}M" if mc else "N/A"
                comp_data.append([
                    p.get("ticker", ""),
                    mc_str,
                    f"{p.get('pe_ratio', 'N/A')}",
                    f"{p.get('ev_to_revenue', 'N/A')}",
                    f"{p.get('ev_to_ebitda', 'N/A')}",
                ])
            comp_table = Table(comp_data, colWidths=[1.0 * inch, 1.2 * inch, 1.0 * inch, 1.0 * inch, 1.2 * inch])
            comp_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            elements.append(comp_table)

    # Bull / Bear Case
    bull = score.get("bull_case", [])
    bear = score.get("bear_case", [])
    if bull or bear:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Investment Thesis", section_style))
        if bull:
            elements.append(Paragraph("<b>Bull Case:</b>", body_style))
            for b in bull:
                elements.append(Paragraph(f"  + {b}", body_style))
        if bear:
            elements.append(Paragraph("<b>Bear Case:</b>", body_style))
            for b in bear:
                elements.append(Paragraph(f"  - {b}", body_style))

    # Insider Trading
    cluster = insider.get("cluster_buys", {})
    if cluster.get("detected"):
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Insider Activity Alert", section_style))
        elements.append(Paragraph(
            f"<b>CLUSTER BUY DETECTED:</b> {cluster.get('signal', '')}",
            body_style
        ))

    # Sentiment
    if sentiment:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("News Sentiment", section_style))
        sent_label = sentiment.get("overall_label", "neutral").upper()
        sent_score = sentiment.get("overall_score", 0)
        elements.append(Paragraph(
            f"Sentiment: <b>{sent_label}</b> (Score: {sent_score})",
            body_style
        ))

    # Disclaimer
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    elements.append(Paragraph(
        "DISCLAIMER: This report is generated automatically for informational purposes only. "
        "It is not investment advice. Data sourced from SEC EDGAR and public sources. "
        "Always conduct your own due diligence before making investment decisions.",
        small_style
    ))
    elements.append(Paragraph(
        f"Generated by Business Evaluator | {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        small_style
    ))

    doc.build(elements)
    return buffer.getvalue()
