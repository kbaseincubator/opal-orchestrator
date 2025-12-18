"""Sources API router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SourceChunk, SourceDocument
from app.models.database import get_db
from app.models.schemas import SourceChunkResponse, SourceDocumentResponse
from app.services.retrieval import get_retrieval_service

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceDocumentResponse])
async def list_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[SourceDocumentResponse]:
    """List all source documents.

    Args:
        skip: Number of results to skip
        limit: Maximum number of results
        db: Database session

    Returns:
        List of source documents
    """
    result = await db.execute(
        select(SourceDocument)
        .order_by(SourceDocument.ingested_at.desc())
        .offset(skip)
        .limit(limit)
    )
    sources = result.scalars().all()
    return [SourceDocumentResponse.model_validate(s) for s in sources]


@router.get("/{source_id}", response_model=SourceDocumentResponse)
async def get_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
) -> SourceDocumentResponse:
    """Get a specific source document.

    Args:
        source_id: Source document ID
        db: Database session

    Returns:
        Source document details
    """
    source = await db.get(SourceDocument, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source document not found")
    return SourceDocumentResponse.model_validate(source)


@router.get("/{source_id}/chunks", response_model=list[SourceChunkResponse])
async def get_source_chunks(
    source_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[SourceChunkResponse]:
    """Get chunks for a source document.

    Args:
        source_id: Source document ID
        skip: Number of results to skip
        limit: Maximum number of results
        db: Database session

    Returns:
        List of source chunks
    """
    # Verify source exists
    source = await db.get(SourceDocument, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source document not found")

    retrieval_service = get_retrieval_service(db)
    chunks = await retrieval_service.get_source_chunks(source_id)

    return [
        SourceChunkResponse(
            id=chunk.id,
            source_document_id=chunk.source_document_id,
            text=chunk.text,
            metadata_=chunk.metadata_,
            chunk_index=chunk.chunk_index,
            created_at=chunk.created_at,
        )
        for chunk in chunks[skip : skip + limit]
    ]


@router.delete("/{source_id}")
async def delete_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a source document and its chunks.

    Args:
        source_id: Source document ID
        db: Database session

    Returns:
        Deletion confirmation
    """
    from app.services.embeddings import get_embedding_service

    source = await db.get(SourceDocument, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source document not found")

    # Delete embeddings from vector store
    embedding_service = get_embedding_service()
    chunks_deleted = await embedding_service.delete_document_chunks(source_id)

    # Delete from database (cascades to chunks)
    await db.delete(source)
    await db.commit()

    return {
        "message": f"Deleted source document '{source.title}'",
        "chunks_deleted": chunks_deleted,
    }
