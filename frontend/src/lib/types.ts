export interface CompanyEvaluation {
  ticker: string;
  company: CompanyInfo;
  score: InvestmentScore;
  stock: StockData;
  price_history: PricePoint[] | null;
  financials: {
    statements: FinancialStatement[];
    ratios: FinancialRatios;
  };
  valuation: {
    dcf: DCFResult;
    comps: CompsResult;
  };
  debt_analysis: DebtAnalysis;
  burn_rate: BurnRate;
  industry_comparison: IndustryComparison;
  insider_trading: InsiderData;
  news: NewsData;
  filings: Filing[];
}

export interface CompanyInfo {
  cik: string;
  name: string;
  ticker: string;
  sic_code: string;
  sic_description: string;
  exchange: string;
  state: string;
  fiscal_year_end: string;
  website: string;
  description: string;
}

export interface InvestmentScore {
  overall_score: number;
  grade: string;
  components: Record<string, { score: number; weight: number }>;
  bull_case: string[];
  bear_case: string[];
}

export interface StockData {
  current_price: number | null;
  previous_close: number | null;
  market_cap: number | null;
  pe_ratio: number | null;
  forward_pe: number | null;
  price_to_book: number | null;
  enterprise_value: number | null;
  ev_to_revenue: number | null;
  ev_to_ebitda: number | null;
  beta: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  dividend_yield: number | null;
  profit_margin: number | null;
  revenue_growth: number | null;
  recommendation: string | null;
}

export interface PricePoint {
  timestamp: number;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

export interface FinancialStatement {
  fiscal_year: number;
  fiscal_period: string;
  revenue: number | null;
  cost_of_revenue: number | null;
  gross_profit: number | null;
  operating_expenses: number | null;
  operating_income: number | null;
  interest_expense: number | null;
  income_tax: number | null;
  net_income: number | null;
  ebitda: number | null;
  eps_basic: number | null;
  eps_diluted: number | null;
  shares_outstanding: number | null;
  cash_and_equivalents: number | null;
  total_current_assets: number | null;
  total_assets: number | null;
  total_current_liabilities: number | null;
  long_term_debt: number | null;
  total_liabilities: number | null;
  stockholders_equity: number | null;
  total_debt: number | null;
  operating_cash_flow: number | null;
  capital_expenditures: number | null;
  free_cash_flow: number | null;
  depreciation_amortization: number | null;
}

export interface FinancialRatios {
  profitability: Record<string, number>;
  liquidity: Record<string, number>;
  leverage: Record<string, number>;
  efficiency: Record<string, number>;
  growth: Record<string, number>;
  valuation: Record<string, number>;
  per_share: Record<string, number>;
}

export interface DCFResult {
  intrinsic_value_per_share?: number;
  current_price?: number | null;
  upside_percent?: number | null;
  verdict?: string;
  assumptions?: Record<string, number>;
  projections?: Array<{ year: number; projected_fcf: number; present_value: number }>;
  error?: string;
}

export interface CompsResult {
  peers?: Array<{
    ticker: string;
    market_cap: number | null;
    pe_ratio: number | null;
    ev_to_revenue: number | null;
    ev_to_ebitda: number | null;
    profit_margin: number | null;
    revenue_growth: number | null;
  }>;
  median_multiples?: Record<string, number | null>;
  average_implied_value?: number | null;
  premium_discount_percent?: number | null;
  verdict?: string;
  error?: string;
}

export interface DebtAnalysis {
  total_debt: number;
  net_debt: number;
  ratios: Record<string, number | null>;
  risk_level: string;
  risk_factors: string[];
  debt_trend: Array<{ year: number; total_debt: number; cash: number; net_debt: number }>;
}

export interface BurnRate {
  is_burning_cash: boolean;
  total_cash: number;
  monthly_burn_rate: number;
  runway_months: number | null;
  health: string;
  health_color: string;
  note: string;
}

export interface IndustryComparison {
  industry: string;
  metrics: Array<{
    name: string;
    company_value: number;
    industry_median: number;
    difference: number;
    unit: string;
    status: string;
  }>;
  summary?: {
    above_average_count: number;
    below_average_count: number;
    total_metrics: number;
    overall: string;
  };
}

export interface InsiderData {
  trades: InsiderTrade[];
  total_trades: number;
  cluster_buys: {
    detected: boolean;
    signal: string;
    clusters: Array<{
      insider_count: number;
      total_value: number;
      insiders: string[];
    }>;
  };
}

export interface InsiderTrade {
  insider_name: string;
  insider_title: string;
  transaction_type: string;
  transaction_date: string;
  shares: number;
  price_per_share: number;
  total_value: number;
  acquired_disposed: string;
}

export interface NewsData {
  sentiment: {
    overall_score: number;
    overall_label: string;
    positive_count: number;
    negative_count: number;
    neutral_count: number;
  };
  articles: Array<{
    title: string;
    source: string;
    url: string;
    published_at: string;
    sentiment?: { score: number; label: string };
  }>;
}

export interface Filing {
  form_type: string;
  filed_date: string;
  accession_number: string;
  reporting_date: string;
  description: string;
  document_url: string;
}
