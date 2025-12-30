# Jobly Implementation Guide

This guide documents all the implemented features and provides setup instructions for the Jobly AI-powered job search automation platform.

## 🎉 What's Been Implemented

### 1. LLM Integration ✅

**Location:** `backend/jobly/utils/llm.py`, `backend/jobly/agents/base.py`

**Features:**
- Unified LLM client supporting both OpenAI and Anthropic (Claude)
- Automatic provider selection based on available API keys
- Async and sync completion methods
- Multi-turn chat support
- Graceful fallback to deterministic logic when LLM unavailable

**Integrated Agents:**
- `CoverLetterAgent` - Generates personalized cover letters using LLM
- `InterviewPrepAgent` - Creates tailored interview prep materials
- `OutreachWriterAgent` - Drafts professional networking messages

**Usage:**
```python
from jobly.utils.llm import get_llm_client

# Get LLM client (auto-selects provider based on API keys)
llm = get_llm_client()

# Generate completion
response = await llm.acomplete(
    prompt="Write a cover letter for...",
    system="You are an expert career counselor",
    temperature=0.7
)
```

### 2. Job Board Scraping ✅

**Location:** `backend/jobly/tools/job_boards/`

**Implemented Scrapers:**

#### Indeed Scraper
- Full job search with filters (keywords, location, job type, experience level)
- Pagination support
- Job detail extraction
- Automatic skill and requirement parsing
- Rate limiting built-in

```python
from jobly.tools.job_boards.indeed_scraper import IndeedScraper

scraper = IndeedScraper()
jobs = scraper.search_jobs(
    keywords="Software Engineer",
    location="Remote",
    job_type="fulltime",
    limit=50
)
```

#### Glassdoor Scraper
- Job search functionality
- Company rating retrieval
- Salary information extraction
- Rate limiting

```python
from jobly.tools.job_boards.glassdoor_scraper import GlassdoorScraper

scraper = GlassdoorScraper()
jobs = scraper.search_jobs(
    keywords="Data Scientist",
    location="San Francisco",
    limit=30
)
```

#### LinkedIn API Client
- OAuth2 authentication flow
- Profile retrieval
- Company information lookup
- Seed job support for development
- Helper functions for URL generation

```python
from jobly.tools.job_boards.linkedin_api import LinkedInAPIClient

client = LinkedInAPIClient(
    access_token="your_token",
    client_id="your_client_id",
    client_secret="your_secret"
)

# Search with seed jobs for testing
jobs = client.search_jobs(
    keywords="Product Manager",
    location="New York",
    seed_jobs=seed_data
)
```

### 3. Gmail/Email Monitoring ✅

**Location:** `backend/jobly/tools/gmail_client.py`

**Features:**
- OAuth2 authentication with Google
- Email fetching with query support
- Email categorization (interview, offer, rejection, etc.)
- Label management
- Job-specific email search
- Mark as read/unread
- Full email body extraction

**Usage:**
```python
from jobly.tools.gmail_client import GmailClient

gmail = GmailClient(credentials_path="path/to/credentials.json")

# Search for job-related emails
emails = gmail.search_job_emails(days_back=30)

# Categorize emails
for email in emails:
    category = gmail.categorize_email(email)
    print(f"Email: {email['subject']} - Category: {category}")

# Add labels
gmail.add_label(email['id'], "Jobly/Interview")
```

### 4. Vector Store for Semantic Search ✅

**Location:** `backend/jobly/memory/vector_store.py`

**Features:**
- Sentence-transformers based embeddings
- Cosine similarity search
- Persistent storage
- Batch operations
- Helper functions for job search

**Usage:**
```python
from jobly.memory.vector_store import VectorStore, add_job_to_vector_store, search_jobs_semantic

# Initialize vector store
vector_store = VectorStore(model_name="all-MiniLM-L6-v2")

# Add jobs
for job in jobs:
    add_job_to_vector_store(vector_store, job)

# Semantic search
results = search_jobs_semantic(
    vector_store,
    query="machine learning engineer with python and tensorflow",
    top_k=20,
    min_score=0.3
)
```

### 5. React Frontend ✅

The Streamlit UI has been removed. All UI functionality is implemented in the React frontend under `frontend/`.

## 📋 Setup Instructions

### 1. Install Dependencies

```bash
cd backend
poetry install

# For optional features:
poetry add sentence-transformers  # For vector search
```

### 2. Configure API Keys

Create a `.env` file in the backend directory:

```env
# LLM APIs (at least one required)
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Gmail API (optional)
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json

# LinkedIn API (optional)
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token

# SMTP for sending emails (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Database
DATABASE_URL=sqlite:///./jobly.db
```

### 3. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials.json
6. Set `GMAIL_CREDENTIALS_PATH` in .env

On first run, it will open a browser for OAuth consent.

### 4. LinkedIn API Setup

LinkedIn's job search API requires partnership access. For development:

1. Apply for [LinkedIn Partner Program](https://business.linkedin.com/talent-solutions)
2. OR use seed jobs for testing
3. OR manually collect job data via authorized means

### 5. Run the Application

#### React Frontend

```bash
cd frontend
npm install
npm run dev
```

#### FastAPI Backend
```bash
cd backend
poetry run uvicorn jobly.api.main:app --reload
```

#### CLI
```bash
poetry run jobly --help
```

## 🧪 Testing

Run the existing tests:

```bash
poetry run pytest
```

### Test Coverage Status

**Tested:**
- ✅ ProfileAgent
- ✅ JobRankerAgent
- ✅ JobService
- ✅ PDFParser

**Missing Tests (need implementation):**
- JobSearchAgent, DedupAgent, AnalyticsAgent
- ResumeTailorAgent, CoverLetterAgent, ContactDiscoveryAgent
- OutreachWriterAgent, FollowupAgent, ApplicationAgent
- AssessmentAgent, EmailMonitorAgent, InterviewPrepAgent
- TrackerAgent, ErrorHandlerAgent, OfferEvalAgent
- Other services (ProfileService, OutreachService, etc.)

## 🔄 Workflow Examples

### Complete Job Search Flow

```python
import asyncio
from jobly.tools.job_boards.indeed_scraper import IndeedScraper
from jobly.agents.dedup_agent import DedupAgent
from jobly.agents.job_ranker_agent import JobRankerAgent
from jobly.services.job_service import JobService

async def search_and_rank_jobs():
    # 1. Search jobs from Indeed
    scraper = IndeedScraper()
    jobs = scraper.search_jobs(
        keywords="Python Developer",
        location="Remote",
        limit=50
    )

    # 2. Deduplicate
    dedup_agent = DedupAgent()
    result = await dedup_agent.execute({"jobs": jobs})
    unique_jobs = result["deduplicated_jobs"]

    # 3. Rank by fit
    ranker = JobRankerAgent()
    user_profile = {
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_years": 5,
        "location": "Remote"
    }
    result = await ranker.execute({
        "jobs": unique_jobs,
        "profile": user_profile
    })
    ranked_jobs = result["ranked_jobs"]

    # 4. Save to database
    job_service = JobService()
    for job in ranked_jobs:
        job_service.create_job({
            "user_id": "user123",
            "title": job["title"],
            "company": job["company"],
            "description": job["description"],
            "url": job["url"],
            "match_score": job.get("match_score", 0)
        })

    return ranked_jobs

# Run
asyncio.run(search_and_rank_jobs())
```

### Email Monitoring Flow

```python
from jobly.tools.gmail_client import GmailClient
from jobly.agents.email_monitor_agent import EmailMonitorAgent

# Initialize
gmail = GmailClient()
monitor = EmailMonitorAgent()

# Fetch job-related emails
emails = gmail.search_job_emails(days_back=7)

# Categorize and process
async def process_emails():
    result = await monitor.execute({"emails": emails})

    for email in result["categorized_emails"]:
        category = email["category"]
        if category == "interview":
            print(f"Interview request from {email['from']}")
            # Trigger interview prep agent
        elif category == "offer":
            print(f"Job offer from {email['from']}")
            # Trigger offer evaluation agent

asyncio.run(process_emails())
```

### Document Generation Flow

```python
from jobly.agents.cover_letter_agent import CoverLetterAgent
from jobly.agents.resume_tailor_agent import ResumeTailorAgent

async def generate_application_docs():
    # User profile
    profile = {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "Machine Learning", "AWS"],
        "experience_years": 5
    }

    # Target job
    job = {
        "title": "Senior ML Engineer",
        "company": "TechCorp",
        "description": "Looking for experienced ML engineer...",
        "requirements": ["Python", "TensorFlow", "AWS"]
    }

    # Generate cover letter
    cover_letter_agent = CoverLetterAgent()
    cl_result = await cover_letter_agent.execute({
        "profile": profile,
        "job": job
    })
    cover_letter = cl_result["cover_letter"]

    # Tailor resume
    resume_agent = ResumeTailorAgent()
    resume_result = await resume_agent.execute({
        "profile": profile,
        "job": job
    })
    tailored_resume = resume_result["tailored_resume"]

    return cover_letter, tailored_resume

cover_letter, resume = asyncio.run(generate_application_docs())
```

## 🚀 What's Left to Implement

### High Priority

1. **Approval Gates**
   - Human-in-the-loop workflow system
   - UI components for approval
   - State management for pending actions

2. **Multi-User Authentication**
   - User registration and login
   - JWT token management
   - User-specific data isolation
   - Password hashing and security

3. **Comprehensive Test Suite**
   - Add tests for 13 missing agents
   - Integration tests
   - Service layer tests
   - End-to-end tests

4. **Complete FastAPI Endpoints**
   - Connect routes to services
   - Add request/response validation
   - Implement error handling
   - Add API documentation

### Medium Priority

1. **Remaining UI Pages**
   - Profile page integration
   - Networking page integration
   - Documents page integration
   - Interviews page integration
   - Analytics page integration

2. **Advanced Analytics**
   - Response rate tracking
   - Interview success metrics
   - Offer acceptance rates
   - Time-to-hire analytics

3. **Enhanced Job Search**
   - More job board integrations
   - Custom company website scraping
   - Job alert notifications
   - Saved search functionality

### Low Priority

1. **Company Research Agent**
   - Automated company information gathering
   - Culture analysis
   - Funding and growth metrics

2. **Salary Negotiation Assistant**
   - Market salary analysis
   - Negotiation strategy generation
   - Offer comparison matrices

3. **Career Path Planning**
   - Skill gap analysis
   - Learning recommendations
   - Career trajectory modeling

## 📚 Architecture Overview

```
┌─────────────────────────────────────────────┐
│           User Interfaces                    │
│  (React UI, CLI, FastAPI REST API)          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           Services Layer                     │
│  (JobService, ProfileService, etc.)         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Agent Orchestration                  │
│  (17 Specialized AI Agents)                 │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      Data & External Integrations           │
│  (SQLite, Vector Store, Job Boards, Gmail)  │
└─────────────────────────────────────────────┘
```

## 🎯 Key Files Reference

### Core Utilities
- `backend/jobly/utils/llm.py` - LLM client
- `backend/jobly/agents/base.py` - Base agent with LLM support
- `backend/jobly/memory/vector_store.py` - Semantic search
- `backend/jobly/memory/sqlite_store.py` - Database operations

### Job Board Integrations
- `backend/jobly/tools/job_boards/indeed_scraper.py` - Indeed scraper
- `backend/jobly/tools/job_boards/glassdoor_scraper.py` - Glassdoor scraper
- `backend/jobly/tools/job_boards/linkedin_api.py` - LinkedIn client

### Email Integration
- `backend/jobly/tools/gmail_client.py` - Gmail API client

### UI
- React frontend: `frontend/`

### Configuration
- `backend/jobly/config/settings.py` - Application settings
- `backend/.env` - Environment variables

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'sentence_transformers'"
```bash
poetry add sentence-transformers
```

### "LLM client not configured"
Set either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in your `.env` file.

### "Gmail client not authenticated"
1. Set up Gmail API credentials (see Gmail API Setup section)
2. Run the application - it will open a browser for OAuth
3. Grant permissions
4. Token will be saved for future use

### Indeed/Glassdoor returning empty results
- These scrapers depend on HTML structure which may change
- Be respectful of rate limits
- Consider using job board APIs where available

## 🔐 Security Notes

1. **Never commit API keys** - Use `.env` files
2. **Rate limiting** - All scrapers include rate limiting
3. **OAuth tokens** - Stored securely in `~/.jobly/`
4. **SQL injection** - Services use parameterized queries
5. **TOS compliance** - Respect job board terms of service

## 📈 Performance Tips

1. **Batch operations** - Use batch methods for vector store operations
2. **Async/await** - All agents are async for better performance
3. **Rate limiting** - Respect external API limits
4. **Caching** - Consider caching job search results
5. **Database indexing** - Add indexes for frequently queried fields

## 🤝 Contributing

When adding new features:

1. Follow existing patterns (agents, services, tools)
2. Add type hints
3. Write docstrings
4. Add tests
5. Update this guide

## 📞 Support

For issues or questions:
- Check the codebase documentation
- Review agent implementations for examples
- Check integration examples above

---

**Last Updated:** 2025-12-30
**Version:** 0.1.0
**Status:** Functional with core features implemented
