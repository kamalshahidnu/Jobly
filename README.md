# Jobly 💼

> AI-Powered Job Search Automation Platform

Jobly is an intelligent job search automation system that uses 17 specialized AI agents to handle every aspect of your job search - from resume parsing to interview preparation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🤖 **17 AI Agents** - Specialized agents for every job search task
- 📄 **Resume Parsing** - Automatically extract profile from your resume
- 🔍 **Multi-Source Job Search** - Search LinkedIn, Indeed, Glassdoor, and more
- 🎯 **Smart Job Ranking** - AI matches jobs to your profile
- ✍️ **Document Generation** - Auto-tailor resumes and cover letters
- 🤝 **Networking Automation** - Discover contacts and craft outreach messages
- 📊 **Application Tracking** - Monitor all your applications in one place
- 📈 **Analytics Dashboard** - Get insights on your job search performance
- 🔔 **Email Monitoring** - Track responses and follow-ups
- 🎤 **Interview Prep** - AI-generated preparation materials

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│       Streamlit UI (Phase 1)        │
│   or React Frontend (Phase 2)       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Services Layer              │
│  Profile | Jobs | Outreach | Docs   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    17 Specialized AI Agents         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  SQLite | Vector Store | Memory     │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- OpenAI or Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jobly.git
cd jobly

# Install dependencies
cd backend
poetry install

# Copy environment template
cp ../.env.example ../.env
# Edit .env and add your API keys

# Initialize database
poetry run python ../scripts/setup_db.py

# Run Streamlit UI
poetry run streamlit run jobly/ui/streamlit/app.py
```

Visit `http://localhost:8501` to access the Jobly interface.

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose -f docker/docker-compose.streamlit.yml up

# Access at http://localhost:8501
```

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [AI Agents Guide](docs/AGENTS.md)
- [API Reference](docs/API.md)
- [Streamlit Setup](docs/STREAMLIT_SETUP.md)
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

### Phase 1: Streamlit UI (Current)
- ✅ Core agent framework
- ✅ Streamlit interface
- ✅ Basic workflow automation
- 🔄 Advanced features

### Phase 2: React Frontend
- ⬜ FastAPI backend activation
- ⬜ React TypeScript frontend
- ⬜ Enhanced UX/UI
- ⬜ Real-time updates

### Phase 3: Advanced Features
- ⬜ Multi-user support
- ⬜ Company research agent
- ⬜ Salary negotiation assistant
- ⬜ Career path planning

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
- [Streamlit](https://streamlit.io/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

Made with ❤️ by the Jobly team
