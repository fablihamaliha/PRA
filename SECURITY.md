# 🔒 Security & Access Control

This document explains how your repository and infrastructure are protected.

---

## 🛡️ GitHub Actions Security

### Workflow Protection

All GitHub Actions workflows are protected with **repository owner verification**:

```yaml
verify-owner:
  steps:
    - name: Check if repository owner
      run: |
        if [ "${{ github.repository_owner }}" = "fablihamaliha" ]; then
          echo "✅ Authorized"
        else
          echo "❌ Unauthorized - workflow blocked"
          exit 1
        fi
```

**What this means:**
- ✅ Workflows **ONLY run** for `fablihamaliha` (you)
- ❌ If someone forks your repo, workflows **will NOT execute**
- ❌ They **cannot deploy** to your Raspberry Pi
- ❌ They **cannot push** to your container registry
- ✅ Your infrastructure is **completely protected**

### Self-Hosted Runner Protection

Your Raspberry Pi runner:
- Only accepts jobs from `fablihamaliha/PRA`
- Requires GitHub authentication token
- Cannot be accessed by forked repositories
- Protected by GitHub's runner security model

---

## 🔐 Secrets Management

### GitHub Secrets (Protected)

The following secrets are stored in GitHub and **never exposed**:

- `SECRET_KEY` - Flask secret key
- `RAPIDAPI_KEY` - API keys
- `OPENAI_API_KEY` - OpenAI credentials
- `SMTP_PASSWORD` - Email credentials
- Database passwords

**Security measures:**
- ✅ Never committed to git (in `.gitignore`)
- ✅ Only accessible to repository owner
- ✅ Encrypted at rest by GitHub
- ✅ Only injected at runtime
- ✅ Not visible in logs

### Local Environment Variables

All sensitive data uses `.env` files:

```bash
# .env is in .gitignore - NEVER committed
.env
.env.local
.env.docker
```

---

## 📁 Protected Files & Documentation

### What's Hidden from GitHub

The following files are **NEVER pushed** to GitHub:

```
# Sensitive Documentation
*_SETUP.md
*_FEATURES.md
*_GUIDE.md
SECURITY_*.md
SOC_*.md
MONITORING_*.md

# Environment Files
.env
.env.local
.env.docker

# Setup Scripts
setup_*.py
monitor_*.py
check_*.py
```

### What's Public

Only these files are visible:
- `README.md` - Basic project information
- `LICENSE` - License file
- `CONTRIBUTING.md` - Contribution guidelines
- Source code (application logic)

**Internal documentation stays private!**

---

## 🚫 What Attackers CANNOT Do

Even if someone forks your repository, they **CANNOT**:

❌ Run your CI/CD pipelines  
❌ Deploy to your Raspberry Pi  
❌ Access your self-hosted runner  
❌ Push to your container registry  
❌ See your environment variables  
❌ Access your database  
❌ View internal documentation  
❌ Use your API keys  
❌ Access your monitoring dashboard  
❌ Trigger deployments  
❌ Modify your production environment  

---

## ✅ What You Should Do

### 1. Keep Repository Private (Recommended)

Make your repository private in GitHub settings:
- Settings → General → Danger Zone → Change visibility → Make private

### 2. Or Use These Protections (If Public)

If you want to keep it public for portfolio:

✅ **Workflows are protected** - Owner verification in place  
✅ **Secrets are safe** - Using GitHub Secrets  
✅ **Runner is protected** - Self-hosted runner security  
✅ **Internal docs hidden** - .gitignore configured  
✅ **No hardcoded secrets** - All use environment variables  

### 3. Additional Security Measures

**Branch Protection:**
```
Settings → Branches → Add branch protection rule
- Branch name: master
- ✓ Require pull request reviews
- ✓ Require status checks to pass
- ✓ Do not allow bypassing
```

**Runner Labels:**
```
Your runner only accepts jobs labeled: self-hosted
Forks cannot use self-hosted runners
```

**Container Registry:**
```
Your images are at: ghcr.io/fablihamaliha/pra
Only you can push to this registry
Others can pull (if public) but cannot modify
```

---

## 🔍 Monitoring Access Control

### Admin Dashboard

**Protected by:**
- Flask-Login authentication
- Admin-only email verification (`@admin.com`)
- Session management
- HTTPS (via ngrok in production)

**Access:**
```python
@login_required
def dashboard():
    if not current_user.email.endswith('@admin.com'):
        return jsonify({'error': 'Admin access required'}), 403
```

### External Monitoring Stack

**Protected by:**
- Separate Docker network
- Grafana authentication (change default password!)
- Firewall rules (recommended)
- Not exposed publicly by default

**Recommended:**
```bash
# Only allow local network access
sudo ufw allow from 192.168.1.0/24 to any port 3000
sudo ufw allow from 192.168.1.0/24 to any port 9090
```

---

## 🚨 Security Checklist

### Before Pushing to GitHub

- [ ] Check `.env` is in `.gitignore`
- [ ] No hardcoded API keys in code
- [ ] No database passwords in code
- [ ] Internal documentation in `.gitignore`
- [ ] Workflow owner verification in place
- [ ] Secrets configured in GitHub settings

### Production Deployment

- [ ] Change default Grafana password
- [ ] Enable HTTPS for ngrok
- [ ] Configure firewall rules
- [ ] Set up email notifications
- [ ] Enable monitoring alerts
- [ ] Regular security updates
- [ ] Database backups configured

### Ongoing Security

- [ ] Review GitHub Actions logs
- [ ] Monitor security events in admin dashboard
- [ ] Check Grafana for anomalies
- [ ] Update dependencies regularly
- [ ] Review access logs
- [ ] Rotate API keys periodically

---

## 🎯 Attack Surface Analysis

### Exposed Endpoints

**Public (via ngrok):**
- `/` - Main application
- `/auth` - Login/signup
- `/deals` - Product search

**Protected (admin only):**
- `/analytics/dashboard` - Requires admin login

**Internal (not exposed):**
- Monitoring stack (Grafana, Prometheus)
- PostgreSQL database
- Docker containers

### Security Layers

1. **Network Layer** - ngrok HTTPS tunnel
2. **Application Layer** - Flask security middleware
3. **Authentication Layer** - Flask-Login
4. **Authorization Layer** - Admin role verification
5. **Data Layer** - PostgreSQL with credentials
6. **Infrastructure Layer** - Docker isolation

---

## 📞 Incident Response

### If You Suspect Unauthorized Access

1. **Immediately:**
   - Revoke GitHub tokens
   - Rotate all API keys
   - Change admin passwords
   - Check GitHub Actions logs

2. **Investigate:**
   - Review security events in admin dashboard
   - Check Prometheus/Grafana for anomalies
   - Review database access logs
   - Check Docker container logs

3. **Recover:**
   - Reset all credentials
   - Force logout all sessions
   - Update security rules
   - Enable additional monitoring

### Emergency Commands

```bash
# Stop all services
docker-compose down
docker stop pra-app

# Revoke runner token
cd ~/actions-runner
./config.sh remove

# Check access logs
docker logs pra-app | grep -i "admin"
docker logs pra-app | grep -i "auth"

# Block IP address (if needed)
# Use admin dashboard or direct database access
```

---

## ✅ Summary

Your repository and infrastructure are protected by:

1. ✅ **Workflow owner verification** - Only you can run CI/CD
2. ✅ **Self-hosted runner security** - Protected by GitHub
3. ✅ **Secrets management** - GitHub Secrets + .env
4. ✅ **Hidden documentation** - .gitignore protection
5. ✅ **Authentication** - Admin dashboard protected
6. ✅ **Network isolation** - Docker networks
7. ✅ **Monitoring** - Separate, protected monitoring stack

**Your infrastructure is secure and cannot be accessed by others, even if they clone your code!**
