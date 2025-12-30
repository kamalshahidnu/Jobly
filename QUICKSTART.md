# Jobly Quick Start Guide

Get up and running with Jobly in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)
- API key for Anthropic Claude or OpenAI (for AI features)

## Installation

### 1. Clone and Setup

```bash
cd Jobly/backend
poetry install
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
# Start Streamlit UI (Recommended)
cd jobly/ui/streamlit
streamlit run app.py
```

Your browser should open to `http://localhost:8501`

## First Steps

### 1. Search for Jobs

1. Click on "💼 Jobs" in the sidebar
2. Replace the default page with the connected version:
   ```bash
   cp pages/2_💼_Jobs_Connected.py pages/2_💼_Jobs.py
   ```
3. Restart Streamlit
4. Enter search criteria (e.g., "Software Engineer", "Remote")
5. Click "Search Jobs"

The system will:
- Search Indeed (and optionally Glassdoor)
- Remove duplicates
- Rank jobs by fit
- Save results to database

### 2. Generate Documents

```python
# Example: Generate cover letter
import asyncio
from jobly.agents.cover_letter_agent import CoverLetterAgent

async def generate():
    agent = CoverLetterAgent()
    result = await agent.execute({
        "profile": {
            "name": "John Doe",
            "skills": ["Python", "React", "AWS"],
            "experience_years": 5
        },
        "job": {
            "title": "Senior Software Engineer",
            "company": "TechCorp",
            "description": "Looking for experienced engineer..."
        }
    })
    print(result["cover_letter"])

asyncio.run(generate())
```

### 3. Monitor Emails (Optional)

If you set up Gmail API:

```python
from jobly.tools.gmail_client import GmailClient

gmail = GmailClient(credentials_path="path/to/credentials.json")
emails = gmail.search_job_emails(days_back=30)

for email in emails:
    category = gmail.categorize_email(email)
    print(f"{email['subject']} - {category}")
```

## Example Workflows

### Complete Job Search

```python
import asyncio
from jobly.tools.job_boards.indeed_scraper import IndeedScraper
from jobly.agents.dedup_agent import DedupAgent
from jobly.agents.job_ranker_agent import JobRankerAgent

async def search():
    # Search Indeed
    scraper = IndeedScraper()
    jobs = scraper.search_jobs(
        keywords="Python Developer",
        location="Remote",
        limit=30
    )
    print(f"Found {len(jobs)} jobs")

    # Deduplicate
    dedup = DedupAgent()
    result = await dedup.execute({"jobs": jobs})
    unique_jobs = result["deduplicated_jobs"]
    print(f"{len(unique_jobs)} unique jobs")

    # Rank by fit
    ranker = JobRankerAgent()
    result = await ranker.execute({
        "jobs": unique_jobs,
        "profile": {
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience_years": 5
        }
    })

    # Display top matches
    for job in result["ranked_jobs"][:5]:
        print(f"{job['title']} at {job['company']} - Score: {job['match_score']}")

asyncio.run(search())
```

### Semantic Job Search

```python
from jobly.memory.vector_store import VectorStore, add_job_to_vector_store, search_jobs_semantic

# Initialize vector store (first time downloads model)
vector_store = VectorStore()

# Add jobs
for job in jobs:
    add_job_to_vector_store(vector_store, job)

# Semantic search
results = search_jobs_semantic(
    vector_store,
    query="machine learning engineer with python and tensorflow experience",
    top_k=10
)

for job in results:
    print(f"{job['title']} - Similarity: {job.get('similarity_score', 0):.2f}")
```

## Common Commands

```bash
# Run Streamlit UI
cd backend/jobly/ui/streamlit
streamlit run app.py

# Run FastAPI backend
cd backend
poetry run uvicorn jobly.api.main:app --reload

# Run CLI
poetry run jobly --help

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=jobly --cov-report=term-missing
```

## Troubleshooting

### "No module named 'sentence_transformers'"

Install for semantic search:
```bash
poetry add sentence-transformers
```

### "LLM client not configured"

Make sure you've set either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in your `.env` file.

### Job search returns no results

1. Check your internet connection
2. Be patient - scraping takes time
3. Try different keywords
4. Respect rate limits (wait between searches)

### "Gmail client not authenticated"

See the Gmail API setup section in [IMPLEMENTATION_GUIDE.md](backend/IMPLEMENTATION_GUIDE.md).

## What Works Now

✅ **Core Features Implemented:**
- AI-powered cover letter generation
- Interview preparation materials
- Networking message generation
- Job board scraping (Indeed, Glassdoor)
- Gmail email monitoring
- Semantic job search
- Job deduplication
- Job ranking by fit
- Vector-based search
- Streamlit UI example

## What's Next

🚧 **In Progress:**
- Full UI integration for all pages
- Multi-user authentication
- Approval gate workflows
- Complete test coverage
- Enhanced analytics

See [IMPLEMENTATION_GUIDE.md](backend/IMPLEMENTATION_GUIDE.md) for detailed documentation.

## Getting Help

1. Check [IMPLEMENTATION_GUIDE.md](backend/IMPLEMENTATION_GUIDE.md) for detailed docs
2. Review example code in this guide
3. Check agent implementations in `backend/jobly/agents/`
4. Read docstrings in the code

## Project Structure

```
backend/
├── jobly/
│   ├── agents/          # 17 AI agents (all implemented)
│   ├── services/        # Business logic layer
│   ├── tools/           # External integrations
│   │   ├── job_boards/  # Indeed, Glassdoor, LinkedIn
│   │   └── gmail_client.py
│   ├── memory/          # Database and vector store
│   ├── utils/           # LLM client and helpers
│   ├── ui/              # Streamlit UI
│   └── api/             # FastAPI routes
├── tests/               # Test suite
├── .env                 # Your configuration
└── IMPLEMENTATION_GUIDE.md  # Detailed documentation
```

## Quick Examples by Use Case

### "I want to search for jobs"
→ Use the Streamlit Jobs page (see step 1 above)

### "I need a cover letter"
→ Use `CoverLetterAgent` (see example above)

### "I want to track emails"
→ Use `GmailClient` (see example above)

### "I need interview prep"
→ Use `InterviewPrepAgent`:
```python
from jobly.agents.interview_prep_agent import InterviewPrepAgent

agent = InterviewPrepAgent()
result = await agent.execute({
    "interviews": [{
        "job_title": "Senior Engineer",
        "company": "TechCorp",
        "job_description": "...",
        "user_profile": {...}
    }]
})
```

### "I want semantic search"
→ Use `VectorStore` (see example above)

## Performance Tips

- Job scraping can take 10-30 seconds per source
- LLM responses take 2-5 seconds
- Vector store searches are very fast (<100ms)
- Use batch operations when possible
- Respect rate limits to avoid blocking

## Next Steps

1. ✅ Complete this quick start
2. 📖 Read [IMPLEMENTATION_GUIDE.md](backend/IMPLEMENTATION_GUIDE.md) for details
3. 🎨 Customize the UI for your needs
4. 🧪 Add tests for new features
5. 🚀 Deploy to production

Happy job hunting! 🎯
