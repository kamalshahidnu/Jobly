# Jobly AWS Deployment Guide

This guide walks you through deploying Jobly to AWS using the simplified stack:
- **Frontend**: AWS Amplify (React + Vite)
- **Backend**: AWS App Runner (FastAPI)
- **Database**: Amazon RDS PostgreSQL
- **File Storage**: Amazon S3
- **Secrets**: AWS Secrets Manager

## Prerequisites

- AWS Account with billing enabled
- GitHub account (or GitLab/Bitbucket)
- Your code pushed to a Git repository
- AWS CLI installed (optional, for local testing)

## Estimated Monthly Cost

- **RDS PostgreSQL (db.t3.micro)**: ~$15-20/month
- **App Runner**: ~$5-15/month (based on usage)
- **Amplify**: Free tier covers most needs, ~$0-5/month
- **S3**: ~$1-5/month (based on storage)
- **Total**: ~$20-45/month

## Part 1: Set Up RDS PostgreSQL Database

### 1.1 Create RDS Database

1. Go to [AWS RDS Console](https://console.aws.amazon.com/rds)
2. Click **Create database**
3. Configure:
   - **Engine**: PostgreSQL
   - **Version**: PostgreSQL 15.x (latest)
   - **Templates**: Free tier (if eligible) or Dev/Test
   - **DB instance identifier**: `jobly-db`
   - **Master username**: `jobly_admin`
   - **Master password**: Generate strong password (save it securely!)
   - **DB instance class**: db.t3.micro (1 vCPU, 1 GB RAM)
   - **Storage**: 20 GB gp3 (General Purpose SSD)
   - **Storage autoscaling**: Enable (max 100 GB)

4. **Connectivity**:
   - **Public access**: Yes (for now; we'll secure it later)
   - **VPC security group**: Create new
   - **Security group name**: `jobly-db-sg`

5. **Database authentication**: Password authentication
6. **Additional configuration**:
   - **Initial database name**: `jobly`
   - **Backup retention**: 7 days
   - **Enable encryption**: Yes (default KMS key)

7. Click **Create database** (takes 5-10 minutes)

### 1.2 Configure Security Group

1. Once the database is created, click on it
2. Go to **Connectivity & security** tab
3. Click on the security group (e.g., `jobly-db-sg`)
4. Click **Edit inbound rules**
5. Add rule:
   - **Type**: PostgreSQL
   - **Source**: My IP (for testing from your computer)
   - Click **Add rule** again
   - **Type**: PostgreSQL
   - **Source**: Custom, `0.0.0.0/0` (temporary - we'll restrict this to App Runner later)
6. Click **Save rules**

### 1.3 Get Database Connection Details

1. In RDS console, click on your database (`jobly-db`)
2. Note the **Endpoint** (e.g., `jobly-db.xxxxxx.us-east-1.rds.amazonaws.com`)
3. Note the **Port** (usually 5432)
4. Your connection string format:
   ```
   postgresql://jobly_admin:YOUR_PASSWORD@jobly-db.xxxxxx.us-east-1.rds.amazonaws.com:5432/jobly
   ```

## Part 2: Set Up AWS Secrets Manager

### 2.1 Store Database Credentials

1. Go to [AWS Secrets Manager Console](https://console.aws.amazon.com/secretsmanager)
2. Click **Store a new secret**
3. **Secret type**: Other type of secret
4. **Key/value pairs**:
   ```
   DATABASE_URL: postgresql://jobly_admin:YOUR_PASSWORD@YOUR_RDS_ENDPOINT:5432/jobly
   JWT_SECRET_KEY: <generate strong random string>
   OPENAI_API_KEY: your-openai-key (if you have one)
   ANTHROPIC_API_KEY: your-anthropic-key (if you have one)
   ```
5. **Secret name**: `jobly/backend/prod`
6. Click **Next** → **Next** → **Store**
7. Note the **ARN** (you'll need this for App Runner)

### 2.2 Alternative: Store Each Secret Separately

You can also store secrets individually:
- `jobly/backend/database-url`
- `jobly/backend/jwt-secret`
- `jobly/backend/openai-key`

This approach gives more granular access control.

## Part 3: Set Up S3 Bucket for File Storage

### 3.1 Create S3 Bucket

1. Go to [AWS S3 Console](https://console.aws.amazon.com/s3)
2. Click **Create bucket**
3. **Bucket name**: `jobly-storage-<your-unique-id>` (must be globally unique)
4. **Region**: Same as your RDS database (e.g., us-east-1)
5. **Block Public Access**: Keep all blocked (we'll use presigned URLs)
6. **Bucket Versioning**: Enable (recommended)
7. **Encryption**: Enable (SSE-S3)
8. Click **Create bucket**

### 3.2 Create Folder Structure

1. Click on your bucket
2. Create folders:
   - `profiles/`
   - `jobs/`
   - `documents/`
   - `resumes/`

### 3.3 Set Up CORS (if needed)

If your frontend needs to upload files directly:
1. Click on your bucket
2. Go to **Permissions** tab
3. Scroll to **Cross-origin resource sharing (CORS)**
4. Click **Edit** and add:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["https://your-amplify-domain.amplifyapp.com"],
        "ExposeHeaders": ["ETag"]
    }
]
```

## Part 4: Deploy Backend with AWS App Runner

### 4.1 Push Code to GitHub

1. Make sure your backend code is pushed to GitHub:
   ```bash
   cd /path/to/Jobly
   git add .
   git commit -m "Prepare for AWS deployment"
   git push origin main
   ```

### 4.2 Create App Runner Service

1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner)
2. Click **Create service**

**Step 1: Source**
3. **Source**: Repository
4. **Repository type**: GitHub
5. Click **Add new** to connect GitHub account
6. Authorize AWS Connector for GitHub
7. Select repository: `your-username/Jobly`
8. **Branch**: main
9. Click **Next**

**Step 2: Build**
10. **Deployment settings**: Manual (for now; can enable automatic later)
11. **Build settings**:
    - **Configuration source**: Use a configuration file (we'll create it)
    - OR select **Configure all settings here**
    - **Runtime**: Python 3
    - **Build command**: Leave empty
    - **Start command**: `uvicorn jobly.api.main:app --host 0.0.0.0 --port 8000`
    - **Port**: 8000
12. Click **Next**

**Step 3: Configure**
13. **Service name**: `jobly-backend`
14. **Virtual CPU**: 1 vCPU
15. **Memory**: 2 GB
16. **Environment variables**: Click **Add environment variable**
    - Key: `DATABASE_URL`, Value: (paste your PostgreSQL connection string)
    - Key: `JWT_SECRET_KEY`, Value: (your secret key)
    - Key: `CORS_ORIGINS`, Value: `https://*.amplifyapp.com,https://yourdomain.com`
    - Key: `OPENAI_API_KEY`, Value: (your key)
    - Key: `ANTHROPIC_API_KEY`, Value: (your key)
    - Add other environment variables from `.env.example`
17. **Auto scaling**:
    - Min instances: 1
    - Max instances: 3
18. **Health check**:
    - Path: `/health`
    - Interval: 20 seconds
    - Timeout: 5 seconds
19. Click **Next**

**Step 4: Review and Create**
20. Review all settings
21. Click **Create & deploy**
22. Wait 5-10 minutes for deployment

### 4.3 Get Backend URL

1. Once deployed, note the **Default domain**
2. Format: `https://xxxxx.us-east-1.awsapprunner.com`
3. Test it: Open `https://xxxxx.us-east-1.awsapprunner.com/health`
4. Should return: `{"status": "healthy"}`

### 4.4 Update RDS Security Group (Secure Database)

1. Go back to RDS Console
2. Click on your database security group
3. Edit inbound rules
4. Remove the `0.0.0.0/0` rule
5. Add new rule:
   - **Type**: PostgreSQL
   - **Source**: Security group of App Runner (find in App Runner VPC connector)
   - OR keep `0.0.0.0/0` but rotate password regularly

## Part 5: Deploy Frontend with AWS Amplify

### 5.1 Create Amplify App

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify)
2. Click **New app** → **Host web app**
3. **Repository service**: GitHub
4. Authorize GitHub (if not already)
5. Select repository: `your-username/Jobly`
6. **Branch**: main
7. Click **Next**

### 5.2 Configure Build Settings

8. **App name**: `jobly-frontend`
9. Amplify will auto-detect Vite configuration
10. **Build and test settings**:
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/dist
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
```

11. **Advanced settings**: Click to expand
12. Add environment variable:
    - Key: `VITE_API_URL`
    - Value: Your App Runner URL (e.g., `https://xxxxx.us-east-1.awsapprunner.com`)
13. Click **Next**

### 5.3 Deploy

14. Review settings
15. Click **Save and deploy**
16. Wait 5-10 minutes for build and deployment

### 5.4 Access Your App

1. Once deployed, Amplify provides a URL: `https://main.xxxxxx.amplifyapp.com`
2. Open it in your browser
3. Your Jobly app should be live!

### 5.5 Set Up Custom Domain (Optional)

1. In Amplify console, click **Domain management**
2. Click **Add domain**
3. Enter your domain (e.g., `jobly.yourdomain.com`)
4. Follow DNS configuration instructions
5. Amplify provides SSL certificate automatically

## Part 6: Update Backend CORS

### 6.1 Update Environment Variable

1. Go to App Runner Console
2. Click on `jobly-backend` service
3. Go to **Configuration** tab
4. Click **Edit** under **Environment variables**
5. Update `CORS_ORIGINS`:
   ```
   https://main.xxxxxx.amplifyapp.com,https://jobly.yourdomain.com
   ```
6. Click **Apply**
7. Service will redeploy automatically

## Part 7: Initialize Database Schema

### 7.1 Test Database Connection

1. Use a PostgreSQL client (e.g., pgAdmin, TablePlus, or `psql`)
2. Connect using your RDS endpoint and credentials
3. Verify the `jobly` database exists

### 7.2 Run Initial Migration

The database schema will be created automatically when the backend starts (see `memory/database.py` - `init_schema()` method).

To verify:
1. Visit: `https://your-app-runner-url.awsapprunner.com/docs`
2. Try the `/health` endpoint
3. Try creating a user via `/api/v1/auth/register`

## Part 8: Testing and Verification

### 8.1 Test Backend

```bash
# Health check
curl https://your-app-runner-url.awsapprunner.com/health

# API docs
open https://your-app-runner-url.awsapprunner.com/docs
```

### 8.2 Test Frontend

1. Open your Amplify URL
2. Try registering a new user
3. Log in
4. Test core features

### 8.3 Test Database

```bash
# Connect to RDS
psql "postgresql://jobly_admin:PASSWORD@your-rds-endpoint:5432/jobly"

# List tables
\dt

# Check users
SELECT * FROM users;
```

## Part 9: Monitoring and Logs

### 9.1 App Runner Logs

1. Go to App Runner Console
2. Click on your service
3. Go to **Logs** tab
4. View application and system logs
5. Can export to CloudWatch for advanced monitoring

### 9.2 Amplify Logs

1. Go to Amplify Console
2. Click on your app
3. Each deployment has logs
4. View build logs and runtime logs

### 9.3 RDS Monitoring

1. Go to RDS Console
2. Click on your database
3. Go to **Monitoring** tab
4. View CPU, connections, storage metrics

### 9.4 Set Up CloudWatch Alarms (Optional)

1. Go to CloudWatch Console
2. Create alarms for:
   - RDS high CPU usage (>80%)
   - RDS low storage (<20%)
   - App Runner high error rate
   - App Runner high response time

## Part 10: Security Best Practices

### 10.1 Secure RDS

- ✅ Enable encryption at rest
- ✅ Use SSL/TLS for connections
- ✅ Restrict security group to only App Runner
- ✅ Regular automated backups
- ✅ Enable CloudWatch monitoring

### 10.2 Secure App Runner

- ✅ Use Secrets Manager for sensitive data
- ✅ Enable IAM authentication
- ✅ Use private VPC (advanced)
- ✅ Implement rate limiting in FastAPI

### 10.3 Secure S3

- ✅ Block public access
- ✅ Enable versioning
- ✅ Enable encryption
- ✅ Use IAM roles for access
- ✅ Enable access logging

### 10.4 Frontend Security

- ✅ HTTPS only (Amplify provides this)
- ✅ Enable security headers
- ✅ Implement CSP (Content Security Policy)
- ✅ Regular dependency updates

## Part 11: CI/CD Setup

### 11.1 Enable Auto-Deploy

**App Runner:**
1. Go to service settings
2. Enable automatic deployments
3. Every push to `main` triggers deployment

**Amplify:**
1. Already enabled by default
2. Configure branch patterns if needed

### 11.2 Preview Environments

**Amplify:**
1. Go to **Previews** tab
2. Enable pull request previews
3. Each PR gets its own preview URL

## Part 12: Scaling and Optimization

### 12.1 App Runner Scaling

- Auto-scales between min/max instances
- Adjust based on traffic patterns
- Monitor metrics to optimize

### 12.2 RDS Scaling

- Vertical: Upgrade instance type
- Horizontal: Add read replicas
- Storage: Auto-scaling enabled

### 12.3 Cost Optimization

1. Use RDS Reserved Instances (save 30-60%)
2. Implement caching (Redis/ElastiCache)
3. Optimize API queries
4. Use S3 lifecycle policies for old files

## Troubleshooting

### Backend not starting

1. Check App Runner logs
2. Verify environment variables
3. Test database connectivity
4. Check Python dependencies

### Frontend can't reach backend

1. Verify `VITE_API_URL` is correct
2. Check CORS configuration
3. Verify App Runner is running
4. Check network connectivity

### Database connection errors

1. Verify RDS is running
2. Check security group rules
3. Verify connection string
4. Check database credentials

### High costs

1. Review RDS instance size
2. Check App Runner instance count
3. Optimize S3 storage
4. Enable cost allocation tags

## Next Steps

- [ ] Set up custom domain
- [ ] Configure email service (SES)
- [ ] Add Redis for caching (ElastiCache)
- [ ] Implement CDN (CloudFront)
- [ ] Set up monitoring dashboard
- [ ] Configure automated backups
- [ ] Implement disaster recovery plan
- [ ] Add staging environment

## Resources

- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [AWS Amplify Documentation](https://docs.aws.amazon.com/amplify/)
- [Amazon RDS Documentation](https://docs.aws.amazon.com/rds/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## Support

- AWS Support: [console.aws.amazon.com/support](https://console.aws.amazon.com/support)
- GitHub Issues: Create an issue in your repository
- AWS Community Forums: [forums.aws.amazon.com](https://forums.aws.amazon.com)

---

**Congratulations!** Your Jobly application is now deployed on AWS! 🎉
