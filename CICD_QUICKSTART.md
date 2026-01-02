# CI/CD Quick Start - 5 Minutes Setup

## ✅ What You Have Now

Three GitHub Actions workflows ready to use:

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **CI** | `.github/workflows/ci.yml` | Every push/PR | Test & build |
| **CD** | `.github/workflows/cd.yml` | Release tags | Deploy to registry & Pi |
| **Docker Hub** | `.github/workflows/docker-hub.yml` | Tags or manual | Push to Docker Hub |

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Push to GitHub (2 minutes)

```bash
cd /Users/maliha/PycharmProjects/PRA

# Add all files
git add .

# Commit
git commit -m "feat: Add CI/CD workflows"

# Create GitHub repo first at github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/PRA.git
git push -u origin master
```

### Step 2: Add Secrets (2 minutes)

**Go to:** GitHub → Your Repo → Settings → Secrets → New secret

**Add these** (minimum for basic CI/CD):

```
No secrets needed for basic CI!
```

**Optional** (for deployment):

| Secret | Value | Why |
|--------|-------|-----|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | To push images |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Authentication |

**Get Docker Hub token:**
1. Go to hub.docker.com
2. Account Settings → Security → New Access Token
3. Copy and paste as secret

### Step 3: Test It! (1 minute)

```bash
# Make a small change
echo "# CI/CD Test" >> README.md

# Push it
git add README.md
git commit -m "test: Trigger CI"
git push

# Go to GitHub → Actions tab
# Watch the CI workflow run! ✅
```

---

## 📦 Deploy Your First Release

### Create a Release

```bash
# Tag your code
git tag v1.0.0
git push origin v1.0.0

# Or on GitHub:
# Releases → Create new release → Tag: v1.0.0 → Publish
```

**What happens:**
1. ✅ Builds Docker image for x86 and ARM
2. ✅ Pushes to GitHub Container Registry
3. ✅ Image available at: `ghcr.io/YOUR_USERNAME/pra:v1.0.0`

### Pull Image Anywhere

```bash
# On Raspberry Pi or any server:
docker pull ghcr.io/YOUR_USERNAME/pra:v1.0.0

# Run it
docker run -d -p 80:5001 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="your-secret" \
  ghcr.io/YOUR_USERNAME/pra:v1.0.0
```

---

## 🎯 Common Workflows

### Daily Development

```bash
# 1. Write code
# 2. Commit
git add .
git commit -m "feat: Add new feature"

# 3. Push (triggers CI)
git push

# ✅ CI runs tests automatically
```

### Release New Version

```bash
# 1. Bump version in your app
# 2. Tag it
git tag v1.1.0

# 3. Push tag (triggers CD)
git push origin v1.1.0

# ✅ CD builds and deploys automatically
```

### Hotfix

```bash
# 1. Fix the bug
git add .
git commit -m "fix: Critical bug"

# 2. Tag as patch
git tag v1.0.1

# 3. Push
git push origin v1.0.1

# ✅ New version deployed in ~5 minutes
```

---

## 🔍 Check Status

### View Workflows

**GitHub → Actions tab**

You'll see:
- 🟢 Green = Success
- 🔴 Red = Failed
- 🟡 Yellow = Running

### View Images

**GitHub → Packages**

You'll see all your published images:
- `pra:latest`
- `pra:v1.0.0`
- `pra:v1.1.0`

---

## 🐛 Troubleshooting

### CI Fails

```bash
# Click the failed workflow → View logs
# Common issues:
# - Import error → Check file exists
# - Dependency missing → Add to requirements.txt
# - Syntax error → Fix the code
```

### CD Can't Push Image

```bash
# Error: "denied: permission_denied"
# Fix: Enable "write:packages" in GitHub settings
# Go to: Settings → Actions → General → Workflow permissions
# Select: Read and write permissions
```

### Image Too Large

```bash
# Current size: ~550MB
# This is normal! Don't worry.

# If needed, optimize:
# 1. Use multi-stage build (saves ~200MB)
# 2. Remove dev dependencies (saves ~50MB)
# 3. Use alpine images (saves ~100MB)
```

---

## 📊 What Each Workflow Does

### CI Workflow (`ci.yml`)

**Triggers:** Every push, every PR

**Steps:**
1. Checkout code
2. Setup Python 3.12
3. Install dependencies
4. Run tests
5. Check code quality
6. Build Docker image
7. Security scan

**Time:** ~3-5 minutes

### CD Workflow (`cd.yml`)

**Triggers:** Release tags (v1.0.0, v1.1.0, etc.)

**Steps:**
1. Checkout code
2. Build Docker image (x86 + ARM)
3. Push to GitHub Container Registry
4. Tag as `latest` and version number
5. (Optional) Deploy to Raspberry Pi

**Time:** ~5-8 minutes

### Docker Hub Workflow (`docker-hub.yml`)

**Triggers:** Tags or manual

**Steps:**
1. Build image
2. Push to Docker Hub
3. Tag with version

**Time:** ~4-6 minutes

---

## 💡 Pro Tips

### Tip 1: Make Images Public

```
GitHub → Packages → Your Image → Package settings
→ Change visibility → Public

Now anyone can pull: ghcr.io/YOUR_USERNAME/pra:latest
```

### Tip 2: View Build Logs Live

```
GitHub → Actions → Click running workflow
→ Click job → Watch logs in real-time
```

### Tip 3: Cancel Failed Builds

```
Actions → Click workflow → Cancel workflow
(Saves your free minutes!)
```

### Tip 4: Re-run Failed Workflows

```
Actions → Failed workflow → Re-run jobs
(If it was a temporary failure)
```

---

## 📈 Free Tier Limits

**GitHub Actions (Free):**
- ✅ 2,000 minutes/month (private repos)
- ✅ Unlimited (public repos)

**Package Storage:**
- ✅ 500 MB free storage
- ✅ 1 GB free transfer/month

**Your Usage:**
- CI: ~4 min × 30 runs = 120 min/month
- CD: ~6 min × 4 releases = 24 min/month
- **Total: ~150 min/month** (well under limit!)

---

## 🎉 You're Done!

Your CI/CD pipeline is ready:

- ✅ **Push code** → Tests run automatically
- ✅ **Create tag** → Image builds automatically
- ✅ **Deploy** → Pull image and run

**No more manual deployment!**

---

## Next Steps

1. **Read full guide:** [CICD_SETUP_GUIDE.md](CICD_SETUP_GUIDE.md)
2. **Deploy to Pi:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
3. **Docker basics:** [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)

---

## Questions?

**Check workflow logs:**
```
GitHub → Actions → Click workflow → View logs
```

**Test locally:**
```bash
# Run CI checks locally
docker build -t pra-app:test .
python -c "from pra.app import app; print('✅ OK')"
```

**Common Commands:**
```bash
# List tags
git tag -l

# Delete tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# View remote images
docker search ghcr.io/YOUR_USERNAME

# Pull specific version
docker pull ghcr.io/YOUR_USERNAME/pra:v1.0.0
```

**Happy deploying! 🚀**
