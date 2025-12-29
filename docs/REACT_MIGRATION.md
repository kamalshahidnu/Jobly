## React Migration (Phase 2)

Jobly Phase 1 ships with a Streamlit UI for fast iteration. Phase 2 aims to add a React frontend that talks to the FastAPI backend.

### Goals

- Create a modern web UI (React + TypeScript) for:
  - Profile management
  - Job search + ranking
  - Document generation
  - Outreach workflows
  - Analytics dashboards
- Keep business logic in the backend services/agents so both Streamlit and React share the same core.

### Recommended approach

1. Stabilize the API surface under `/api/v1/*`
2. Add authentication (Phase 2)
3. Build React pages that mirror the Streamlit page structure:
   - Dashboard, Jobs, Profile, Networking, Documents, Interviews, Analytics
4. Incrementally replace Streamlit features while keeping it as an admin/dev UI

### Notes

- The current `frontend/` folder is intentionally minimal.
- When the API contracts are stable, generate a typed client from OpenAPI.

