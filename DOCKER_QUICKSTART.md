# Docker Quick Start Guide

## ✅ FIXED! Your Docker Setup is Ready

Your application is now successfully containerized and ready to deploy!

## What Was Fixed

1. ✅ **Dockerfile** - Created in the correct location (project root)
2. ✅ **Fixed paths** - Changed from `COPY app` to `COPY pra`
3. ✅ **Dependencies** - Added all required system packages
4. ✅ **.dockerignore** - Excludes unnecessary files
5. ✅ **docker-compose.yml** - Full stack setup (app + database)
6. ✅ **Image built** - `pra-app:latest` (553MB)

---

## Quick Test (Local)

### 1. Start Everything

```bash
# Make sure you're in the project directory
cd /Users/maliha/PycharmProjects/PRA

# Copy environment template
cp .env.docker .env

# Edit .env with your values
# At minimum, change:
# - DB_PASSWORD
# - SECRET_KEY
# - RAPIDAPI_KEY (if you have it)
# - OPENAI_API_KEY (if you have it)

# Start the application
docker-compose up -d

# Watch the logs
docker-compose logs -f app
```

### 2. Check It's Running

```bash
# Check containers
docker-compose ps

# Should show:
# pra-app      ✓ healthy
# pra-postgres ✓ healthy

# Test the app
curl http://localhost:5001

# Open in browser
open http://localhost:5001
```

### 3. Stop Everything

```bash
# Stop containers
docker-compose down

# Stop and remove data
docker-compose down -v  # Warning: Deletes database!
```

---

## What You Have Now

### File Structure

```
PRA/
├── Dockerfile                  ✅ Main Docker image definition
├── .dockerignore              ✅ Files to exclude from image
├── docker-compose.yml         ✅ Multi-container setup
├── .env.docker                ✅ Environment template
├── pra/                       ✅ Your application code
└── requirements.txt           ✅ Python dependencies
```

### Docker Images

```bash
# View your image
docker images pra-app

REPOSITORY   TAG      IMAGE ID       SIZE
pra-app      latest   df1a84b1572b   553MB
```

**Size breakdown:**
- Base Python image: ~150MB
- System dependencies: ~100MB
- Python packages: ~200MB
- Your app code: ~3MB
- **Total: 553MB** (Normal for Flask + PostgreSQL drivers)

---

## Next Steps

### A. Push to Docker Hub (for deployment)

```bash
# 1. Login to Docker Hub
docker login
# Enter username and password

# 2. Tag your image
docker tag pra-app:latest YOUR_USERNAME/pra-app:latest

# 3. Push to Docker Hub
docker push YOUR_USERNAME/pra-app:latest

# Now you can pull this image on Raspberry Pi!
```

### B. Push to GitHub Container Registry (alternative)

```bash
# 1. Create GitHub Personal Access Token
# Go to: GitHub → Settings → Developer settings → Personal access tokens
# Create token with 'write:packages' permission

# 2. Login
echo YOUR_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# 3. Tag and push
docker tag pra-app:latest ghcr.io/YOUR_GITHUB_USERNAME/pra-app:latest
docker push ghcr.io/YOUR_GITHUB_USERNAME/pra-app:latest
```

### C. Deploy to Raspberry Pi

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full instructions.

**Quick version:**

1. **On Raspberry Pi:** Install k3s
   ```bash
   curl -sfL https://get.k3s.io | sh -
   ```

2. **Pull your image:**
   ```bash
   docker pull YOUR_USERNAME/pra-app:latest
   ```

3. **Run it:**
   ```bash
   docker run -d \
     -p 80:5001 \
     -e DATABASE_URL="postgresql://user:pass@host/db" \
     -e SECRET_KEY="your-secret" \
     YOUR_USERNAME/pra-app:latest
   ```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs app

# Common issues:
# 1. Database not ready → Wait 30s and try again
# 2. Port already in use → Change port in docker-compose.yml
# 3. Missing env vars → Check .env file exists
```

### Database Connection Error

```bash
# Check postgres is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U prra_user -d prra_db

# Restart everything
docker-compose restart
```

### Image Too Large

```bash
# Current size: 553MB (this is normal!)

# If you want to reduce:
# 1. Use multi-stage build (saves ~200MB)
# 2. Remove dev dependencies (saves ~50MB)
# 3. Use alpine-based images (saves ~100MB)

# But 553MB is fine for Raspberry Pi 4!
```

### Can't Access on Port 5001

```bash
# Check if port is bound
docker-compose ps

# Should show: 0.0.0.0:5001->5001/tcp

# Test locally
curl http://localhost:5001

# If still issues, check firewall
# Mac: System Preferences → Security → Firewall
```

---

## Useful Commands

### Docker Management

```bash
# View running containers
docker ps

# View all images
docker images

# Remove old images
docker image prune -a

# View logs
docker-compose logs -f app

# Restart a service
docker-compose restart app

# Execute command in container
docker-compose exec app bash
```

### Database Management

```bash
# Access database
docker-compose exec postgres psql -U prra_user -d prra_db

# Backup database
docker-compose exec postgres pg_dump -U prra_user prra_db > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U prra_user -d prra_db
```

### Cleaning Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (deletes data!)
docker-compose down -v

# Remove everything Docker (careful!)
docker system prune -a --volumes
```

---

## Production Checklist

Before deploying to production:

- [ ] Change `DB_PASSWORD` to strong password
- [ ] Change `SECRET_KEY` to random string
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Add your `RAPIDAPI_KEY`
- [ ] Add your `OPENAI_API_KEY`
- [ ] Enable HTTPS (use reverse proxy)
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Set resource limits in docker-compose.yml
- [ ] Use Docker secrets for sensitive data

---

## Performance Tuning

### For Raspberry Pi

```yaml
# Add to docker-compose.yml under 'app:'
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      memory: 512M
```

### Add Gunicorn (Production Server)

```dockerfile
# Add to requirements.txt:
gunicorn==21.2.0

# Change CMD in Dockerfile to:
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--threads", "4", "pra.app:app"]
```

---

## Success! 🎉

Your Docker setup is complete and working. You have:

✅ Working Dockerfile
✅ Built Docker image (pra-app:latest)
✅ Docker Compose configuration
✅ Environment variable setup
✅ Ready for deployment

**Next:** Push your image to a registry and deploy to Raspberry Pi!
