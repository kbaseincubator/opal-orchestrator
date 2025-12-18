"""Retrieval service for searching capabilities and documents."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Capability, Facility, Lab, SourceChunk, SourceDocument
from app.models.schemas import (
    CapabilitySearchResult,
    CapabilityWithContext,
    SearchResult,
)
from app.services.embeddings import get_embedding_service


class RetrievalService:
    """Service for retrieving and searching capabilities."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = get_embedding_service()

    async def search_chunks(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict] = None,
    ) -> list[SearchResult]:
        """Search source chunks by semantic similarity.

        Args:
            query: Search query
            top_k: Number of results
            filters: Optional metadata filters

        Returns:
            List of SearchResult objects
        """
        results = await self.embedding_service.search(
            query=query,
            top_k=top_k,
            filters=filters,
        )

        search_results = []
        for r in results:
            # Get source document title
            doc_id = r["metadata"].get("source_document_id")
            source_title = "Unknown"
            if doc_id:
                doc = await self.db.get(SourceDocument, doc_id)
                if doc:
                    source_title = doc.title

            search_results.append(SearchResult(
                chunk_id=r["id"],
                source_document_id=doc_id or "",
                source_title=source_title,
                text=r["text"],
                score=r["score"],
                metadata=r["metadata"],
            ))

        return search_results

    async def search_capabilities(
        self,
        query: str,
        top_k: int = 10,
        lab_id: Optional[str] = None,
        modality: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list[CapabilitySearchResult]:
        """Search capabilities by semantic similarity with optional filters.

        Args:
            query: Search query
            top_k: Number of results
            lab_id: Filter by lab ID
            modality: Filter by modality
            tags: Filter by tags

        Returns:
            List of CapabilitySearchResult objects
        """
        # Build filters for vector search
        filters = {}
        if lab_id:
            filters["lab_id"] = lab_id

        # Search chunks
        chunk_results = await self.embedding_service.search(
            query=query,
            top_k=top_k * 2,  # Get more results for filtering
            filters=filters if filters else None,
        )

        # Group results by capability
        capability_scores: dict[str, tuple[float, list[dict]]] = {}

        for result in chunk_results:
            cap_name = result["metadata"].get("capability_name")
            if not cap_name:
                continue

            if cap_name not in capability_scores:
                capability_scores[cap_name] = (result["score"], [result])
            else:
                current_score, chunks = capability_scores[cap_name]
                capability_scores[cap_name] = (
                    max(current_score, result["score"]),
                    chunks + [result],
                )

        # Fetch capability details
        search_results = []
        for cap_name, (score, chunks) in sorted(
            capability_scores.items(),
            key=lambda x: x[1][0],
            reverse=True,
        )[:top_k]:
            # Find capability in database
            result = await self.db.execute(
                select(Capability)
                .options(selectinload(Capability.facility).selectinload(Facility.lab))
                .where(Capability.name == cap_name)
            )
            capability = result.scalar_one_or_none()

            if not capability:
                continue

            # Apply additional filters
            if modality and capability.modalities:
                if modality.lower() not in [m.lower() for m in capability.modalities]:
                    continue

            if tags and capability.tags:
                cap_tags_lower = [t.lower() for t in capability.tags]
                if not any(t.lower() in cap_tags_lower for t in tags):
                    continue

            # Build response
            facility = capability.facility
            lab = facility.lab

            cap_with_context = CapabilityWithContext(
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
                facility_name=facility.name,
                lab_name=lab.name,
                lab_institution=lab.institution,
            )

            source_chunks = []
            for chunk in chunks:
                doc_id = chunk["metadata"].get("source_document_id")
                source_title = "Unknown"
                if doc_id:
                    doc = await self.db.get(SourceDocument, doc_id)
                    if doc:
                        source_title = doc.title

                source_chunks.append(SearchResult(
                    chunk_id=chunk["id"],
                    source_document_id=doc_id or "",
                    source_title=source_title,
                    text=chunk["text"],
                    score=chunk["score"],
                    metadata=chunk["metadata"],
                ))

            search_results.append(CapabilitySearchResult(
                capability=cap_with_context,
                relevance_score=score,
                source_chunks=source_chunks,
            ))

        return search_results

    async def get_all_labs(self) -> list[Lab]:
        """Get all labs."""
        result = await self.db.execute(select(Lab))
        return list(result.scalars().all())

    async def get_lab_capabilities(self, lab_id: str) -> list[Capability]:
        """Get all capabilities for a lab."""
        result = await self.db.execute(
            select(Capability)
            .join(Facility)
            .where(Facility.lab_id == lab_id)
            .options(selectinload(Capability.facility))
        )
        return list(result.scalars().all())

    async def get_capability_by_id(self, capability_id: str) -> Optional[Capability]:
        """Get a capability by ID with full context."""
        result = await self.db.execute(
            select(Capability)
            .options(selectinload(Capability.facility).selectinload(Facility.lab))
            .where(Capability.id == capability_id)
        )
        return result.scalar_one_or_none()

    async def get_source_chunks(
        self,
        source_document_id: str,
    ) -> list[SourceChunk]:
        """Get all chunks for a source document."""
        result = await self.db.execute(
            select(SourceChunk)
            .where(SourceChunk.source_document_id == source_document_id)
            .order_by(SourceChunk.chunk_index)
        )
        return list(result.scalars().all())


def get_retrieval_service(db: AsyncSession) -> RetrievalService:
    """Get a retrieval service instance."""
    return RetrievalService(db)
