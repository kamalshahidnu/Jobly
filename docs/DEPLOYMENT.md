# Jobly Deployment Guide

This guide covers deploying Jobly to Render.com with PostgreSQL.

## Prerequisites

- GitHub account with your Jobly repository
- Render.com account (free tier available)
- Anthropic API key

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository has all the configuration files:
- ✅ `render.yaml` in root directory
- ✅ `frontend/Dockerfile` for React app
- ✅ `frontend/nginx.conf` for Nginx configuration
- ✅ `backend/Dockerfile` for FastAPI app
- ✅ `backend/pyproject.toml` with `psycopg2-binary` dependency

**Push your code to GitHub:**
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Sign Up for Render

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### 3. Deploy Using Blueprint

**Option A: Automatic Deployment (Recommended)**

1. In Render Dashboard, click "New +" → "Blueprint"
2. Connect your GitHub repository
3. Render will detect `render.yaml` automatically
4. Click "Apply" to create all services

**Option B: Manual Service Creation**

If automatic deployment doesn't work, create services manually:

#### Create PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Configuration:
   - **Name:** `jobly-db`
   - **Database:** `jobly`
   - **User:** `jobly`
   - **Region:** Choose closest to you
   - **Plan:** Starter ($7/month) or Free
3. Click "Create Database"
4. **Save the Internal Database URL** (you'll need this)

#### Create Backend Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Configuration:
   - **Name:** `jobly-backend`
   - **Region:** Same as database
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./backend/Dockerfile`
   - **Plan:** Starter ($7/month) or Free
4. **Add Environment Variables:**
   ```
   DATABASE_URL=<paste Internal Database URL from step above>
   ANTHROPIC_API_KEY=<your Anthropic API key>
   JWT_SECRET_KEY=<generate a secure random string>
   ENVIRONMENT=production
   DEBUG=false
   ```
5. **Advanced Settings:**
   - Health Check Path: `/health`
6. Click "Create Web Service"
7. **Copy the service URL** (e.g., `https://jobly-backend-xxxxx.onrender.com`)

#### Create Frontend Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Configuration:
   - **Name:** `jobly-frontend`
   - **Region:** Same as backend
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./frontend/Dockerfile`
   - **Plan:** Starter ($7/month) or Free
4. **Add Environment Variables:**
   ```
   VITE_API_BASE_URL=<your backend URL from previous step>
   ```
5. **Build Command (optional):**
   ```bash
   echo "VITE_API_BASE_URL=$VITE_API_BASE_URL" > .env.production
   ```
6. Click "Create Web Service"

### 4. Verify Deployment

1. Wait for all services to deploy (5-10 minutes for first deploy)
2. Check backend: Visit `https://your-backend-url.onrender.com/health`
   - Should return: `{"status":"healthy"}`
3. Check API docs: Visit `https://your-backend-url.onrender.com/docs`
4. Check frontend: Visit `https://your-frontend-url.onrender.com`
5. Try registering a new account

### 5. Set Up Custom Domain (Optional)

#### For Frontend:
1. Go to your frontend service settings
2. Click "Custom Domains"
3. Add your domain (e.g., `jobly.yourdomain.com`)
4. Follow Render's DNS configuration instructions
5. Render automatically provisions SSL certificate

#### For Backend:
1. Go to your backend service settings
2. Add custom domain (e.g., `api.yourdomain.com`)
3. Update frontend `VITE_API_BASE_URL` to use custom domain

### 6. Enable Auto-Deploy

Render automatically deploys when you push to your main branch:

1. Go to each service's "Settings"
2. Ensure "Auto-Deploy" is set to "Yes"
3. Now every `git push` triggers a deployment!

## Environment Variables Reference

### Backend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `ANTHROPIC_API_KEY` | Yes | Anthropic Claude API key | `sk-ant-api03-...` |
| `JWT_SECRET_KEY` | Yes | Secret for JWT tokens | Generate with `openssl rand -hex 32` |
| `ENVIRONMENT` | No | Environment name | `production` |
| `DEBUG` | No | Debug mode | `false` |
| `OPENAI_API_KEY` | No | OpenAI API key (alternative to Anthropic) | `sk-...` |

### Frontend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_BASE_URL` | Yes | Backend API URL | `https://jobly-backend-xxxxx.onrender.com` |

## Cost Breakdown

### Free Tier
- ✅ Backend: Free tier (with spin-down)
- ✅ Frontend: Free tier (with spin-down)
- ❌ PostgreSQL: Free tier available but limited

**Free tier limitations:**
- Services spin down after 15 minutes of inactivity
- Cold start takes 30-60 seconds
- Shared resources

### Paid Tier (Recommended for Production)
- Backend: $7/month (Starter)
- Frontend: $7/month (Starter)
- PostgreSQL: $7/month (Starter)
- **Total: $21/month**

**Benefits:**
- No spin-down
- Better performance
- More resources
- Background workers

## Troubleshooting

### Build Failures

**Problem:** `poetry: command not found`
```bash
# Solution: Ensure backend/Dockerfile has poetry installation
RUN pip install --no-cache-dir poetry
```

**Problem:** `psycopg2 build error`
```bash
# Solution: Use psycopg2-binary in pyproject.toml
psycopg2-binary = "^2.9.9"
```

### Database Connection Issues

**Problem:** `could not connect to server`
```bash
# Solution: Verify DATABASE_URL format
# Render uses: postgresql://user:pass@host:5432/dbname
# Check "Internal Database URL" in database settings
```

**Problem:** `relation "users" does not exist`
```bash
# Solution: Tables are created automatically on first API call
# Try accessing /health endpoint to trigger initialization
```

### Deployment Errors

**Problem:** Service fails health check
```bash
# Solution: Check logs in Render dashboard
# Common issues:
# 1. Wrong port (should be 8000 for backend)
# 2. Missing environment variables
# 3. Database not connected
```

**Problem:** Frontend shows "Failed to fetch"
```bash
# Solution: Check CORS and backend URL
# 1. Verify VITE_API_BASE_URL is correct
# 2. Check backend CORS settings allow frontend domain
# 3. Ensure backend is running (check health endpoint)
```

### Performance Issues

**Problem:** Slow cold starts
```bash
# Solution: Upgrade to paid tier ($7/month)
# Or keep service "warmer" with periodic pings
```

**Problem:** Database connection timeout
```bash
# Solution: Check connection pool settings
# PostgreSQL has connection limits (check your plan)
```

## Monitoring & Logs

### View Logs
1. Go to service in Render dashboard
2. Click "Logs" tab
3. Filter by time range or search

### Metrics
1. Go to service settings
2. Click "Metrics" tab
3. View CPU, memory, requests

### Alerts
1. Go to service settings
2. Click "Alerts"
3. Configure email/Slack notifications

## Backup & Recovery

### Database Backups

Render automatically backs up PostgreSQL databases:
- **Free tier:** No backups
- **Paid tier:** Daily automated backups

**Manual backup:**
```bash
# Install Render CLI
npm install -g @render-com/cli

# Login
render login

# Create backup
render db backup <database-name>
```

### Restore from Backup
1. Go to database in Render dashboard
2. Click "Backups" tab
3. Select backup to restore
4. Click "Restore"

## Scaling

### Vertical Scaling (More Resources)
1. Go to service settings
2. Change "Instance Type"
3. Available plans: Free, Starter, Standard, Pro

### Horizontal Scaling (More Instances)
1. Upgrade to Standard plan or higher
2. Go to service settings
3. Increase "Instances" count
4. Load balancer automatically distributes traffic

## CI/CD Pipeline

Render provides automatic CI/CD:
1. Push code to GitHub
2. Render detects changes
3. Builds new Docker image
4. Runs health checks
5. Deploys if successful
6. Rolls back if failed

### Manual Deploy
```bash
# Trigger manual deploy via Render dashboard
# Or use Render API:
curl -X POST https://api.render.com/v1/services/<service-id>/deploys \
  -H "Authorization: Bearer <your-api-key>"
```

## Security Best Practices

1. **Use Secrets Manager**
   - Store sensitive data in Render's Environment Variables
   - Never commit secrets to git

2. **Enable HTTPS**
   - Render provides free SSL certificates
   - Enforced by default

3. **Database Security**
   - Use strong passwords
   - Limit database connections
   - Use internal URLs for service-to-service communication

4. **API Keys**
   - Rotate keys regularly
   - Use separate keys for dev/staging/prod

5. **CORS Configuration**
   - Only allow your frontend domain
   - Update backend CORS settings

## Next Steps

- [ ] Set up monitoring/alerts
- [ ] Configure custom domain
- [ ] Set up staging environment
- [ ] Add GitHub Actions for testing
- [ ] Configure database backups
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Add analytics (e.g., PostHog, Plausible)

## Support

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **Jobly Issues:** https://github.com/yourusername/jobly/issues
