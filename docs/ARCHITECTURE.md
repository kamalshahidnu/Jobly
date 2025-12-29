# Jobly Architecture

## Overview

Jobly is a multi-agent AI system for automating job search workflows. The architecture follows a modular, service-oriented design.

## System Architecture

```
┌─────────────────────────────────────────────┐
│          User Interfaces                    │
│  ┌─────────────┐      ┌──────────────┐     │
│  │  Streamlit  │      │     CLI      │     │
│  │     UI      │      │  (Optional)  │     │
│  └──────┬──────┘      └──────┬───────┘     │
│         │                    │              │
└─────────┼────────────────────┼──────────────┘
          │                    │
┌─────────┼────────────────────┼──────────────┐
│         │  Services Layer    │              │
│  ┌──────▼────────────────────▼───────┐     │
│  │  Profile | Job | Outreach | Doc   │     │
│  │  Service | Svc | Service  | Svc   │     │
│  └──────┬────────────────────┬───────┘     │
│         │                    │              │
└─────────┼────────────────────┼──────────────┘
          │                    │
┌─────────┼────────────────────┼──────────────┐
│         │   Agent Layer      │              │
│  ┌──────▼────────────────────▼───────┐     │
│  │        17 Specialized Agents       │     │
│  │  Profile | Job Search | Ranker     │     │
│  │  Resume  | Cover Letter | Contact  │     │
│  │  Outreach| Application  | Tracker  │     │
│  │  And more...                        │     │
│  └──────┬────────────────────┬───────┘     │
│         │                    │              │
└─────────┼────────────────────┼──────────────┘
          │                    │
┌─────────┼────────────────────┼──────────────┐
│         │   Data Layer       │              │
│  ┌──────▼────────────────────▼───────┐     │
│  │  SQLite | Vector Store | Memory   │     │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Key Components

### 1. User Interfaces

#### Streamlit UI (Phase 1)
- Primary interface for Phase 1
- Fast prototyping and iteration
- Python-based, integrated with backend
- 7 main pages: Dashboard, Jobs, Profile, Networking, Documents, Interviews, Analytics

#### CLI (Optional)
- Command-line interface for power users
- Automation and scripting
- Batch operations

### 2. Services Layer

Shared business logic used by all interfaces:

- **ProfileService** - Profile management and resume parsing
- **JobService** - Job discovery and management
- **OutreachService** - Contact management and messaging
- **DocumentService** - Resume and cover letter generation
- **AnalyticsService** - Metrics and insights

### 3. Agent Layer

17 specialized AI agents:

1. **ProfileAgent** - Parse resumes, build profiles
2. **JobSearchAgent** - Search job boards
3. **DedupAgent** - Remove duplicate jobs
4. **JobRankerAgent** - Rank jobs by fit
5. **AnalyticsAgent** - Generate insights
6. **ResumeTailorAgent** - Tailor resumes
7. **CoverLetterAgent** - Generate cover letters
8. **ContactDiscoveryAgent** - Find hiring managers
9. **OutreachWriterAgent** - Write messages
10. **FollowupAgent** - Manage follow-ups
11. **ApplicationAgent** - Submit applications
12. **AssessmentAgent** - Handle assessments
13. **EmailMonitorAgent** - Monitor emails
14. **InterviewPrepAgent** - Prepare for interviews
15. **TrackerAgent** - Track status
16. **ErrorHandlerAgent** - Handle errors
17. **OfferEvalAgent** - Evaluate offers

### 4. Orchestration

- **AgentCoordinator** - Manages agent execution
- **StateMachine** - Workflow state management
- **ApprovalGates** - Human-in-the-loop control

### 5. Data Layer

- **SQLite** - Primary data storage
- **VectorStore** - Semantic search (future)
- **SharedMemory** - Inter-agent communication

## Design Principles

1. **Modularity** - Each agent is independent and focused
2. **Extensibility** - Easy to add new agents or features
3. **Human-in-the-loop** - Approval gates for critical actions
4. **Service-oriented** - Shared services for consistency
5. **Data-driven** - Analytics and feedback loops

## Technology Stack

- **Language:** Python 3.11+
- **UI Framework:** Streamlit (Phase 1), React (Phase 2)
- **AI:** OpenAI GPT-4 or Anthropic Claude
- **Database:** SQLite (dev), PostgreSQL (production)
- **Async:** asyncio
- **Testing:** pytest
- **Deployment:** Docker

## Workflows

### Job Application Workflow

```
1. Profile Parsing → 2. Job Search → 3. Deduplication
         ↓                                    ↓
4. Job Ranking ← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
         ↓
5. Resume Tailoring → 6. Cover Letter → 7. [Approval Gate]
         ↓                                    ↓
8. Application Submit → 9. Track Status → 10. Analytics
```

### Networking Workflow

```
1. Contact Discovery → 2. Profile Enrichment → 3. Outreach Message
         ↓                                            ↓
4. [Approval Gate] → 5. Send Message → 6. Follow-up Scheduling
         ↓                                            ↓
7. Track Responses → 8. Analytics
```

## Scalability

- Agents can run in parallel
- Rate limiting for API calls
- Queue-based processing for batch jobs
- Horizontal scaling with multiple instances

## Security

- API keys stored in environment variables
- No sensitive data in logs
- User data encrypted at rest
- OAuth for third-party integrations
