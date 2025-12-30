# Jobly Frontend

React + TypeScript frontend for Jobly.

## Getting started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## API integration

- **Dev**: defaults to `http://localhost:8000` unless you set `VITE_API_URL`
- **Docker**: frontend uses same-origin requests (`/api/...`) and nginx proxies to the backend container

## Notes

See `docs/REACT_MIGRATION.md` for background.
