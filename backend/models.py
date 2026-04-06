from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean, Date, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    cik = Column(String(10), unique=True, index=True)
    ticker = Column(String(10), unique=True, index=True)
    name = Column(String(255), nullable=False)
    sic_code = Column(String(10))
    sic_description = Column(String(255))
    exchange = Column(String(20))
    state = Column(String(10))
    fiscal_year_end = Column(String(4))
    description = Column(Text)
    website = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    financials = relationship("FinancialStatement", back_populates="company")
    filings = relationship("SECFiling", back_populates="company")
    insider_trades = relationship("InsiderTrade", back_populates="company")
    news_articles = relationship("NewsArticle", back_populates="company")
    valuations = relationship("Valuation", back_populates="company")
    stock_prices = relationship("StockPrice", back_populates="company")


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period_end = Column(Date, nullable=False)
    form_type = Column(String(10))  # 10-K or 10-Q
    fiscal_year = Column(Integer)
    fiscal_period = Column(String(5))  # FY, Q1, Q2, Q3, Q4

    # Income Statement
    revenue = Column(BigInteger)
    cost_of_revenue = Column(BigInteger)
    gross_profit = Column(BigInteger)
    operating_expenses = Column(BigInteger)
    operating_income = Column(BigInteger)
    interest_expense = Column(BigInteger)
    income_before_tax = Column(BigInteger)
    income_tax = Column(BigInteger)
    net_income = Column(BigInteger)
    ebitda = Column(BigInteger)
    eps_basic = Column(Float)
    eps_diluted = Column(Float)
    shares_outstanding = Column(BigInteger)
    shares_diluted = Column(BigInteger)

    # Balance Sheet
    cash_and_equivalents = Column(BigInteger)
    short_term_investments = Column(BigInteger)
    total_current_assets = Column(BigInteger)
    total_assets = Column(BigInteger)
    total_current_liabilities = Column(BigInteger)
    long_term_debt = Column(BigInteger)
    total_liabilities = Column(BigInteger)
    stockholders_equity = Column(BigInteger)
    total_debt = Column(BigInteger)

    # Cash Flow
    operating_cash_flow = Column(BigInteger)
    capital_expenditures = Column(BigInteger)
    free_cash_flow = Column(BigInteger)
    investing_cash_flow = Column(BigInteger)
    financing_cash_flow = Column(BigInteger)
    depreciation_amortization = Column(BigInteger)

    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="financials")


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    market_cap = Column(BigInteger)

    company = relationship("Company", back_populates="stock_prices")


class SECFiling(Base):
    __tablename__ = "sec_filings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    accession_number = Column(String(25), unique=True)
    form_type = Column(String(20), nullable=False)
    filed_date = Column(Date, nullable=False)
    reporting_date = Column(Date)
    document_url = Column(String(500))
    description = Column(Text)
    sections_json = Column(JSON)  # Extracted sections from 10-K

    company = relationship("Company", back_populates="filings")


class InsiderTrade(Base):
    __tablename__ = "insider_trades"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    insider_name = Column(String(255), nullable=False)
    insider_title = Column(String(255))
    transaction_type = Column(String(20))  # P=Purchase, S=Sale, A=Award
    transaction_date = Column(Date, nullable=False)
    shares = Column(BigInteger)
    price_per_share = Column(Float)
    total_value = Column(BigInteger)
    shares_owned_after = Column(BigInteger)
    is_direct = Column(Boolean, default=True)
    filing_date = Column(Date)
    filing_url = Column(String(500))

    company = relationship("Company", back_populates="insider_trades")


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(500), nullable=False)
    source = Column(String(100))
    url = Column(String(500))
    published_at = Column(DateTime)
    sentiment_score = Column(Float)  # -1.0 to 1.0
    sentiment_label = Column(String(20))  # positive, negative, neutral
    summary = Column(Text)

    company = relationship("Company", back_populates="news_articles")


class IndustryBenchmark(Base):
    __tablename__ = "industry_benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    sic_code = Column(String(10), unique=True, index=True)
    industry_name = Column(String(255))
    naics_code = Column(String(10))
    median_gross_margin = Column(Float)
    median_operating_margin = Column(Float)
    median_net_margin = Column(Float)
    median_roe = Column(Float)
    median_roa = Column(Float)
    median_current_ratio = Column(Float)
    median_debt_to_equity = Column(Float)
    median_pe_ratio = Column(Float)
    median_pb_ratio = Column(Float)
    median_ev_revenue = Column(Float)
    median_ev_ebitda = Column(Float)
    median_revenue_growth = Column(Float)
    company_count = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Valuation(Base):
    __tablename__ = "valuations"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, nullable=False)
    dcf_value = Column(Float)
    comps_value = Column(Float)
    overall_score = Column(Integer)  # 0-100
    grade = Column(String(2))  # A+ to F
    analysis_json = Column(JSON)
    bull_case = Column(JSON)  # list of strings
    bear_case = Column(JSON)  # list of strings

    company = relationship("Company", back_populates="valuations")
