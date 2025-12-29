## Jobly Agents

Jobly is organized around small, focused agents that each do one part of the job-search workflow. Agents are implemented under `backend/jobly/agents/`.

### Conventions

- Each agent inherits from `BaseAgent` and implements `async def execute(self, input_data)`.
- Agents are stateless by default but may store lightweight state in `self.state`.
- Agents return dictionaries shaped like:
  - `{"status": "success", ...}`
  - `{"status": "error", "error": "...", ...}`

### Available agents (Phase 1)

- `ProfileAgent`: parse resume text into structured fields
- `JobSearchAgent`: filter/search seed jobs based on criteria
- `DedupAgent`: remove duplicates from job lists
- `JobRankerAgent`: score jobs for profile fit
- `ResumeTailorAgent`: tailor resume content for a job (lightweight)
- `CoverLetterAgent`: generate cover letter text (lightweight)
- `ContactDiscoveryAgent`: demo contact discovery (seed-based)
- `OutreachWriterAgent`: draft outreach messages
- `FollowupAgent`: suggest follow-ups
- `ApplicationAgent`: demo submission flow (no real ATS integration yet)
- `AssessmentAgent`: assessment helper
- `EmailMonitorAgent`: monitoring scaffold
- `InterviewPrepAgent`: interview prep scaffold
- `TrackerAgent`: track workflow status
- `AnalyticsAgent`: basic insights scaffold
- `ErrorHandlerAgent`: normalize errors
- `OfferEvalAgent`: offer evaluation scaffold

### Executing agents via API

See `docs/API.md` for the `/api/v1/agents/*` endpoints.

### Adding a new agent

1. Create `backend/jobly/agents/<my_agent>.py`
2. Implement a `BaseAgent` subclass with `execute()`
3. Register it in `backend/jobly/api/routes/agents.py` so it’s available via API workflows

