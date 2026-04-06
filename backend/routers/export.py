from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import httpx
import io
from utils.pdf_generator import generate_one_pager

router = APIRouter()


@router.get("/export/{ticker}/pdf")
async def export_pdf(ticker: str):
    # Fetch the full company evaluation
    from routers.company import get_company_evaluation
    data = await get_company_evaluation(ticker)

    if "error" in data:
        return data

    # Generate PDF
    pdf_buffer = generate_one_pager(data)

    return StreamingResponse(
        io.BytesIO(pdf_buffer),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={ticker.upper()}_evaluation.pdf"
        },
    )
