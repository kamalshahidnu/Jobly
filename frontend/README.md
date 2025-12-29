# Jobly Frontend (Phase 2)

This directory is reserved for the React-based frontend that will be built in Phase 2.

## Phase 1: Streamlit UI

For Phase 1, we're using Streamlit for the UI. See `backend/jobly/ui/streamlit/` for the current implementation.

## Phase 2: React Frontend (Future)

The React frontend will provide:
- Modern, responsive UI
- Better performance and UX
- Advanced features and customization
- Progressive Web App (PWA) capabilities

### Planned Tech Stack

- **Framework:** React 18 with TypeScript
- **State Management:** Redux Toolkit or Zustand
- **Styling:** Tailwind CSS
- **API Client:** Axios with React Query
- **Routing:** React Router v6
- **Forms:** React Hook Form
- **Charts:** Recharts or Chart.js
- **Build Tool:** Vite

### Getting Started (Future)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Migration Path

When migrating from Streamlit to React:

1. The backend API (FastAPI) will be fully enabled
2. Services layer remains unchanged (shared between Streamlit and React)
3. Streamlit UI can be kept as an alternative interface
4. Both UIs can coexist during transition period
