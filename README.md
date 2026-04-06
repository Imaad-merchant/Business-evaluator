# Business Evaluator

A comprehensive company evaluation platform for **investors**, **venture capitalists**, **private equity firms**, and **traders**. Enter any public company's ticker and get a full investment analysis powered by SEC EDGAR data.

## Features

- **SEC EDGAR Integration** — Automated scraping of 10-K, 10-Q, 8-K filings with XBRL financial data extraction
- **Financial Analysis** — Revenue, profit margins, EBITDA, ROE, ROA, liquidity ratios, leverage metrics
- **DCF Valuation** — 10-year discounted cash flow model with intrinsic value per share
- **Comparable Companies** — Peer comparison with implied valuation from median multiples
- **Investment Score** — 0-100 score (A+ to F grade) with weighted components and bull/bear case
- **Insider Trading Tracker** — Form 4 parsing with cluster buy detection (strong buy signal)
- **News Sentiment** — RSS aggregation with NLP sentiment analysis (TextBlob + financial keywords)
- **Burn Rate Calculator** — Cash runway analysis for high-growth / cash-burning companies
- **Debt Risk Analysis** — Leverage ratios, interest coverage, risk assessment
- **Industry Benchmarks** — Company metrics vs. SIC industry medians
- **PDF Export** — One-pager investment report with all key metrics
- **Bloomberg-style UI** — Dark theme dashboard with charts, tables, and gauges

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Data Sources | SEC EDGAR (free), Yahoo Finance, Google News RSS |
| NLP | TextBlob with financial keyword boosters |
| PDF Export | ReportLab |
| Deploy | Vercel (frontend) + Railway (backend + DB) |

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose (for local PostgreSQL)

### Local Development

```bash
# 1. Clone the repo
git clone https://github.com/Imaad-merchant/Business-evaluator.git
cd Business-evaluator

# 2. Start PostgreSQL
docker-compose up -d db

# 3. Start the backend
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 4. Start the frontend (new terminal)
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000 and search for any ticker (AAPL, TSLA, MSFT, etc.)

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/company/{ticker}` | Full company evaluation (all data + analysis) |
| `GET /api/search?q=` | Ticker/company name search |
| `GET /api/financials/{ticker}` | Financial statements + ratios |
| `GET /api/valuation/{ticker}` | DCF + comparable companies |
| `GET /api/news/{ticker}` | News articles + sentiment |
| `GET /api/insiders/{ticker}` | Insider trading + cluster buy detection |
| `GET /api/filings/{ticker}` | SEC filing history |
| `GET /api/industry/{sic_code}` | Industry benchmarks |
| `GET /api/export/{ticker}/pdf` | Download PDF one-pager |

## Deployment

### Frontend (Vercel)
1. Connect the repo to Vercel
2. Set root directory to `frontend`
3. Add env var: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api`

### Backend (Railway)
1. Create new project on Railway
2. Add PostgreSQL plugin
3. Deploy from GitHub, set root directory to `backend`
4. Add env vars: `DATABASE_URL`, `SEC_USER_AGENT`, `CORS_ORIGINS`

## Data Sources

All data is from **free, public sources** — no API keys required:

- **SEC EDGAR** (`data.sec.gov`) — Company filings, XBRL financial data, insider trades
- **Yahoo Finance** — Stock prices, market cap, valuation multiples
- **Google News RSS** — Recent news articles
- **Yahoo Finance RSS** — Financial news

## License

MIT
