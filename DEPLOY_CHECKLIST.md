# Deployment Checklist for Render.com

Follow these steps to deploy Jobly to Render:

## Pre-Deployment

- [ ] Push all code to GitHub
  ```bash
  git add .
  git commit -m "Ready for deployment"
  git push origin main
  ```

- [ ] Verify these files exist:
  - [ ] `render.yaml`
  - [ ] `frontend/Dockerfile`
  - [ ] `frontend/nginx.conf`
  - [ ] `backend/Dockerfile`
  - [ ] `backend/pyproject.toml` (with `psycopg2-binary`)

- [ ] Have your Anthropic API key ready

## Deployment on Render

### Step 1: Create Account
- [ ] Sign up at [render.com](https://render.com)
- [ ] Connect your GitHub account

### Step 2: Deploy via Blueprint
- [ ] Click "New +" → "Blueprint"
- [ ] Select your GitHub repository
- [ ] Click "Apply"

### Step 3: Configure Environment Variables

#### Backend Service:
- [ ] Add `ANTHROPIC_API_KEY` (your API key)
- [ ] Generate `JWT_SECRET_KEY`: `openssl rand -hex 32`
- [ ] Verify `DATABASE_URL` is auto-populated

#### Frontend Service:
- [ ] Add `VITE_API_BASE_URL` (backend URL from Render)

### Step 4: Verify Deployment
- [ ] Backend health: `https://your-backend-url/health`
- [ ] API docs: `https://your-backend-url/docs`
- [ ] Frontend loads: `https://your-frontend-url`
- [ ] Test registration and login

## Post-Deployment

- [ ] Set up custom domain (optional)
- [ ] Enable auto-deploy on git push
- [ ] Set up monitoring/alerts
- [ ] Test all features
- [ ] Update documentation with live URLs

## Troubleshooting

If something goes wrong:
1. Check logs in Render dashboard
2. Verify environment variables
3. Confirm database connection
4. Review [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed troubleshooting

## Cost

**Free Tier:** $0/month (services spin down after 15 min)
**Paid Tier:** ~$21/month (always on, better performance)

## Need Help?

See detailed guide: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
