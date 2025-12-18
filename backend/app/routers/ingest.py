"""Ingestion API router."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.database import get_db
from app.models.schemas import IngestResponse, IngestURLRequest
from app.services.ingestion import get_ingestion_service

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/pdf", response_model=IngestResponse)
async def ingest_pdf(
    file: Annotated[UploadFile, File(description="PDF file to ingest")],
    title: Annotated[str, Form(description="Document title")],
    description: Annotated[str | None, Form(description="Optional description")] = None,
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    """Ingest a PDF document into the knowledge base.

    The PDF is processed, chunked, and embedded for semantic search.
    Extracted text is stored with source provenance for citations.

    Args:
        file: PDF file upload
        title: Document title
        description: Optional description
        db: Database session

    Returns:
        IngestResponse with document ID and chunk count
    """
    settings = get_settings()

    # Save uploaded file
    pdf_dir = settings.pdfs_dir
    pdf_dir.mkdir(parents=True, exist_ok=True)
    file_path = pdf_dir / file.filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Ingest the PDF
    try:
        ingestion_service = get_ingestion_service(db)
        source_doc, num_chunks = await ingestion_service.ingest_pdf(
            file_path=file_path,
            title=title,
            metadata={"description": description} if description else None,
        )

        return IngestResponse(
            source_document_id=source_doc.id,
            chunks_created=num_chunks,
            message=f"Successfully ingested '{title}' with {num_chunks} chunks",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/url", response_model=IngestResponse)
async def ingest_url(
    request: IngestURLRequest,
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    """Ingest a web page into the knowledge base.

    The URL is scraped, text is extracted, chunked, and embedded
    for semantic search.

    Args:
        request: URL ingestion request with url and title
        db: Database session

    Returns:
        IngestResponse with document ID and chunk count
    """
    try:
        ingestion_service = get_ingestion_service(db)
        source_doc, num_chunks = await ingestion_service.ingest_url(
            url=request.url,
            title=request.title,
            metadata={"description": request.description} if request.description else None,
        )

        return IngestResponse(
            source_document_id=source_doc.id,
            chunks_created=num_chunks,
            message=f"Successfully ingested '{request.title}' from URL with {num_chunks} chunks",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/yaml", response_model=dict)
async def ingest_yaml_capabilities(
    file: Annotated[UploadFile, File(description="YAML file with capability definitions")],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Ingest capabilities from a YAML file.

    The YAML file should contain lab and capability definitions
    following the expected schema.

    Args:
        file: YAML file upload
        db: Database session

    Returns:
        Summary of ingested entities
    """
    settings = get_settings()

    # Save uploaded file temporarily
    data_dir = settings.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / file.filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        ingestion_service = get_ingestion_service(db)
        labs, facilities, capabilities = await ingestion_service.ingest_yaml_capabilities(
            file_path=file_path,
        )

        # Clean up temp file
        file_path.unlink()

        return {
            "message": "Successfully ingested capabilities from YAML",
            "labs_created": labs,
            "facilities_created": facilities,
            "capabilities_created": capabilities,
        }
    except Exception as e:
        # Clean up temp file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
