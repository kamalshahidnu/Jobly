# React Frontend Implementation

Jobly now features a complete React + TypeScript frontend with Material-UI, replacing the previous Streamlit UI.

## Overview

The React frontend is a modern single-page application (SPA) that communicates with the FastAPI backend via REST APIs.

### Technology Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for components and styling
- **React Router** for navigation
- **Axios** for HTTP requests
- **Vite** as the build tool
- **JWT** for authentication

## Architecture

### Frontend Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Main application pages
│   ├── services/       # API service layer
│   ├── contexts/       # React contexts (Auth, etc.)
│   ├── types/          # TypeScript type definitions
│   └── App.tsx         # Root application component
├── public/             # Static assets
├── index.html          # Entry HTML
└── vite.config.ts      # Vite configuration
```

### Main Pages

1. **Dashboard** - Overview of job search activity and metrics
2. **Jobs** - Search, browse, and manage job listings
3. **Profile** - Manage user profile and resume
4. **Outreach** - Contact management and networking
5. **Documents** - Resume and cover letter generation
6. **Interviews** - Interview preparation and tracking
7. **Analytics** - Insights and performance metrics

### Authentication Flow

1. User registers/logs in via `/auth/register` or `/auth/login`
2. Backend returns JWT access token
3. Frontend stores token in localStorage
4. All subsequent API requests include `Authorization: Bearer <token>` header
5. Token is validated by FastAPI middleware

### API Integration

The frontend communicates with the backend through RESTful APIs:

```typescript
// Example: Fetching jobs
import api from '../services/api';

const fetchJobs = async () => {
  const response = await api.get('/api/v1/jobs');
  return response.data;
};
```

The `api` service automatically includes authentication headers and handles token refresh.

### Approval Workflows

The frontend implements human-in-the-loop approval workflows for critical actions:

- Application submissions require user approval
- Outreach messages must be reviewed before sending
- Document generation shows previews for editing
- Bulk operations have confirmation dialogs

## Development

### Local Development

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` with hot module replacement.

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Docker Deployment

The frontend is containerized with Nginx:

```bash
docker-compose up -d
```

Access the application at `http://localhost`.

## Features Implemented

### Authentication
- ✅ User registration with email validation
- ✅ JWT-based login
- ✅ Protected routes
- ✅ Automatic token refresh
- ✅ Logout functionality

### Profile Management
- ✅ View and edit user profile
- ✅ Resume upload and parsing
- ✅ Skills and experience management

### Job Search
- ✅ Multi-source job search (LinkedIn, Indeed, Glassdoor)
- ✅ Job listing display with details
- ✅ Job ranking and filtering
- ✅ Save/bookmark jobs

### Document Generation
- ✅ AI-powered cover letter generation
- ✅ Resume tailoring for specific jobs
- ✅ Document preview and editing

### Application Tracking
- ✅ View all applications
- ✅ Track application status
- ✅ Update application notes

### Approval Gates
- ✅ Review AI-generated documents
- ✅ Approve/reject outreach messages
- ✅ Confirm application submissions

### Analytics
- ✅ Dashboard with key metrics
- ✅ Application success rate
- ✅ Job source breakdown
- ✅ Timeline visualizations

## Migration from Streamlit

The Streamlit UI has been completely removed from the codebase. All UI functionality is now implemented in the React frontend:

### Removed
- `backend/jobly/ui/streamlit/` - Entire Streamlit UI directory
- `docker/Dockerfile.streamlit` - Streamlit Docker configuration
- `docker/docker-compose.streamlit.yml` - Streamlit compose file
- `scripts/run_streamlit.sh` - Streamlit startup script
- `docs/STREAMLIT_SETUP.md` - Streamlit documentation

### Benefits of React Migration

1. **Better Performance** - SPA with client-side rendering
2. **Improved UX** - Smooth navigation without page reloads
3. **Mobile Responsive** - Works on all device sizes
4. **Modern UI** - Material-UI provides a polished look
5. **TypeScript** - Type safety catches errors early
6. **Production Ready** - Optimized builds with Vite

## API Documentation

The backend API is fully documented with OpenAPI/Swagger:

- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

You can use the interactive docs to test API endpoints directly.

## Future Enhancements

- [ ] Real-time notifications with WebSockets
- [ ] Advanced search filters and saved searches
- [ ] Drag-and-drop document editing
- [ ] Calendar integration for interviews
- [ ] Mobile app (React Native)
- [ ] Progressive Web App (PWA) support
