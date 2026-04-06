from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from database import init_db
from routers import company, search, filings, financials, valuation, news, insiders, industry, export

app = FastAPI(
    title="Business Evaluator API",
    description="Company evaluation platform for investors, VCs, PE firms, and traders",
    version="1.0.0",
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(company.router, prefix="/api", tags=["company"])
app.include_router(filings.router, prefix="/api", tags=["filings"])
app.include_router(financials.router, prefix="/api", tags=["financials"])
app.include_router(valuation.router, prefix="/api", tags=["valuation"])
app.include_router(news.router, prefix="/api", tags=["news"])
app.include_router(insiders.router, prefix="/api", tags=["insiders"])
app.include_router(industry.router, prefix="/api", tags=["industry"])
app.include_router(export.router, prefix="/api", tags=["export"])


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
