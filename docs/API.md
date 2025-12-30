## Jobly API

The Jobly backend exposes a small FastAPI application primarily for programmatic access and future React frontend integration.

### Running locally

From repo root:

```bash
cd backend
poetry install
poetry run uvicorn jobly.api.main:app --reload --port 8000
```

Then visit:
- `http://localhost:8000/` (welcome)
- `http://localhost:8000/health` (health)
- `http://localhost:8000/docs` (OpenAPI / Swagger)

### Endpoints (v1)

#### Jobs

- `POST /api/v1/jobs/`: create a job
- `GET /api/v1/jobs/`: list jobs
- `GET /api/v1/jobs/{job_id}`: fetch one job
- `PUT /api/v1/jobs/{job_id}`: update job
- `DELETE /api/v1/jobs/{job_id}`: delete job
- `GET /api/v1/jobs/search/?q=...`: search jobs

#### Profile

- `POST /api/v1/profile/`: create a profile
- `GET /api/v1/profile/{user_id}`: fetch profile
- `PUT /api/v1/profile/{user_id}`: update profile
- `POST /api/v1/profile/parse-resume`: upload a resume and extract profile fields

#### Agents

- `POST /api/v1/agents/execute/{agent_name}`: execute an agent (e.g. `profile_agent`, `JobRankerAgent`)
- `POST /api/v1/agents/workflow/execute`: execute a list of agents in order
- `GET /api/v1/agents/status/{agent_name}`: get agent state (Phase 1 is always "idle")
- `GET /api/v1/agents/list`: list agent names

### Notes

- The API is designed as a RESTful interface for the React frontend.
- Authentication is required for all endpoints except `/auth/*`.
- For persistence, the service layer uses a lightweight SQLite schema created automatically on connect.

