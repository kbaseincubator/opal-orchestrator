"""Capabilities API router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Capability, Facility, Lab
from app.models.database import get_db
from app.models.schemas import (
    CapabilityResponse,
    CapabilitySearchResult,
    CapabilityWithContext,
    LabResponse,
    SearchQuery,
)
from app.services.retrieval import get_retrieval_service

router = APIRouter(prefix="/capabilities", tags=["capabilities"])


@router.get("/search", response_model=list[CapabilitySearchResult])
async def search_capabilities(
    q: str = Query(..., description="Search query"),
    lab: str | None = Query(None, description="Filter by lab name"),
    modality: str | None = Query(None, description="Filter by modality"),
    tags: list[str] | None = Query(None, description="Filter by tags"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results"),
    db: AsyncSession = Depends(get_db),
) -> list[CapabilitySearchResult]:
    """Search capabilities using semantic similarity.

    Searches the capability registry using embeddings and returns
    matching capabilities with relevance scores and source citations.

    Args:
        q: Search query
        lab: Optional lab name filter
        modality: Optional modality filter
        tags: Optional tag filters
        top_k: Number of results to return
        db: Database session

    Returns:
        List of CapabilitySearchResult with capabilities and citations
    """
    retrieval_service = get_retrieval_service(db)

    # If lab name provided, find lab ID
    lab_id = None
    if lab:
        result = await db.execute(
            select(Lab).where(Lab.name.ilike(f"%{lab}%"))
        )
        lab_obj = result.scalar_one_or_none()
        if lab_obj:
            lab_id = lab_obj.id

    results = await retrieval_service.search_capabilities(
        query=q,
        top_k=top_k,
        lab_id=lab_id,
        modality=modality,
        tags=tags,
    )

    return results


@router.get("", response_model=list[CapabilityWithContext])
async def list_capabilities(
    lab_id: str | None = Query(None, description="Filter by lab ID"),
    facility_id: str | None = Query(None, description="Filter by facility ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[CapabilityWithContext]:
    """List all capabilities with optional filters.

    Args:
        lab_id: Optional lab ID filter
        facility_id: Optional facility ID filter
        skip: Number of results to skip
        limit: Maximum number of results
        db: Database session

    Returns:
        List of capabilities with context
    """
    query = (
        select(Capability)
        .options(selectinload(Capability.facility).selectinload(Facility.lab))
        .offset(skip)
        .limit(limit)
    )

    if facility_id:
        query = query.where(Capability.facility_id == facility_id)
    elif lab_id:
        query = query.join(Facility).where(Facility.lab_id == lab_id)

    result = await db.execute(query)
    capabilities = result.scalars().all()

    return [
        CapabilityWithContext(
            id=cap.id,
            facility_id=cap.facility_id,
            name=cap.name,
            description=cap.description,
            modalities=cap.modalities,
            throughput=cap.throughput,
            sample_requirements=cap.sample_requirements,
            constraints=cap.constraints,
            typical_outputs=cap.typical_outputs,
            readiness_level=cap.readiness_level,
            tags=cap.tags,
            source_document_id=cap.source_document_id,
            created_at=cap.created_at,
            updated_at=cap.updated_at,
            facility_name=cap.facility.name,
            lab_name=cap.facility.lab.name,
            lab_institution=cap.facility.lab.institution,
        )
        for cap in capabilities
    ]


@router.get("/{capability_id}", response_model=CapabilityWithContext)
async def get_capability(
    capability_id: str,
    db: AsyncSession = Depends(get_db),
) -> CapabilityWithContext:
    """Get a specific capability by ID.

    Args:
        capability_id: Capability ID
        db: Database session

    Returns:
        Capability with full context
    """
    result = await db.execute(
        select(Capability)
        .options(selectinload(Capability.facility).selectinload(Facility.lab))
        .where(Capability.id == capability_id)
    )
    capability = result.scalar_one_or_none()

    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    return CapabilityWithContext(
        id=capability.id,
        facility_id=capability.facility_id,
        name=capability.name,
        description=capability.description,
        modalities=capability.modalities,
        throughput=capability.throughput,
        sample_requirements=capability.sample_requirements,
        constraints=capability.constraints,
        typical_outputs=capability.typical_outputs,
        readiness_level=capability.readiness_level,
        tags=capability.tags,
        source_document_id=capability.source_document_id,
        created_at=capability.created_at,
        updated_at=capability.updated_at,
        facility_name=capability.facility.name,
        lab_name=capability.facility.lab.name,
        lab_institution=capability.facility.lab.institution,
    )


@router.get("/labs", response_model=list[LabResponse])
async def list_labs(
    db: AsyncSession = Depends(get_db),
) -> list[LabResponse]:
    """List all OPAL member labs.

    Returns:
        List of labs
    """
    result = await db.execute(select(Lab))
    labs = result.scalars().all()
    return [LabResponse.model_validate(lab) for lab in labs]
