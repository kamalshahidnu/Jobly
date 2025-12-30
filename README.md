# Jobly 💼

> AI-Powered Job Search Automation Platform

Jobly is an intelligent job search automation system that uses 17 specialized AI agents to handle every aspect of your job search - from resume parsing to interview preparation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🤖 **17 AI Agents** - Specialized agents for every job search task
- 🔐 **Multi-User Authentication** - JWT tokens with secure password hashing
- 📄 **Resume Parsing** - Automatically extract profile from your resume
- 🔍 **Multi-Source Job Search** - Search LinkedIn, Indeed, Glassdoor
- 🎯 **Semantic Job Matching** - Vector-based matching using sentence-transformers
- ✍️ **Document Generation** - AI-powered cover letters and resume tailoring
- ✅ **Approval Workflows** - Human-in-the-loop gates for critical actions
- 📊 **Application Tracking** - Monitor all applications in one place
- 📈 **Analytics Dashboard** - Real-time insights and metrics
- 🔔 **Email Monitoring** - Gmail integration with OAuth2
- 🎤 **Interview Prep** - AI-generated preparation materials
- 🐳 **Docker Deployment** - Containerized for easy deployment

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   React + TypeScript Frontend       │
│   Material-UI | React Router        │
└──────────────┬──────────────────────┘
               │ REST API
┌──────────────▼──────────────────────┐
│      FastAPI Backend (Python)       │
│  Authentication | Routes | CORS     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    17 Specialized AI Agents         │
│  + Approval Gates & Workflows       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  SQLite | Vector Store | Memory     │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 18+
- Poetry (for dependency management)
- OpenAI or Anthropic API key

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/jobly.git
cd Jobly
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start the backend:**
```bash
cd backend
poetry install
poetry run uvicorn jobly.api.main:app --reload
```

4. **Start the frontend (in a new terminal):**
```bash
cd frontend
npm install
npm run dev
```

5. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Using Docker

```bash
# Build and start all services
docker-compose up -d

# Access at:
# - Frontend: http://localhost
# - Backend: http://localhost:8000

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [AI Agents Guide](docs/AGENTS.md)
- [API Reference](docs/API.md)
- [React Migration Guide](docs/REACT_MIGRATION.md)

## 🎯 Usage

### 1. Upload Your Resume

Navigate to the **Profile** page and upload your resume. Jobly will automatically parse and extract your information.

### 2. Search for Jobs

Go to the **Jobs** page, enter your search criteria, and let AI agents search multiple job boards simultaneously.

### 3. Review Ranked Jobs

Jobs are automatically ranked based on your profile. Review top matches and select jobs to apply to.

### 4. Generate Documents

For each job, Jobly can generate a tailored resume and cover letter optimized for that specific position.

### 5. Network Strategically

Discover hiring managers and recruiters at target companies. Generate personalized outreach messages.

### 6. Track Applications

Monitor all your applications, interviews, and offers in the centralized dashboard.

### 7. Analyze Performance

View analytics on response rates, interview conversion, and optimize your strategy.

## 🤖 AI Agents

| Agent | Function |
|-------|----------|
| ProfileAgent | Parse resumes and build profiles |
| JobSearchAgent | Search job boards |
| DedupAgent | Remove duplicate listings |
| JobRankerAgent | Rank jobs by fit |
| AnalyticsAgent | Generate insights |
| ResumeTailorAgent | Customize resumes |
| CoverLetterAgent | Write cover letters |
| ContactDiscoveryAgent | Find hiring managers |
| OutreachWriterAgent | Craft messages |
| FollowupAgent | Manage follow-ups |
| ApplicationAgent | Submit applications |
| AssessmentAgent | Handle assessments |
| EmailMonitorAgent | Track emails |
| InterviewPrepAgent | Prepare for interviews |
| TrackerAgent | Update application status |
| ErrorHandlerAgent | Handle errors |
| OfferEvalAgent | Evaluate job offers |

## 🛠️ Development

### Running Tests

```bash
cd backend
poetry run pytest
```

### Code Quality

```bash
# Format code
poetry run black .

# Lint
poetry run ruff check .

# Type checking
poetry run mypy jobly
```

## 🗺️ Roadmap

### Phase 1: Core Backend ✅
- ✅ 17 AI agent framework
- ✅ LLM integration (OpenAI + Anthropic)
- ✅ Job board scrapers
- ✅ Vector store with semantic search
- ✅ Gmail OAuth2 integration

### Phase 2: Authentication & Workflows ✅
- ✅ JWT authentication system
- ✅ Multi-user support
- ✅ Approval gate workflows
- ✅ FastAPI endpoints
- ✅ Comprehensive test coverage

### Phase 3: React Frontend ✅
- ✅ React + TypeScript + Material-UI
- ✅ Authentication UI
- ✅ Job search interface
- ✅ Approval workflow UI
- ✅ Dashboard with analytics
- ✅ Docker deployment

### Phase 4: Advanced Features (Next)
- ⬜ Real-time notifications
- ⬜ Email/SMS alerts
- ⬜ Browser extension
- ⬜ Mobile app (React Native)
- ⬜ Advanced ML insights
- ⬜ Calendar integration
- ⬜ ATS system integration

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

Jobly is a tool to assist with job searching. Always review AI-generated content before sending. Respect website terms of service when scraping. Use responsibly and ethically.

## 🙏 Acknowledgments

Built with:
- [OpenAI GPT-4](https://openai.com/)
- [Anthropic Claude](https://www.anthropic.com/)
- [React](https://react.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

Made with ❤️ by the Jobly team
