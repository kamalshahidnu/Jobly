# Jobly Documentation

Welcome to the Jobly documentation!

## Table of Contents

1. [Architecture](ARCHITECTURE.md) - System architecture and design
2. [Agents](AGENTS.md) - AI agent documentation
3. [API](API.md) - API reference and endpoints
4. [React Migration](REACT_MIGRATION.md) - React frontend implementation details

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI or Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jobly.git
cd jobly

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Build and run with Docker
docker-compose up -d

# Access the application at:
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

```bash
# Backend
cd backend
poetry install
poetry run uvicorn jobly.api.main:app --reload

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

## Project Structure

```
jobly/
├── backend/          # Python FastAPI backend
│   ├── jobly/       # Main package
│   │   ├── agents/  # 17 AI agents
│   │   ├── api/     # FastAPI routes & endpoints
│   │   ├── auth/    # Authentication & JWT
│   │   ├── models/  # Data models
│   │   ├── services/# Service layer
│   │   └── memory/  # SQLite storage
│   └── tests/       # Tests
├── frontend/        # React + TypeScript UI
│   ├── src/        # React components
│   └── public/     # Static assets
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
