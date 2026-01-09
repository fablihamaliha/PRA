# PRA - Deployment Guide

**Date:** 2026-01-09
**Status:** ✅ Ready to Deploy

---

## 📋 Summary of Changes

You asked two questions:

### Question 1: OPENAI_API_KEY Warning
> "When deploying to Pi, are the OPENAI_API_KEY warnings disabled?"

**Answer: NO** - The warning still appears because your production `.env` doesn't have the key.

**Is this a problem?** NO! The app works perfectly without it. Only optional GPT features are disabled.

### Question 2: Analytics Not Working + Security Issues
> "Analytics deployed but not working, and need to harden security"

**Fixed!** Created secure admin authentication system with Argon2 hashing + IP allowlist + rate limiting.

---

## 🚀 What You Need To Do

Follow this simple checklist in order:

### ✅ Step 1: Install Dependency Locally

```bash
pip3 install argon2-cffi
```

### ✅ Step 2: Generate Admin Credentials

```bash
cd /Users/maliha/Desktop/PRA
python3 generate_admin_creds.py
```

**Save the output!** You'll need:
- Username (e.g., `maliha_admin`)
- Passphrase Hash (starts with `$argon2id$...`)
- Your passphrase (save in password manager)

### ✅ Step 3: Push to GitHub

```bash
git add -A
git commit -m "Add secure admin authentication for analytics"
git push origin master
```

CI/CD will deploy automatically (takes 2-3 minutes).

### ✅ Step 4: Update Production .env

```bash
# SSH into Raspberry Pi
ssh malsi123@your-raspberry-pi-ip

# Edit .env
nano ~/PRA/.env

# Add these lines (use YOUR values):
ADMIN_USERNAME=maliha_admin
ADMIN_PASSPHRASE_HASH=$argon2id$v=19$m=65536,t=3,p=4$YOUR_HASH

# Save: Ctrl+X, Y, Enter
```

### ✅ Step 5: Restart & Test

```bash
# Restart app
docker restart pra-app

# Check logs
docker logs pra-app --tail 50
```

**Then test login:**
1. Visit: https://skincares.work/admin/login
2. Enter your credentials
3. Access analytics dashboard!

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** | Step-by-step deployment guide with troubleshooting |
| **[QUICK_START_ANALYTICS.md](QUICK_START_ANALYTICS.md)** | Quick 5-step setup guide |
| **[ANALYTICS_SECURITY_FIX.md](ANALYTICS_SECURITY_FIX.md)** | Comprehensive technical documentation |

**Start here:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 🔒 Security Features Implemented

1. **Argon2 Password Hashing** - Impossible to crack, industry-standard
2. **IP Allowlist** (optional) - Restrict access to your home/office
3. **Rate Limiting** - 5 failed attempts = 15 minute lockout
4. **Session-Based Auth** - Secure admin sessions
5. **Failed Login Tracking** - Monitor attack attempts
6. **Separate Admin Table** - Not mixed with regular users

---

## ❓ FAQs

### "Do I need to add OPENAI_API_KEY?"

**No!** Your app works perfectly without it. Only these optional features are disabled:
- AI-generated product explanations
- AI skincare advice
- AI deal insights

If you want these features, add to `.env`:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
```

⚠️ **Warning:** OpenAI charges per request (~$0.10-$0.50 per 1000 users)

---

### "What if I can't install argon2-cffi locally?"

**Option 1:** Use virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install argon2-cffi
python generate_admin_creds.py
```

**Option 2:** Generate on Raspberry Pi after deployment:
```bash
ssh malsi123@your-pi-ip
cd ~/PRA
docker exec pra-app python generate_admin_creds.py
```

---

### "How do I find my IP for the allowlist?"

```bash
curl https://icanhazip.com
```

Add to `.env`:
```bash
ADMIN_IP_ALLOWLIST=your_ip_here
```

Or leave it out to allow all IPs.

---

### "What if I forget my passphrase?"

You'll need to generate new credentials and update the `.env` file on the Pi.

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "python: command not found" | Use `python3` instead |
| "argon2 not installed" | Run `pip3 install argon2-cffi` |
| "Invalid credentials" | Double-check username and passphrase |
| "IP not allowed" | Add your IP to `ADMIN_IP_ALLOWLIST` or remove the setting |
| "Too many attempts" | Wait 15 minutes or clear failed attempts |

**Full troubleshooting guide:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md#troubleshooting)

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Code pushed to GitHub successfully
- [ ] CI/CD workflow completed (check GitHub Actions)
- [ ] `.env` updated on Raspberry Pi
- [ ] App restarted (`docker restart pra-app`)
- [ ] Can access: https://skincares.work/admin/login
- [ ] Can log in with admin credentials
- [ ] Analytics dashboard shows data
- [ ] Rate limiting works (try 5 wrong passwords)

---

## 🎯 What Changed

### New Files Created:
- `pra/models/admin_user.py` - Admin user model
- `pra/routes/admin_auth.py` - Authentication routes
- `pra/templates/admin_login.html` - Login page
- `generate_admin_creds.py` - Credential generator

### Modified Files:
- `pra/app.py` - Register admin auth blueprint
- `pra/routes/analytics_routes.py` - Use new auth system
- `requirements.txt` - Added argon2-cffi

### Deprecated:
- Email-based admin access (`@admin.com`) - No longer works
- Must use new admin login system

---

## 🎉 Success!

Once deployed, your analytics dashboard is secured with enterprise-grade authentication!

**Access at:** https://skincares.work/admin/login

**Need help?** Read [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for detailed instructions.

---

**Last Updated:** 2026-01-09
**Next Review:** When you want to add more admins or change security settings
