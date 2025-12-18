"""Embedding service using CBORG API."""

import hashlib
import json
from pathlib import Path
from typing import Optional

import chromadb
import httpx
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings


class EmbeddingService:
    """Service for generating and managing embeddings via CBORG."""

    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[httpx.AsyncClient] = None
        self._chroma_client: Optional[chromadb.Client] = None
        self._collection: Optional[chromadb.Collection] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.settings.anthropic_base_url,
                headers={
                    "Authorization": f"Bearer {self.settings.anthropic_auth_token}",
                    "Content-Type": "application/json",
                },
                timeout=120.0,  # Increased timeout for embedding API
            )
        return self._client

    @property
    def chroma_client(self) -> chromadb.Client:
        """Lazy initialization of ChromaDB client."""
        if self._chroma_client is None:
            persist_dir = Path(self.settings.chroma_persist_dir)
            persist_dir.mkdir(parents=True, exist_ok=True)
            self._chroma_client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        return self._chroma_client

    @property
    def collection(self) -> chromadb.Collection:
        """Get or create the source chunks collection."""
        if self._collection is None:
            self._collection = self.chroma_client.get_or_create_collection(
                name="source_chunks",
                metadata={"description": "OPAL source document chunks"},
            )
        return self._collection

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text using CBORG API."""
        response = await self.client.post(
            "/v1/embeddings",
            json={
                "model": self.settings.embedding_model,
                "input": text,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []

        response = await self.client.post(
            "/v1/embeddings",
            json={
                "model": self.settings.embedding_model,
                "input": texts,
            },
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    def _generate_chunk_id(self, source_document_id: str, chunk_index: int, text: str = "") -> str:
        """Generate a deterministic ID for a chunk."""
        # Include text hash to ensure uniqueness even with same index
        content = f"{source_document_id}:{chunk_index}:{text[:100]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def add_chunks(
        self,
        chunks: list[dict],
        source_document_id: str,
    ) -> list[str]:
        """Add chunks to the vector store.

        Args:
            chunks: List of dicts with 'text' and optional 'metadata'
            source_document_id: ID of the source document

        Returns:
            List of chunk IDs
        """
        if not chunks:
            return []

        texts = [c["text"] for c in chunks]
        embeddings = await self.generate_embeddings(texts)

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = self._generate_chunk_id(source_document_id, i, chunk["text"])
            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadata = chunk.get("metadata", {}) or {}
            metadata["source_document_id"] = source_document_id
            metadata["chunk_index"] = i
            metadatas.append(metadata)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        return ids

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict] = None,
    ) -> list[dict]:
        """Search for similar chunks.

        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters (e.g., {"lab_id": "..."})

        Returns:
            List of search results with id, text, score, and metadata
        """
        query_embedding = await self.generate_embedding(query)

        where_filter = None
        if filters:
            where_filter = {k: v for k, v in filters.items() if v is not None}
            if not where_filter:
                where_filter = None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                search_results.append({
                    "id": chunk_id,
                    "text": results["documents"][0][i] if results["documents"] else "",
                    "score": 1 - results["distances"][0][i] if results["distances"] else 0,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                })

        return search_results

    async def delete_document_chunks(self, source_document_id: str) -> int:
        """Delete all chunks for a source document."""
        results = self.collection.get(
            where={"source_document_id": source_document_id},
            include=["metadatas"],
        )

        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            return len(results["ids"])
        return 0

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
