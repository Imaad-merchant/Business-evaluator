from fastapi import APIRouter
from analysis.industry_benchmark import get_benchmark

router = APIRouter()


@router.get("/industry/{sic_code}")
async def get_industry_benchmark(sic_code: str):
    benchmark = get_benchmark(sic_code)
    return {
        "sic_code": sic_code,
        "benchmark": benchmark,
    }
