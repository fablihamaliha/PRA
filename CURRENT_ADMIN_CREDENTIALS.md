# Current Admin Login Credentials

**Last Updated:** 2026-01-09 23:20

---

## ✅ Working Credentials (Verified)

### Username
```
maliha_admin
```

### Passphrase
```
MySecureAdminPass2026!MinTwentyChars
```

**⚠️ IMPORTANT:**
- The passphrase is **case-sensitive**
- Include the `!` exclamation mark
- No spaces before or after

---

## 🌐 Login URLs

### Local Development
**URL:** http://localhost:5001/admin/login

### Production (Raspberry Pi)
**URL:** https://skincares.work/admin/login

---

## ❌ Common Mistakes

### Wrong Username
- ❌ `admin@admin.com` (old system, doesn't work anymore)
- ❌ `admin`
- ❌ `maliha`
- ✅ `maliha_admin` (correct!)

### Wrong Passphrase
- ❌ Missing the `!` exclamation mark
- ❌ Wrong capitalization (it's case-sensitive)
- ❌ Extra spaces
- ✅ `MySecureAdminPass2026!MinTwentyChars` (exactly this)

---

## 🔍 Testing Your Credentials

You can test if the credentials work by running:

```bash
docker exec pra-app python -c "
from pra.app import create_app
from pra.models.admin_user import AdminUser
from pra.models.db import db

app = create_app()
with app.app_context():
    admin = AdminUser.query.filter_by(username='maliha_admin').first()

    # Test with the passphrase
    test_pass = 'MySecureAdminPass2026!MinTwentyChars'
    result = admin.check_passphrase(test_pass)

    if result:
        print('✅ Credentials are CORRECT')
    else:
        print('❌ Passphrase does NOT match')
"
```

---

## 🔓 Reset Failed Login Attempts

If you're getting "too many failed attempts", clear them:

```bash
docker exec pra-app python -c "
from pra.app import create_app
from pra.models.admin_user import FailedLoginAttempt
from pra.models.db import db

app = create_app()
with app.app_context():
    FailedLoginAttempt.query.delete()
    db.session.commit()
    print('✅ Cleared all failed login attempts')
"
```

---

## 🆕 Create a New Admin User

If you want different credentials:

```bash
docker exec pra-app python -c "
from argon2 import PasswordHasher
from pra.app import create_app
from pra.models.admin_user import AdminUser
from pra.models.db import db

# Your new credentials
new_username = 'your_username_here'
new_passphrase = 'YourNewPassphraseHere_MinTwentyChars'

app = create_app()
with app.app_context():
    # Check if user already exists
    existing = AdminUser.query.filter_by(username=new_username).first()

    if existing:
        # Update existing user
        existing.set_passphrase(new_passphrase)
        db.session.commit()
        print(f'✅ Updated passphrase for: {new_username}')
    else:
        # Create new admin user
        admin = AdminUser(username=new_username)
        admin.set_passphrase(new_passphrase)
        db.session.add(admin)
        db.session.commit()
        print(f'✅ Created new admin user: {new_username}')

    print(f'Username: {new_username}')
    print(f'Passphrase: {new_passphrase}')
"
```

---

## 📊 Recent Login History

**Last successful login:**
- Time: 2026-01-09 23:09:27
- Username: `maliha_admin`
- IP: 172.18.0.1
- Status: ✅ Success
- Dashboard accessed: ✅ Yes (at 23:09:28)

**Recent failed attempts:**
- 3 attempts with username `admin@admin.com` (old system)
- All before the successful login

---

## 🛠️ Troubleshooting Steps

### Step 1: Verify Admin User Exists
```bash
docker exec pra-app python -c "
from pra.app import create_app
from pra.models.admin_user import AdminUser

app = create_app()
with app.app_context():
    admin = AdminUser.query.filter_by(username='maliha_admin').first()
    if admin:
        print('✅ Admin user exists')
        print(f'Username: {admin.username}')
        print(f'Active: {admin.is_active}')
    else:
        print('❌ Admin user not found')
"
```

### Step 2: Check Application Logs
```bash
docker logs pra-app --tail 30 | grep -i "admin\|login"
```

### Step 3: Test Login via curl
```bash
curl -X POST http://localhost:5001/admin/login \
  -H "Content-Type: application/json" \
  --data-binary @- << 'EOF'
{
  "username": "maliha_admin",
  "passphrase": "MySecureAdminPass2026!MinTwentyChars"
}
EOF
```

**Expected response:**
```json
{
  "success": true,
  "message": "Login successful",
  "redirect": "/analytics/dashboard"
}
```

### Step 4: Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Try logging in
4. Look for any JavaScript errors

### Step 5: Check Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Try logging in
4. Click on the `/admin/login` request
5. Check the response

---

## 📝 Copy-Paste Credentials

**For easy copy-paste:**

```
Username: maliha_admin
Passphrase: MySecureAdminPass2026!MinTwentyChars
```

---

## 🎯 Quick Test

Try this RIGHT NOW:

1. Open browser: http://localhost:5001/admin/login
2. Clear both fields completely
3. Copy this username: `maliha_admin`
4. Paste into username field
5. Copy this passphrase: `MySecureAdminPass2026!MinTwentyChars`
6. Paste into passphrase field
7. Click "Log In"

Should work! ✅

---

**If you're still having issues, please:**
1. Tell me what error message you see exactly
2. Run the test command above to verify credentials
3. Check browser console for JavaScript errors
