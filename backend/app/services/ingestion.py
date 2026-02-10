"""Ingestion service for PDF, URL, and YAML documents."""

import re
from pathlib import Path
from typing import Optional

import httpx
import pdfplumber
import yaml
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Capability, Facility, Lab, SourceChunk, SourceDocument
from app.models.schemas import SourceTypeEnum
from app.services.embeddings import get_embedding_service


class IngestionService:
    """Service for ingesting documents into the knowledge base."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = get_embedding_service()

    async def close_connections(self):
        await self.embedding_service.close()

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> list[dict]:
        """Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Target chunk size in words
            chunk_overlap: Number of overlapping words between chunks

        Returns:
            List of chunk dicts with 'text' and 'metadata'
        """
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()

        # Split into sentences (approximate)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_word_count = 0

        for sentence in sentences:
            words = sentence.split()
            word_count = len(words)

            if current_word_count + word_count > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "metadata": {"word_count": current_word_count},
                })

                # Start new chunk with overlap
                overlap_words = chunk_overlap
                overlap_sentences = []
                overlap_word_count = 0
                for s in reversed(current_chunk):
                    s_words = len(s.split())
                    if overlap_word_count + s_words <= overlap_words:
                        overlap_sentences.insert(0, s)
                        overlap_word_count += s_words
                    else:
                        break

                current_chunk = overlap_sentences
                current_word_count = overlap_word_count

            current_chunk.append(sentence)
            current_word_count += word_count

        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "metadata": {"word_count": current_word_count},
            })

        return chunks

    async def ingest_pdf(
        self,
        file_path: Path,
        title: str,
        metadata: Optional[dict] = None,
    ) -> tuple[SourceDocument, int]:
        """Ingest a PDF document.

        Args:
            file_path: Path to PDF file
            title: Document title
            metadata: Optional metadata dict

        Returns:
            Tuple of (SourceDocument, num_chunks)
        """
        # Extract text from PDF
        text_by_page = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                text_by_page.append({
                    "page": i + 1,
                    "text": page_text,
                })

        # Check if source document with same path already exists
        result = await self.db.execute(
            select(SourceDocument).where(
                SourceDocument.url_or_path == str(file_path)
            )
        )
        existing_doc = result.scalar_one_or_none()

        if existing_doc:
            # Delete old chunks from ChromaDB
            await self.embedding_service.delete_document_chunks(existing_doc.id)
            # Delete old source document
            await self.db.delete(existing_doc)
            await self.db.flush()

        # Create source document
        source_doc = SourceDocument(
            type=SourceTypeEnum.PDF.value,
            title=title,
            url_or_path=str(file_path),
            metadata_=metadata or {},
        )
        self.db.add(source_doc)
        await self.db.flush()

        # Create chunks with page metadata
        all_chunks = []
        for page_data in text_by_page:
            page_chunks = self._chunk_text(page_data["text"])
            for chunk in page_chunks:
                chunk["metadata"]["page"] = page_data["page"]
            all_chunks.extend(page_chunks)

        # Create chunk records and embeddings
        chunk_ids = await self.embedding_service.add_chunks(
            chunks=all_chunks,
            source_document_id=source_doc.id,
        )

        for i, chunk_data in enumerate(all_chunks):
            chunk = SourceChunk(
                id=chunk_ids[i],
                source_document_id=source_doc.id,
                text=chunk_data["text"],
                metadata_=chunk_data["metadata"],
                chunk_index=i,
            )
            self.db.add(chunk)

        await self.db.commit()
        return source_doc, len(all_chunks)

    async def ingest_url(
        self,
        url: str,
        title: str,
        metadata: Optional[dict] = None,
    ) -> tuple[SourceDocument, int]:
        """Ingest a web page.

        Args:
            url: URL to scrape
            title: Document title
            metadata: Optional metadata dict

        Returns:
            Tuple of (SourceDocument, num_chunks)
        """
        # Fetch page
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            html = response.text

        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Extract text
        text = soup.get_text(separator=' ', strip=True)

        # Check if source document with same URL already exists
        result = await self.db.execute(
            select(SourceDocument).where(
                SourceDocument.url_or_path == url
            )
        )
        existing_doc = result.scalar_one_or_none()

        if existing_doc:
            # Delete old chunks from ChromaDB
            await self.embedding_service.delete_document_chunks(existing_doc.id)
            # Delete old source document
            await self.db.delete(existing_doc)
            await self.db.flush()

        # Create source document
        source_doc = SourceDocument(
            type=SourceTypeEnum.HTML.value,
            title=title,
            url_or_path=url,
            metadata_=metadata or {},
        )
        self.db.add(source_doc)
        await self.db.flush()

        # Create chunks
        chunks = self._chunk_text(text)
        for chunk in chunks:
            chunk["metadata"]["url"] = url

        # Create chunk records and embeddings
        chunk_ids = await self.embedding_service.add_chunks(
            chunks=chunks,
            source_document_id=source_doc.id,
        )

        for i, chunk_data in enumerate(chunks):
            chunk = SourceChunk(
                id=chunk_ids[i],
                source_document_id=source_doc.id,
                text=chunk_data["text"],
                metadata_=chunk_data["metadata"],
                chunk_index=i,
            )
            self.db.add(chunk)

        await self.db.commit()
        return source_doc, len(chunks)

    async def ingest_yaml_capabilities(
        self,
        file_path: Path,
    ) -> tuple[int, int, int]:
        """Ingest capabilities from a YAML file.

        YAML format:
        labs:
          - name: "Lab Name"
            institution: "Institution"
            facilities:
              - name: "Facility Name"
                capabilities:
                  - name: "Capability Name"
                    description: "..."
                    modalities: [...]
                    ...

        Returns:
            Tuple of (labs_created, facilities_created, capabilities_created)
        """
        with open(file_path) as f:
            data = yaml.safe_load(f)

        labs_created = 0
        facilities_created = 0
        capabilities_created = 0
        chunk_counter = 0  # Track chunk index across all capabilities

        # Check if source document with same path already exists
        result = await self.db.execute(
            select(SourceDocument).where(
                SourceDocument.url_or_path == str(file_path)
            )
        )
        existing_doc = result.scalar_one_or_none()

        if existing_doc:
            # Delete old chunks from ChromaDB
            await self.embedding_service.delete_document_chunks(existing_doc.id)
            # Delete old source document (will cascade to capabilities via foreign key)
            await self.db.delete(existing_doc)
            await self.db.flush()

        # Create source document for provenance
        source_doc = SourceDocument(
            type=SourceTypeEnum.YAML.value,
            title=f"Capability Import: {file_path.name}",
            url_or_path=str(file_path),
        )
        self.db.add(source_doc)
        await self.db.flush()

        for lab_data in data.get("labs", []):
            # Check if lab exists
            result = await self.db.execute(
                select(Lab).where(
                    Lab.name == lab_data["name"],
                    Lab.institution == lab_data.get("institution", ""),
                )
            )
            lab = result.scalar_one_or_none()

            if not lab:
                lab = Lab(
                    name=lab_data["name"],
                    institution=lab_data.get("institution", ""),
                    location=lab_data.get("location"),
                    contacts=lab_data.get("contacts"),
                    urls=lab_data.get("urls"),
                    description=lab_data.get("description"),
                )
                self.db.add(lab)
                await self.db.flush()
                labs_created += 1

            for facility_data in lab_data.get("facilities", []):
                # Check if facility exists
                result = await self.db.execute(
                    select(Facility).where(
                        Facility.lab_id == lab.id,
                        Facility.name == facility_data["name"],
                    )
                )
                facility = result.scalar_one_or_none()

                if not facility:
                    facility = Facility(
                        lab_id=lab.id,
                        name=facility_data["name"],
                        description=facility_data.get("description"),
                    )
                    self.db.add(facility)
                    await self.db.flush()
                    facilities_created += 1

                for cap_data in facility_data.get("capabilities", []):
                    capability = Capability(
                        facility_id=facility.id,
                        name=cap_data["name"],
                        description=cap_data.get("description"),
                        modalities=cap_data.get("modalities"),
                        throughput=cap_data.get("throughput"),
                        sample_requirements=cap_data.get("sample_requirements"),
                        constraints=cap_data.get("constraints"),
                        typical_outputs=cap_data.get("typical_outputs"),
                        readiness_level=cap_data.get("readiness_level"),
                        tags=cap_data.get("tags"),
                        source_document_id=source_doc.id,
                    )
                    self.db.add(capability)
                    capabilities_created += 1

                    # Also create a chunk for this capability for search
                    cap_text = f"{cap_data['name']}: {cap_data.get('description', '')}"
                    if cap_data.get("modalities"):
                        cap_text += f" Modalities: {', '.join(cap_data['modalities'])}."
                    if cap_data.get("tags"):
                        cap_text += f" Tags: {', '.join(cap_data['tags'])}."

                    chunk_metadata = {
                        "type": "capability",
                        "capability_name": cap_data["name"],
                        "facility_name": facility_data["name"],
                        "lab_name": lab_data["name"],
                        "chunk_index": chunk_counter,
                    }

                    # Add to vector store and get generated IDs
                    chunk_ids = await self.embedding_service.add_chunks(
                        chunks=[{"text": cap_text, "metadata": chunk_metadata}],
                        source_document_id=source_doc.id,
                    )

                    chunk = SourceChunk(
                        id=chunk_ids[0],
                        source_document_id=source_doc.id,
                        text=cap_text,
                        metadata_=chunk_metadata,
                        chunk_index=chunk_counter,
                    )
                    self.db.add(chunk)
                    chunk_counter += 1

        await self.db.commit()
        return labs_created, facilities_created, capabilities_created


def get_ingestion_service(db: AsyncSession) -> IngestionService:
    """Get an ingestion service instance."""
    return IngestionService(db)
