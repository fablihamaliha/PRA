# CI/CD Setup Guide - Complete Step-by-Step

This guide will help you set up automated testing, building, and deployment for your PRA application.

## Table of Contents
1. [What is CI/CD?](#what-is-cicd)
2. [GitHub Actions Setup](#github-actions-setup)
3. [Configure Secrets](#configure-secrets)
4. [Test the Pipeline](#test-the-pipeline)
5. [Deploy to Raspberry Pi](#deploy-to-raspberry-pi)

---

## What is CI/CD?

**CI (Continuous Integration):**
- Automatically tests your code when you push changes
- Builds Docker images
- Checks for security vulnerabilities
- Ensures code quality

**CD (Continuous Deployment):**
- Automatically deploys your app when you create a release
- Pushes Docker images to a registry
- Updates your Raspberry Pi with the new version

**Your Workflows:**
1. **ci.yml** - Runs tests on every push/PR
2. **cd.yml** - Deploys when you create a release tag
3. **docker-hub.yml** - Alternative deployment to Docker Hub

---

## GitHub Actions Setup

### Step 1: Push Your Code to GitHub

If you haven't already:

```bash
cd /Users/maliha/PycharmProjects/PRA

# Initialize git (if not done)
git init

# Add all files
git add .

# Create first commit
git commit -m "feat: Add CI/CD workflows and Docker setup"

# Create GitHub repository (do this on github.com first)
# Then add remote:
git remote add origin https://github.com/YOUR_USERNAME/PRA.git

# Push to GitHub
git branch -M master
git push -u origin master
```

### Step 2: Verify Workflows Are Detected

1. Go to your GitHub repository
2. Click **"Actions"** tab
3. You should see 3 workflows:
   - ✅ CI - Build & Test
   - ✅ CD - Deploy
   - ✅ Docker Hub Deploy

---

## Configure Secrets

GitHub Secrets store sensitive information (API keys, passwords) securely.

### Step 3: Add GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**

### Required Secrets

#### For Docker Hub (if using docker-hub.yml):

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | Your username at hub.docker.com |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Docker Hub → Account Settings → Security → New Access Token |

#### For Raspberry Pi Deployment (if using cd.yml):

| Secret Name | Value | Example |
|-------------|-------|---------|
| `PI_HOST` | Raspberry Pi IP address | `192.168.1.100` |
| `PI_USERNAME` | SSH username on Pi | `pi` |
| `PI_SSH_KEY` | Private SSH key | (see below) |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/db` |
| `SECRET_KEY` | Flask secret key | (random string) |
| `RAPIDAPI_KEY` | RapidAPI key (optional) | Your RapidAPI key |
| `OPENAI_API_KEY` | OpenAI key (optional) | Your OpenAI API key |

### How to Get SSH Key for Raspberry Pi

```bash
# On your Mac, generate SSH key pair
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/pi_deploy_key

# This creates:
# - ~/.ssh/pi_deploy_key (private key) ← Add this to GitHub secret
# - ~/.ssh/pi_deploy_key.pub (public key) ← Add this to Raspberry Pi

# Copy public key to Raspberry Pi
ssh-copy-id -i ~/.ssh/pi_deploy_key.pub pi@YOUR_PI_IP

# Test connection
ssh -i ~/.ssh/pi_deploy_key pi@YOUR_PI_IP

# Copy private key content for GitHub secret
cat ~/.ssh/pi_deploy_key
# Copy the entire output and paste into PI_SSH_KEY secret
```

---

## Test the Pipeline

### Step 4: Trigger CI Workflow (Automatic)

Every time you push code, CI runs automatically:

```bash
# Make a small change
echo "# Test CI/CD" >> README.md

# Commit and push
git add README.md
git commit -m "test: Trigger CI pipeline"
git push

# Go to GitHub → Actions tab
# You'll see the "CI - Build & Test" workflow running
```

**What CI Does:**
1. ✅ Checks out your code
2. ✅ Sets up Python 3.12
3. ✅ Installs dependencies
4. ✅ Runs tests (checks imports work)
5. ✅ Builds Docker image
6. ✅ Scans for security vulnerabilities

**Expected Result:** Green checkmark ✅ (workflow passes)

### Step 5: Create a Release (Triggers CD)

CD workflow only runs when you create a release:

```bash
# Tag your code with a version
git tag v1.0.0

# Push the tag
git push origin v1.0.0

# OR create release via GitHub UI:
# 1. Go to your repo → Releases
# 2. Click "Create a new release"
# 3. Tag version: v1.0.0
# 4. Release title: "v1.0.0 - Initial Release"
# 5. Description: "First production release with CI/CD"
# 6. Click "Publish release"
```

**What CD Does:**
1. ✅ Builds Docker image for both x86 and ARM (Raspberry Pi)
2. ✅ Pushes to GitHub Container Registry (`ghcr.io`)
3. ✅ Optionally deploys to Raspberry Pi (if secrets configured)

**Expected Result:**
- Image available at: `ghcr.io/YOUR_USERNAME/pra:v1.0.0`
- Raspberry Pi updated with new version

---

## Deploy to Raspberry Pi

### Step 6: Prepare Raspberry Pi

```bash
# SSH into your Raspberry Pi
ssh pi@YOUR_PI_IP

# Install Docker (if not installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi

# Logout and login for group changes to take effect
exit
ssh pi@YOUR_PI_IP

# Verify Docker works
docker --version

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Create directory for app data
mkdir -p ~/pra-app
cd ~/pra-app
```

### Step 7: Manual Deployment (First Time)

```bash
# On Raspberry Pi

# Login to GitHub Container Registry
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Pull your image
docker pull ghcr.io/YOUR_USERNAME/pra:latest

# Create environment file
cat > .env << 'EOF'
DATABASE_URL=postgresql://prra_user:your_password@localhost:5432/prra_db
SECRET_KEY=your-super-secret-key
RAPIDAPI_KEY=your-rapidapi-key
OPENAI_API_KEY=your-openai-key
FLASK_ENV=production
EOF

# Run PostgreSQL
docker run -d \
  --name pra-postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=prra_db \
  -e POSTGRES_USER=prra_user \
  -e POSTGRES_PASSWORD=your_password \
  -v pra-db-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine

# Wait for database to be ready
sleep 10

# Run your app
docker run -d \
  --name pra-app \
  --restart unless-stopped \
  -p 80:5001 \
  --env-file .env \
  --link pra-postgres:postgres \
  ghcr.io/YOUR_USERNAME/pra:latest

# Check it's running
docker ps

# View logs
docker logs pra-app

# Test it works
curl http://localhost
```

### Step 8: Automated Deployment

After manual setup, future deployments are automatic!

**Workflow:**
1. Make code changes
2. Push to GitHub → CI runs tests
3. Create release tag → CD builds and deploys
4. Raspberry Pi automatically pulls and runs new version

```bash
# Example release workflow:
git add .
git commit -m "feat: Add new feature"
git push

# Create new version
git tag v1.1.0
git push origin v1.1.0

# GitHub Actions will:
# 1. Build new Docker image
# 2. Push to registry
# 3. SSH to Raspberry Pi
# 4. Pull new image
# 5. Restart container
# ✅ Your Pi is now running v1.1.0!
```

---

## Monitoring & Troubleshooting

### View Workflow Runs

```
GitHub → Your Repo → Actions tab

You'll see:
- Green ✅ = Success
- Red ❌ = Failed
- Yellow 🟡 = Running
```

### Common Issues

#### 1. CI Workflow Fails

**Check the logs:**
1. GitHub → Actions → Click failed workflow
2. Click the failed job
3. Expand the failed step

**Common fixes:**
- Missing dependency → Add to `requirements.txt`
- Import error → Check file paths in code
- Test failure → Fix the failing test

#### 2. CD Workflow Can't Push Image

**Error:** "authentication required"

**Fix:**
```bash
# For GitHub Container Registry:
# 1. Go to GitHub → Settings → Developer settings
# 2. Personal access tokens → Tokens (classic)
# 3. Generate new token with 'write:packages' permission
# 4. Add as secret: GITHUB_TOKEN

# For Docker Hub:
# 1. hub.docker.com → Account Settings → Security
# 2. New Access Token
# 3. Copy token
# 4. Add as secret: DOCKERHUB_TOKEN
```

#### 3. Raspberry Pi Deployment Fails

**Error:** "permission denied"

**Fix:**
```bash
# Test SSH connection manually
ssh -i ~/.ssh/pi_deploy_key pi@YOUR_PI_IP

# If fails, check:
# 1. Raspberry Pi IP is correct
# 2. SSH key is correct
# 3. Pi is reachable from internet (if deploying from GitHub)
# 4. Firewall allows SSH (port 22)
```

#### 4. Docker Pull Rate Limit

**Error:** "toomanyrequests: You have reached your pull rate limit"

**Fix:**
```bash
# Login to Docker Hub (free tier = 200 pulls/6hr)
docker login

# Or use GitHub Container Registry (unlimited for public repos)
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Developer                                                  │
│  ┌────────┐                                                │
│  │ Code   │                                                │
│  └───┬────┘                                                │
│      │                                                     │
│      ▼                                                     │
│  ┌────────┐      ┌──────────────────────────────────┐    │
│  │git push│─────▶│  GitHub                          │    │
│  └────────┘      │  ┌────────────────────────────┐  │    │
│                  │  │  CI Workflow (ci.yml)      │  │    │
│                  │  │  ✅ Run tests              │  │    │
│                  │  │  ✅ Build Docker image     │  │    │
│                  │  │  ✅ Security scan          │  │    │
│                  │  └────────────────────────────┘  │    │
│                  └──────────────────────────────────┘    │
│                                                           │
│  ┌────────────┐   ┌──────────────────────────────────┐  │
│  │ Create Tag │──▶│  GitHub                          │  │
│  │ v1.0.0     │   │  ┌────────────────────────────┐  │  │
│  └────────────┘   │  │  CD Workflow (cd.yml)      │  │  │
│                   │  │  ✅ Build multi-arch image │  │  │
│                   │  │  ✅ Push to registry       │  │  │
│                   │  │  ✅ Deploy to Pi          │  │  │
│                   │  └────────────────────────────┘  │  │
│                   └──────────────────────────────────┘  │
│                                    │                     │
│                                    ▼                     │
│                   ┌─────────────────────────────┐       │
│                   │  Raspberry Pi                │       │
│                   │  ┌─────────────────────────┐│       │
│                   │  │ 🐳 Docker pulls image   ││       │
│                   │  │ 🔄 Restarts container   ││       │
│                   │  │ ✅ App running!         ││       │
│                   │  └─────────────────────────┘│       │
│                   └─────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

---

## Advanced Configuration

### Add Slack Notifications

```yaml
# Add to end of cd.yml
- name: Notify Slack on Success
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "✅ PRA v${{ github.ref_name }} deployed successfully!"
      }
```

### Add Email Notifications

```yaml
# Add to end of ci.yml
- name: Send failure notification
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "CI Failed: ${{ github.repository }}"
    to: your-email@example.com
    from: GitHub Actions
    body: Build ${{ github.run_number }} failed!
```

### Run Tests on Schedule

```yaml
# Add to ci.yml under "on:"
on:
  push:
    branches: [ master ]
  schedule:
    - cron: '0 0 * * *'  # Run daily at midnight
```

---

## Best Practices

### 1. Version Tagging

Use semantic versioning:
- `v1.0.0` - Major release (breaking changes)
- `v1.1.0` - Minor release (new features)
- `v1.1.1` - Patch release (bug fixes)

```bash
# Patch (bug fix)
git tag v1.0.1

# Minor (new feature)
git tag v1.1.0

# Major (breaking change)
git tag v2.0.0
```

### 2. Branch Protection

1. GitHub → Settings → Branches
2. Add rule for `master`
3. Enable:
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Require pull request reviews

### 3. Environment-Specific Secrets

```yaml
# Use different secrets for staging vs production
environment: production
env:
  DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
```

### 4. Rollback Strategy

```bash
# If new version has issues, rollback:
ssh pi@YOUR_PI_IP

# Run previous version
docker run -d \
  --name pra-app \
  -p 80:5001 \
  --env-file .env \
  ghcr.io/YOUR_USERNAME/pra:v1.0.0  # Previous working version
```

---

## Cost & Performance

### GitHub Actions Free Tier

✅ **2,000 minutes/month** free for private repos
✅ **Unlimited** for public repos

**Your usage:**
- CI run: ~3-5 minutes
- CD run: ~5-8 minutes
- ~60 runs/month on free tier

### Storage

✅ **500 MB** free package storage
✅ **1 GB** free transfer/month

**Your image:**
- Size: ~550 MB
- Compressed: ~200 MB
- ~5 versions fit in free tier

---

## Next Steps

1. ✅ **Push to GitHub** - Upload your code
2. ✅ **Add secrets** - Configure API keys and credentials
3. ✅ **Test CI** - Make a commit and watch tests run
4. ✅ **Create release** - Tag v1.0.0 and deploy
5. ✅ **Setup Pi** - Prepare Raspberry Pi for deployment
6. ✅ **Automate** - Let GitHub Actions handle future deployments

---

## Success! 🎉

You now have:
- ✅ Automated testing on every push
- ✅ Automated Docker builds
- ✅ Security scanning
- ✅ Multi-architecture images (x86 + ARM)
- ✅ Automated deployment to Raspberry Pi
- ✅ Version tracking with Git tags

**Your workflow is now:**
1. Write code
2. Push to GitHub
3. Create release
4. ✨ Magic happens automatically! ✨
5. Your app is live on Raspberry Pi

---

## Support

**Issues?**
- Check GitHub Actions logs
- Review this guide
- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Verify secrets are configured correctly

**Resources:**
- GitHub Actions Docs: https://docs.github.com/en/actions
- Docker Hub: https://hub.docker.com
- GitHub Container Registry: https://ghcr.io
