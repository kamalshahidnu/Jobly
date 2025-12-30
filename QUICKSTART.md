# Jobly Quick Start Guide

Get up and running with Jobly (React + FastAPI) in 5 minutes using Docker!

## Prerequisites

- Docker and Docker Compose
- API key for Anthropic Claude or OpenAI (for AI features)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/jobly.git
cd Jobly
```

### 2. Configure API Keys

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key (choose one):
# Option A: Anthropic Claude (Recommended)
ANTHROPIC_API_KEY=your_key_here

# Option B: OpenAI GPT
OPENAI_API_KEY=your_key_here
```

Get API keys:
- **Anthropic Claude**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys

### 3. Run the Application

```bash
# Build and start services
docker compose -f docker/docker-compose.full.yml up --build -d

# Check status
docker compose -f docker/docker-compose.full.yml ps
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## First Steps

### 1. Create an Account

1. Open http://localhost in your browser
2. Click "Sign Up" or navigate to the Register page
3. Enter your details (name, email, password)
4. Click "Register"
5. You'll be automatically logged in

### 2. Search for Jobs

1. Click on "Jobs" in the navigation
2. Enter search criteria:
   - Keywords (e.g., "Software Engineer", "Python Developer")
   - Location (e.g., "Remote", "San Francisco, CA")
   - Job type, experience level, etc.
3. Click "Search Jobs"

The system will:
- Search multiple job boards (Indeed, Glassdoor, LinkedIn)
- Remove duplicates automatically
- Rank jobs by fit based on your profile
- Display results with key details

### 3. Build Your Profile

1. Click on "Profile" in the navigation
2. Upload your resume (PDF or DOCX)
3. The AI will automatically parse and extract:
   - Skills and technologies
   - Work experience
   - Education
   - Contact information
4. Review and edit as needed

### 4. Generate Documents

1. Navigate to "Documents" page
2. Select a job you want to apply to
3. Choose document type:
   - Cover Letter
   - Tailored Resume
4. Click "Generate with AI"
5. Review and edit the generated document
6. Approve or regenerate if needed

### 5. Track Applications

1. Go to "Jobs" page
2. Click "Apply" on a job listing
3. Upload required documents or use AI-generated ones
4. Track application status in the dashboard
5. Add notes and follow-up reminders

## Key Features

### AI-Powered Automation
- **17 Specialized AI Agents** - Each agent handles a specific task (job search, ranking, document generation, etc.)
- **Multi-Source Job Search** - Search LinkedIn, Indeed, and Glassdoor simultaneously
- **Semantic Matching** - Vector-based job matching using sentence transformers
- **Document Generation** - AI-generated cover letters and tailored resumes

### Human-in-the-Loop
- **Approval Gates** - Review and approve AI-generated content before sending
- **Bulk Operations** - Approve multiple actions at once
- **Custom Edits** - Edit any AI-generated content before approval

### Application Tracking
- **Centralized Dashboard** - View all applications in one place
- **Status Tracking** - Track applications through the entire process
- **Interview Preparation** - AI-generated prep materials for each interview
- **Analytics** - Insights into your job search performance

## Common Commands

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View running containers
docker-compose ps
```

### Local Development

```bash
# Backend
cd backend
poetry install
poetry run uvicorn jobly.api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Run tests
cd backend
poetry run pytest

# Run with coverage
poetry run pytest --cov=jobly --cov-report=term-missing
```

## Troubleshooting

### Cannot access frontend at localhost

1. Check if containers are running: `docker-compose ps`
2. View logs: `docker-compose logs frontend`
3. Restart services: `docker-compose restart`

### "Registration failed" error

1. Check backend logs: `docker-compose logs backend`
2. Verify .env file has correct API keys
3. Rebuild containers: `docker-compose up -d --build backend`

### Backend API errors

1. Make sure API keys are set in `.env`:
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
2. Check backend is running: `curl http://localhost:8000/health`
3. View API docs: http://localhost:8000/docs

### Job search returns no results

1. Check your internet connection
2. Be patient - scraping takes time
3. Try different keywords
4. Respect rate limits (wait between searches)

## What's Included

✅ **Fully Implemented:**
- React + TypeScript frontend with Material-UI
- JWT authentication and multi-user support
- 17 specialized AI agents
- Multi-source job search (LinkedIn, Indeed, Glassdoor)
- Semantic job matching with vector search
- AI-powered document generation (cover letters, resumes)
- Approval gate workflows with human-in-the-loop
- Application tracking and analytics dashboard
- Docker deployment with Nginx
- FastAPI backend with OpenAPI docs

## Getting Help

1. Check the [docs/](docs/) folder for detailed documentation
2. View API documentation: http://localhost:8000/docs
3. Review [REACT_MIGRATION.md](docs/REACT_MIGRATION.md) for frontend details
4. Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
5. See [API.md](docs/API.md) for API reference

## Next Steps

1. ✅ Complete this quick start guide
2. 📖 Explore the [documentation](docs/) for detailed information
3. 🎯 Set up your profile and start searching for jobs
4. 🤖 Let the AI agents work for you
5. 📊 Track your progress in the analytics dashboard

## Tips for Success

- **Be specific in job searches** - Use detailed keywords and locations
- **Review AI-generated content** - Always review before approving
- **Keep your profile updated** - Better profile = better job matches
- **Use approval gates** - Review bulk actions before submitting
- **Track everything** - Use the dashboard to monitor progress

Happy job hunting! 🎯
