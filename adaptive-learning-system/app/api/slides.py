import os
from functools import lru_cache
from pathlib import Path
from fastapi import APIRouter, HTTPException, Response

router = APIRouter(prefix="/documents", tags=["slides"])

UPLOADS_DIR = Path("data/uploads")

@lru_cache(maxsize=256)
def _render_page_cached(pdf_path_str: str, page_num: int) -> bytes:
    import fitz
    with fitz.open(pdf_path_str) as doc:
        if page_num > len(doc):
            return None
        page = doc.load_page(page_num - 1)
        # 150 DPI provides sharp rendering for UI display
        pix = page.get_pixmap(dpi=150)
        return pix.tobytes("png")

@router.get("/{document_id}/slide/{page_number}")
def get_slide_image(document_id: str, page_number: int):
    """Render and serve a specific page of an uploaded PDF document as a PNG image."""
    pdf_path = UPLOADS_DIR / f"{document_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Document PDF {document_id} not found on server.")
    
    if page_number < 1:
        raise HTTPException(status_code=400, detail="Page number must be at least 1.")
        
    try:
        img_bytes = _render_page_cached(str(pdf_path.resolve()), page_number)
        if img_bytes is None:
            raise HTTPException(status_code=404, detail=f"Page {page_number} exceeds document page count.")
        return Response(content=img_bytes, media_type="image/png", headers={"Cache-Control": "max-age=3600"})
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error rendering slide image: {str(e)}")
