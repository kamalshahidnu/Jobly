# Jobly Backend

Python backend for the Jobly job search automation platform.

## Structure

```
jobly/
├── agents/          # 17 AI agents
├── api/             # FastAPI routes (Phase 2)
├── config/          # Configuration
├── memory/          # Storage layer
├── models/          # Data models
├── orchestrator/    # Agent coordination
├── services/        # Business logic
├── tools/           # Utility tools
├── ui/              # Streamlit & CLI
└── utils/           # Helper functions
```

## Installation

```bash
# Install with Poetry
poetry install

# Or with pip
pip install -e .
```

## Running

### Streamlit UI

```bash
poetry run streamlit run jobly/ui/streamlit/app.py
```

### CLI

```bash
# Show help
poetry run jobly --help

# Search jobs
poetry run jobly search jobs -k "Software Engineer" -l "Remote"

# View stats
poetry run jobly analytics stats
```

### API (Phase 2)

```bash
poetry run uvicorn jobly.api.main:app --reload
```

## Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=jobly

# Specific test file
poetry run pytest tests/test_agents/test_profile_agent.py
```

## Development

```bash
# Format code
poetry run black .

# Lint
poetry run ruff check .

# Type checking
poetry run mypy jobly
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
DATABASE_URL=sqlite:///./jobly.db
```

## Key Components

### Agents

17 specialized AI agents handle different aspects of job search:

- **ProfileAgent** - Resume parsing
- **JobSearchAgent** - Job discovery
- **JobRankerAgent** - Match scoring
- **ResumeTailorAgent** - Resume customization
- And 13 more...

### Services

Shared business logic:

- **JobService** - Job operations
- **ProfileService** - Profile management
- **OutreachService** - Networking
- **DocumentService** - Document generation
- **AnalyticsService** - Metrics

### Tools

Utility modules:

- **PDFParser** - Resume extraction
- **DocGenerator** - Document creation
- **GmailClient** - Email integration
- **LinkedInClient** - LinkedIn scraping
- **WebScraper** - General scraping

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
