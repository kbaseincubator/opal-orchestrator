#!/usr/bin/env python3
"""CLI for ingesting documents into the OPAL knowledge base."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.models.database import async_session_maker, init_db, close_db
from app.services.ingestion import get_ingestion_service


async def ingest_pdf(args):
    """Ingest a PDF document."""
    file_path = Path(args.path)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1

    await init_db()

    async with async_session_maker() as session:
        ingestion_service = get_ingestion_service(session)
        source_doc, num_chunks = await ingestion_service.ingest_pdf(
            file_path=file_path,
            title=args.title,
            metadata={"description": args.description} if args.description else None,
        )
        print(f"Successfully ingested '{args.title}'")
        print(f"  Document ID: {source_doc.id}")
        print(f"  Chunks created: {num_chunks}")
        await ingestion_service.close_connections()

    await close_db()

    return 0


async def ingest_url(args):
    """Ingest a web page."""
    await init_db()

    async with async_session_maker() as session:
        ingestion_service = get_ingestion_service(session)
        source_doc, num_chunks = await ingestion_service.ingest_url(
            url=args.url,
            title=args.title,
            metadata={"description": args.description} if args.description else None,
        )
        print(f"Successfully ingested '{args.title}' from URL")
        print(f"  Document ID: {source_doc.id}")
        print(f"  Chunks created: {num_chunks}")
        await ingestion_service.close_connections()

    await close_db()

    return 0


async def ingest_yaml(args):
    """Ingest capabilities from a YAML file."""
    file_path = Path(args.path)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1

    await init_db()

    async with async_session_maker() as session:
        ingestion_service = get_ingestion_service(session)
        labs, facilities, capabilities = await ingestion_service.ingest_yaml_capabilities(
            file_path=file_path,
        )
        print(f"Successfully ingested capabilities from '{file_path.name}'")
        print(f"  Labs created: {labs}")
        print(f"  Facilities created: {facilities}")
        print(f"  Capabilities created: {capabilities}")
        await ingestion_service.close_connections()

    await close_db()

    return 0


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OPAL Orchestrator Ingestion CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest a PDF document
  python -m cli.ingest pdf --path /path/to/doc.pdf --title "OPAL Proposal"

  # Ingest a web page
  python -m cli.ingest url --url https://example.com --title "Lab Website"

  # Ingest capabilities from YAML
  python -m cli.ingest yaml --path /path/to/capabilities.yaml
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # PDF subcommand
    pdf_parser = subparsers.add_parser("pdf", help="Ingest a PDF document")
    pdf_parser.add_argument("--path", required=True, help="Path to PDF file")
    pdf_parser.add_argument("--title", required=True, help="Document title")
    pdf_parser.add_argument("--description", help="Optional description")

    # URL subcommand
    url_parser = subparsers.add_parser("url", help="Ingest a web page")
    url_parser.add_argument("--url", required=True, help="URL to ingest")
    url_parser.add_argument("--title", required=True, help="Document title")
    url_parser.add_argument("--description", help="Optional description")

    # YAML subcommand
    yaml_parser = subparsers.add_parser("yaml", help="Ingest capabilities from YAML")
    yaml_parser.add_argument("--path", required=True, help="Path to YAML file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "pdf":
        await ingest_pdf(args)
    elif args.command == "url":
        await ingest_url(args)
    elif args.command == "yaml":
        await ingest_yaml(args)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
