"""OPAL Orchestrator FastAPI Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.database import init_db
from app.routers import (
    capabilities_router,
    chat_router,
    conversations_router,
    ingest_router,
    sources_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown
    from app.services.embeddings import get_embedding_service
    embedding_service = get_embedding_service()
    await embedding_service.close()


settings = get_settings()

app = FastAPI(
    title="OPAL Orchestrator",
    description="""
OPAL Orchestration Chatbot API

This API provides access to the OPAL (Organized Production of Agile Livelihoods)
Orchestration Assistant, which helps scientists plan cross-lab biological
research projects.

## Features

- **Chat**: Conversational interface for describing research goals and generating plans
- **Capabilities**: Search and browse the OPAL capability registry
- **Ingestion**: Add PDF documents, URLs, and capability definitions to the knowledge base
- **Sources**: Access source documents and citations

## Authentication

For MVP, this API does not require authentication. Production deployments should
implement appropriate security measures.
    """,
    version="0.1.0",
    lifespan=lifespan,
    root_path=settings.root_path,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(capabilities_router)
app.include_router(ingest_router)
app.include_router(sources_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "OPAL Orchestrator API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/labs")
async def list_labs():
    """List all OPAL member labs (convenience endpoint)."""
    from sqlalchemy import select
    from app.models import Lab
    from app.models.database import async_session_maker

    async with async_session_maker() as session:
        result = await session.execute(select(Lab))
        labs = result.scalars().all()
        return [
            {
                "id": lab.id,
                "name": lab.name,
                "institution": lab.institution,
                "location": lab.location,
                "description": lab.description,
                "urls": lab.urls,
                "contacts": lab.contacts,
            }
            for lab in labs
        ]
