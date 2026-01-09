# Fix: Can't Login - argon2 Module Missing

**Date:** 2026-01-09
**Issue:** Login fails because `argon2-cffi` is not installed in Docker container

---

## The Problem

Your logs show:
```
ERROR - Database initialization error: No module named 'argon2'
WARNING - Admin authentication routes not available
```

**What this means:**
- ❌ argon2-cffi is not installed in the Docker container
- ❌ Admin authentication routes didn't register
- ❌ `/admin/login` endpoint doesn't exist
- ❌ AdminUser database table wasn't created

**Why it happened:**
- You added argon2-cffi to `requirements.txt`
- BUT the Docker container needs to be **rebuilt** to install it
- The current running container has the old dependencies

---

## Quick Fix (5 minutes)

### Option 1: Rebuild Docker Container Locally

```bash
# Stop current container
docker-compose down

# Rebuild with new dependencies
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Check logs
docker logs pra-app --tail 50
```

**Expected logs:**
```
INFO - Admin authentication routes registered successfully
INFO - Analytics routes registered successfully
INFO - Database tables created successfully
```

**NOT:**
```
WARNING - Admin authentication routes not available  ❌
ERROR - No module named 'argon2'  ❌
```

---

### Option 2: Install in Running Container (Temporary)

```bash
# Install argon2-cffi in running container
docker exec pra-app pip install argon2-cffi

# Restart container
docker restart pra-app

# Check logs
docker logs pra-app --tail 50
```

**⚠️ Warning:** This is temporary! Changes will be lost if container is rebuilt.

---

### Option 3: Deploy to Production (Recommended)

Push your changes to GitHub so CI/CD rebuilds the container on Raspberry Pi:

```bash
# Make sure requirements.txt has argon2-cffi
cat requirements.txt | grep argon2
# Should show: argon2-cffi==23.1.0

# Commit all changes
git add -A
git commit -m "Add argon2-cffi dependency for admin authentication"
git push origin master
```

**CI/CD will:**
1. Build Docker image with argon2-cffi
2. Deploy to Raspberry Pi
3. Restart container

**Then on Raspberry Pi:**
```bash
# SSH into Pi
ssh malsi123@your-raspberry-pi-ip

# Check logs after deployment
docker logs pra-app --tail 50 | grep -i admin

# Should see:
# INFO - Admin authentication routes registered successfully
```

---

## Verify It's Fixed

### 1. Check Container Has argon2

```bash
# Check if argon2-cffi is installed
docker exec pra-app pip list | grep argon2

# Should show:
# argon2-cffi         23.1.0
```

### 2. Check Admin Routes Registered

```bash
# Check logs
docker logs pra-app --tail 100 | grep -i "admin\|argon2"

# Should see:
# ✅ INFO - Admin authentication routes registered successfully

# Should NOT see:
# ❌ WARNING - Admin authentication routes not available
# ❌ ERROR - No module named 'argon2'
```

### 3. Test Admin Login Page

```bash
# Test endpoint exists
curl -I http://localhost:5001/admin/login

# Should return:
# HTTP/1.1 200 OK

# Should NOT return:
# HTTP/1.1 404 NOT FOUND ❌
```

### 4. Test in Browser

1. Visit: **http://localhost:5001/admin/login** (or https://skincares.work/admin/login)
2. Should see: Beautiful dark login page
3. Should NOT see: 404 error or blank page

---

## Create Admin User

After fixing the argon2 issue, you need to create an admin user:

### Option A: Use the Generator Script

```bash
# Generate credentials locally
pip3 install argon2-cffi
python3 generate_admin_creds.py

# Copy the username and hash
```

### Option B: Create Directly in Database

```bash
# After container is running with argon2
docker exec -it pra-app python -c "
from argon2 import PasswordHasher
from pra.app import create_app
from pra.models.admin_user import AdminUser
from pra.models.db import db

# Your credentials
username = 'maliha_admin'
passphrase = 'YourSecurePassphrase123!MinimumTwentyChars'

# Hash passphrase
ph = PasswordHasher()
passphrase_hash = ph.hash(passphrase)

# Create admin user
app = create_app()
with app.app_context():
    # Check if admin exists
    admin = AdminUser.query.filter_by(username=username).first()

    if admin:
        print(f'❌ Admin user {username} already exists')
    else:
        admin = AdminUser(username=username)
        admin.set_passphrase(passphrase)
        db.session.add(admin)
        db.session.commit()
        print(f'✅ Created admin user: {username}')
        print(f'   Passphrase: {passphrase}')
        print(f'   Hash: {passphrase_hash}')
"
```

---

## Alternative: Use Environment Variables

Instead of creating database entries, you can use environment variables:

**Add to `.env`:**
```bash
ADMIN_USERNAME=maliha_admin
ADMIN_PASSPHRASE_HASH=$argon2id$v=19$m=65536,t=3,p=4$YOUR_HASH_HERE
```

But first, generate the hash:

```bash
# Run locally with argon2-cffi installed
python3 -c "
from argon2 import PasswordHasher
ph = PasswordHasher()
passphrase = input('Enter passphrase: ')
print('Hash:', ph.hash(passphrase))
"
```

---

## Complete Fix Process

### Step 1: Rebuild Docker Container

```bash
# Rebuild locally
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Step 2: Verify Admin Routes Work

```bash
# Check logs
docker logs pra-app --tail 50

# Should see:
# ✅ INFO - Admin authentication routes registered successfully
```

### Step 3: Create Admin User

```bash
# Option A: Use generator
python3 generate_admin_creds.py

# Option B: Create in database (see above)

# Option C: Use environment variables (see above)
```

### Step 4: Test Login

1. Visit: http://localhost:5001/admin/login
2. Enter username and passphrase
3. Should successfully log in!

---

## For Production (Raspberry Pi)

### Step 1: Push Changes

```bash
git add requirements.txt
git add pra/models/admin_user.py
git add pra/routes/admin_auth.py
git add pra/templates/admin_login.html
git add pra/app.py
git commit -m "Add admin authentication with argon2-cffi"
git push origin master
```

### Step 2: Wait for CI/CD

Check: https://github.com/fablihamaliha/PRA/actions

Should see workflow rebuild and deploy.

### Step 3: SSH and Check

```bash
ssh malsi123@your-pi-ip

# Check logs
docker logs pra-app --tail 50 | grep admin

# Should see:
# INFO - Admin authentication routes registered successfully
```

### Step 4: Add Admin Credentials to .env

```bash
# On Raspberry Pi
nano ~/PRA/.env

# Add:
ADMIN_USERNAME=your_username
ADMIN_PASSPHRASE_HASH=your_hash_from_generator

# Save and restart
docker restart pra-app
```

### Step 5: Test

Visit: https://skincares.work/admin/login

---

## Summary

**Root Cause:** argon2-cffi not installed in Docker container

**Solution:** Rebuild Docker container to install argon2-cffi from requirements.txt

**Steps:**
1. ✅ Rebuild container: `docker-compose build --no-cache && docker-compose up -d`
2. ✅ Verify logs: `docker logs pra-app --tail 50`
3. ✅ Create admin user: Use generator or environment variables
4. ✅ Test login: Visit `/admin/login`

---

**After fixing, you'll be able to log in successfully!**
