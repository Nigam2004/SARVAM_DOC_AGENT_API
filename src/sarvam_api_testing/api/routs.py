
import uuid
import logging

from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from fastapi.concurrency import run_in_threadpool

from src.sarvam_api_testing.services.sarvam_extractor import extract_worker_document
from src.sarvam_api_testing.services.sarvam_parser import parse_worker_document
router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)


@router.post("/extract-document")
async def extract_document(
    file: UploadFile = File(...)
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = UPLOAD_DIR / f"{uuid.uuid4()}.pdf"

    try:

        # STEP 1: Save uploaded PDF
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="PDF size must not exceed 15 MB."
            )

        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file."
            )

        file_path.write_bytes(content)

        # STEP 2: Call Sarvam extraction
        result = await run_in_threadpool(
            extract_worker_document,
            str(file_path)
        )

        # STEP 3: Return extracted data
        return {
            "success": True,
            "message": "Document extracted successfully",
            "filename": file.filename,
            "data": result
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Sarvam extraction failed")

        raise HTTPException(
            status_code=502,
            detail=f"Document extraction failed: {type(e).__name__}"
        )

    finally:

        await file.close()

        if file_path.exists():
            file_path.unlink()




@router.post("/parse-document")
async def parse_document(
    file: UploadFile = File(...)
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = UPLOAD_DIR / f"{uuid.uuid4()}.pdf"

    try:

        # STEP 1: Save uploaded PDF
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="PDF size must not exceed 15 MB."
            )

        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file."
            )

        file_path.write_bytes(content)

        # STEP 2: Call Sarvam extraction
        result = await run_in_threadpool(
            parse_worker_document,
            str(file_path)
        )

        # STEP 3: Return parsed data
        return {
            "success": True,
            "message": "Document parsed successfully",
            "filename": file.filename,
            "data": result
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Sarvam parsed failed")

        raise HTTPException(
            status_code=502,
            detail=f"Document extraction failed: {type(e).__name__}"
        )

    finally:

        await file.close()

        if file_path.exists():
            file_path.unlink()



