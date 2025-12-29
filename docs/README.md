# Jobly Documentation

Welcome to the Jobly documentation!

## Table of Contents

1. [Architecture](ARCHITECTURE.md) - System architecture and design
2. [Agents](AGENTS.md) - AI agent documentation
3. [API](API.md) - API reference and endpoints
4. [Streamlit Setup](STREAMLIT_SETUP.md) - Setting up the Streamlit UI
5. [React Migration](REACT_MIGRATION.md) - Migrating to React frontend

## Quick Start

### Prerequisites

- Python 3.10+
- Poetry for dependency management
- OpenAI or Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jobly.git
cd jobly

# Install dependencies
cd backend
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run Streamlit UI
poetry run streamlit run jobly/ui/streamlit/app.py
```

### Using Docker

```bash
# Build and run with docker-compose
docker-compose -f docker/docker-compose.streamlit.yml up
```

## Project Structure

```
jobly/
├── backend/          # Python backend
│   ├── jobly/       # Main package
│   │   ├── agents/  # 17 AI agents
│   │   ├── models/  # Data models
│   │   ├── tools/   # Utility tools
│   │   ├── services/# Service layer
│   │   └── ui/      # User interfaces
│   └── tests/       # Tests
├── frontend/        # React frontend (Phase 2)
├── docker/          # Docker configs
├── docs/            # Documentation
└── data/            # Local data storage
```

## Features

- **Profile Management** - Parse resumes and build profiles
- **Job Discovery** - Multi-source job search and scraping
- **Smart Ranking** - AI-powered job matching
- **Document Generation** - Tailored resumes and cover letters
- **Networking** - Contact discovery and outreach automation
- **Application Tracking** - Monitor applications and interviews
- **Analytics** - Insights and performance metrics

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## License

See [LICENSE](../LICENSE) for license information.
