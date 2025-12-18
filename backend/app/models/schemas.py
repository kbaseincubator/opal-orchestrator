"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ============ Enums ============

class SourceTypeEnum(str, Enum):
    """Types of source documents."""
    PDF = "pdf"
    HTML = "html"
    DOC = "doc"
    YAML = "yaml"
    MANUAL = "manual"


class ResourceTypeEnum(str, Enum):
    """Types of resources."""
    STRAIN = "strain"
    LIBRARY = "library"
    INSTRUMENT = "instrument"
    ASSAY = "assay"
    DATASET = "dataset"
    OTHER = "other"


# ============ Lab Schemas ============

class LabBase(BaseModel):
    """Base schema for Lab."""
    name: str
    institution: str
    location: Optional[str] = None
    contacts: Optional[dict] = None
    urls: Optional[dict] = None
    description: Optional[str] = None


class LabCreate(LabBase):
    """Schema for creating a Lab."""
    pass


class LabResponse(LabBase):
    """Schema for Lab response."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Facility Schemas ============

class FacilityBase(BaseModel):
    """Base schema for Facility."""
    name: str
    description: Optional[str] = None


class FacilityCreate(FacilityBase):
    """Schema for creating a Facility."""
    lab_id: str


class FacilityResponse(FacilityBase):
    """Schema for Facility response."""
    id: str
    lab_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Capability Schemas ============

class CapabilityBase(BaseModel):
    """Base schema for Capability."""
    name: str
    description: Optional[str] = None
    modalities: Optional[list[str]] = None
    throughput: Optional[str] = None
    sample_requirements: Optional[dict] = None
    constraints: Optional[dict] = None
    typical_outputs: Optional[list[str]] = None
    readiness_level: Optional[str] = None
    tags: Optional[list[str]] = None


class CapabilityCreate(CapabilityBase):
    """Schema for creating a Capability."""
    facility_id: str
    source_document_id: Optional[str] = None


class CapabilityResponse(CapabilityBase):
    """Schema for Capability response."""
    id: str
    facility_id: str
    source_document_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CapabilityWithContext(CapabilityResponse):
    """Capability with lab and facility context."""
    facility_name: str
    lab_name: str
    lab_institution: str


# ============ Protocol Schemas ============

class ProtocolBase(BaseModel):
    """Base schema for Protocol."""
    title: str
    summary: Optional[str] = None
    inputs: Optional[list[str]] = None
    outputs: Optional[list[str]] = None
    constraints: Optional[dict] = None


class ProtocolCreate(ProtocolBase):
    """Schema for creating a Protocol."""
    facility_id: str
    source_document_id: Optional[str] = None
    excerpt_offsets: Optional[dict] = None


class ProtocolResponse(ProtocolBase):
    """Schema for Protocol response."""
    id: str
    facility_id: str
    source_document_id: Optional[str] = None
    excerpt_offsets: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Resource Schemas ============

class ResourceBase(BaseModel):
    """Base schema for Resource."""
    type: ResourceTypeEnum
    name: str
    description: Optional[str] = None
    access_constraints: Optional[dict] = None
    metadata_: Optional[dict] = Field(None, alias="metadata")


class ResourceCreate(ResourceBase):
    """Schema for creating a Resource."""
    lab_id: str
    source_document_id: Optional[str] = None


class ResourceResponse(ResourceBase):
    """Schema for Resource response."""
    id: str
    lab_id: str
    source_document_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


# ============ Source Document Schemas ============

class SourceDocumentBase(BaseModel):
    """Base schema for SourceDocument."""
    type: SourceTypeEnum
    title: str
    url_or_path: str
    metadata_: Optional[dict] = Field(None, alias="metadata")


class SourceDocumentCreate(SourceDocumentBase):
    """Schema for creating a SourceDocument."""
    pass


class SourceDocumentResponse(SourceDocumentBase):
    """Schema for SourceDocument response."""
    id: str
    ingested_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


# ============ Source Chunk Schemas ============

class SourceChunkBase(BaseModel):
    """Base schema for SourceChunk."""
    text: str
    metadata_: Optional[dict] = Field(None, alias="metadata")
    chunk_index: int = 0


class SourceChunkCreate(SourceChunkBase):
    """Schema for creating a SourceChunk."""
    source_document_id: str


class SourceChunkResponse(SourceChunkBase):
    """Schema for SourceChunk response."""
    id: str
    source_document_id: str
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


# ============ Search Schemas ============

class SearchQuery(BaseModel):
    """Schema for capability search query."""
    query: str
    filters: Optional[dict] = None
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    """Schema for search result."""
    chunk_id: str
    source_document_id: str
    source_title: str
    text: str
    score: float
    metadata: Optional[dict] = None


class CapabilitySearchResult(BaseModel):
    """Schema for capability search result."""
    capability: CapabilityWithContext
    relevance_score: float
    source_chunks: list[SearchResult]


# ============ Chat Schemas ============

class ChatMessage(BaseModel):
    """Schema for a chat message."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str
    conversation_id: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: str
    conversation_id: str
    plan: Optional["OPALPlan"] = None
    sources: list[SearchResult] = []


# ============ Plan Schemas ============

class Citation(BaseModel):
    """Citation for a capability recommendation."""
    source_document_id: str
    chunk_id: Optional[str] = None
    quote: str
    source_title: Optional[str] = None


class PlanStep(BaseModel):
    """A step in the OPAL resource deployment plan."""
    step_id: str
    objective: str
    recommended_facility: str
    capability_ids: list[str] = []
    inputs: list[str] = []
    outputs: list[str] = []
    constraints: list[str] = []
    dependencies: list[str] = []  # step_ids this step depends on
    decision_points: list[str] = []
    citations: list[Citation] = []
    is_hypothesis: bool = False  # True if not backed by sources


class RiskItem(BaseModel):
    """Risk or alternative for the plan."""
    risk: str
    impact: str
    alternative: Optional[str] = None


class OPALPlan(BaseModel):
    """Complete OPAL Resource Deployment Plan."""
    goal_summary: str
    assumptions: list[str] = []
    steps: list[PlanStep] = []
    open_questions: list[str] = []
    risks_and_alternatives: list[RiskItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============ Ingestion Schemas ============

class IngestPDFRequest(BaseModel):
    """Schema for PDF ingestion request."""
    title: str
    description: Optional[str] = None


class IngestURLRequest(BaseModel):
    """Schema for URL ingestion request."""
    url: str
    title: str
    description: Optional[str] = None


class IngestResponse(BaseModel):
    """Schema for ingestion response."""
    source_document_id: str
    chunks_created: int
    message: str


# Update forward references
ChatResponse.model_rebuild()
