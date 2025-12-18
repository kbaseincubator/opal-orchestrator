# OPAL Orchestrator

A web-based chatbot that helps scientists plan cross-lab biological research projects across the OPAL (Organized Production of Agile Livelihoods) network.

## Features

- **Conversational Interface**: Describe your research goal in natural language and iteratively refine it
- **Capability Registry**: RAG-based search over OPAL lab capabilities, facilities, and protocols
- **Research Plan Generation**: Structured plans with sequenced steps, dependencies, and citations
- **Multi-Source Ingestion**: Import PDFs, web pages, and YAML capability definitions
- **Citation Tracking**: Every recommendation is backed by source documents

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- LBL CBORG API access (for LLM and embeddings)

### Environment Setup

1. Clone the repository:
```bash
cd opal-orchestrator
```

2. Copy the environment template:
```bash
cp .env.example .env
```

3. Edit `.env` and add your CBORG API credentials:
```env
ANTHROPIC_BASE_URL=https://api.cborg.lbl.gov
ANTHROPIC_AUTH_TOKEN=your_cborg_api_key_here
```

### Option 1: Run with Docker Compose

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Run Locally

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Seed the Capability Registry

Before using the chatbot, load the seed data:

```bash
cd backend
python -m cli.ingest yaml --path ../scripts/seed_data/capabilities.yaml
```

This loads 15+ capability cards from OPAL member labs.

## Usage

### Chat Interface

1. Open http://localhost:3000
2. Describe your research goal in the chat panel
3. Answer any clarifying questions from the assistant
4. Review the generated plan in the center panel
5. See source citations in the right panel
6. Export the plan as JSON or Markdown

### Example Research Goal

> "I want to develop a microbial strain/consortium that is root-associated, drought tolerant, and produces a targeted plant hormone and an antifungal compound."

The assistant will:
- Ask clarifying questions about organism, plant system, constraints
- Search the capability registry for relevant facilities
- Generate a sequenced research plan with dependencies
- Provide citations for each recommendation

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send a chat message |
| `/capabilities/search` | GET | Search capabilities |
| `/labs` | GET | List OPAL labs |
| `/ingest/pdf` | POST | Upload and ingest a PDF |
| `/ingest/url` | POST | Ingest a web page |
| `/ingest/yaml` | POST | Import capabilities from YAML |
| `/sources` | GET | List source documents |
| `/sources/{id}/chunks` | GET | Get document chunks |
| `/health` | GET | Health check |

Full API documentation: http://localhost:8000/docs

### CLI Commands

```bash
# Ingest a PDF document
python -m cli.ingest pdf --path /path/to/doc.pdf --title "Document Title"

# Ingest a web page
python -m cli.ingest url --url https://example.com --title "Page Title"

# Import capabilities from YAML
python -m cli.ingest yaml --path /path/to/capabilities.yaml
```

## Evaluation

Run the evaluation harness to test the planner:

```bash
cd scripts
python run_eval.py
```

This runs 10 test cases and generates reports:
- `eval_output/eval_report.json` - Machine-readable results
- `eval_output/eval_report.md` - Human-readable summary

## Architecture

```
opal-orchestrator/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models + Pydantic schemas
│   │   ├── services/       # Business logic
│   │   │   ├── chat.py     # Chat orchestration
│   │   │   ├── planner.py  # Plan generation
│   │   │   ├── embeddings.py # Vector embeddings
│   │   │   ├── retrieval.py  # RAG search
│   │   │   └── ingestion.py  # Document ingestion
│   │   ├── routers/        # API endpoints
│   │   └── mcp/            # MCP/A2A stubs for extensibility
│   └── cli/                # CLI tools
├── frontend/               # Next.js frontend
│   └── src/
│       ├── components/     # React components
│       │   ├── Chat/       # Chat panel
│       │   ├── Plan/       # Plan viewer
│       │   └── Sources/    # Citation viewer
│       └── lib/            # API client
├── scripts/                # Evaluation + seed data
└── data/                   # Runtime data (SQLite, ChromaDB, PDFs)
```

## Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, ChromaDB
- **Frontend**: Next.js 14, React 18, Tailwind CSS
- **LLM**: LBL CBORG (Anthropic-compatible API)
- **Embeddings**: CBORG lbl/nomic-embed-text
- **Database**: SQLite (MVP), upgradable to PostgreSQL

## Extensibility

The architecture includes stubs for future integrations:

- **MCP (Model Context Protocol)**: Plugin interface for external tools
- **A2A (Agent-to-Agent)**: Communication with lab experiment agents
- **Data Lakehouse**: Queries to BER centralized data storage

See `backend/app/mcp/stubs.py` for interface definitions.

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Style

- Python: Follow PEP 8, use type hints
- TypeScript: ESLint + Prettier

## License

Internal OPAL project - see project governance for usage terms.

## Acknowledgments

Built for the OPAL (Organized Production of Agile Livelihoods) network, a DOE BER-funded cross-lab initiative for sustainable biomanufacturing research.
