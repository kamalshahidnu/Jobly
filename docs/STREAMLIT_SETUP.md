## Streamlit Setup

Jobly’s Phase 1 UI is a Streamlit app located at `backend/jobly/ui/streamlit/app.py`.

### Prerequisites

- Python 3.10+
- Poetry installed (`pipx install poetry` recommended)

### Install + run

From repo root:

```bash
cd backend
poetry install
poetry run streamlit run jobly/ui/streamlit/app.py --server.port=8501
```

Or use the helper script:

```bash
./scripts/run_streamlit.sh
```

### Database

By default, Jobly uses SQLite at `./jobly.db` (repo root).

To initialize schema:

```bash
python scripts/migrate_db.py
python scripts/seed_data.py
```

### Common issues

- If Streamlit can’t import `jobly`, make sure you are running it via `poetry run ...` from `backend/`.
- If you want email sending from the outreach flow, set SMTP environment variables in `.env`:
  - `SMTP_SERVER`, `SMTP_USERNAME`, `SMTP_PASSWORD` (and optional `SMTP_PORT`)

