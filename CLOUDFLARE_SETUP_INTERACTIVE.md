# Interactive Cloudflare Tunnel Setup Guide

Follow these steps exactly in your terminal.

---

## 🔌 Step 1: Connect to Your Raspberry Pi

Open Terminal and run:
```bash
ssh pi@192.168.1.68
```

Enter your password when prompted.

**Expected output:**
```
pi@192.168.1.68's password: [enter password]
Last login: ...
pi@raspberrypi:~ $
```

---

## 📥 Step 2: Download cloudflared

Copy and paste this command:
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
```

**Expected output:**
```
Resolving github.com...
Connecting to github.com...
HTTP request sent, awaiting response... 200 OK
Length: ... (27M) [application/octet-stream]
Saving to: 'cloudflared-linux-arm64'
cloudflared-linux-arm64  100%[===================>]  27.35M  ...
```

**What this does:** Downloads the Cloudflare Tunnel client for Raspberry Pi (ARM64).

---

## ⚙️ Step 3: Install cloudflared

Run these commands one by one:

```bash
chmod +x cloudflared-linux-arm64
```
**What this does:** Makes the file executable

```bash
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
```
**What this does:** Moves it to system path so you can run it from anywhere

```bash
cloudflared --version
```

**Expected output:**
```
cloudflared version 2024.x.x (built ...)
```

✅ If you see a version number, installation is successful!

---

## 🔐 Step 4: Authenticate with Cloudflare

Run this command:
```bash
cloudflared tunnel login
```

**Expected output:**
```
Please open the following URL and log in with your Cloudflare account:

https://dash.cloudflare.com/argotunnel?callback=https://login.cloudflareaccess.org/...

Leave cloudflared running to download the cert automatically.
```

**What to do:**
1. **Copy the URL** that appears in the terminal
2. **Open it in your browser** (on your computer, not the Pi)
3. **Log in to Cloudflare** with your account
4. **Select your domain: skincares.work**
5. **Click "Authorize"**

**Expected in terminal after authorization:**
```
You have successfully logged in.
If you wish to copy your credentials to a server, they have been saved to:
/home/pi/.cloudflared/cert.pem
```

✅ Certificate saved! You're authenticated.

---

## 🚇 Step 5: Create a Tunnel

Run this command:
```bash
cloudflared tunnel create pra-tunnel
```

**Expected output:**
```
Tunnel credentials written to /home/pi/.cloudflared/<LONG-UUID>.json.
cloudflared chose this file based on where your origin certificate was found.
Keep this file secret. To revoke these credentials, delete the tunnel.

Created tunnel pra-tunnel with id <TUNNEL-ID>
```

**IMPORTANT:**
- Copy the `<TUNNEL-ID>` (the UUID after "with id")
- You'll need this in the next step
- It looks like: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

✅ Keep this tunnel ID safe!

---

## 📝 Step 6: Create Configuration File

Create the config directory:
```bash
mkdir -p ~/.cloudflared
```

Now create the config file:
```bash
nano ~/.cloudflared/config.yml
```

**What to paste:**

Replace `<YOUR-TUNNEL-ID>` with the UUID from Step 5:

```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /home/pi/.cloudflared/<YOUR-TUNNEL-ID>.json

ingress:
  - hostname: skincares.work
    service: http://localhost:5001
  - hostname: www.skincares.work
    service: http://localhost:5001
  - service: http_status:404
```

**Example (with fake ID):**
```yaml
tunnel: a1b2c3d4-e5f6-7890-abcd-ef1234567890
credentials-file: /home/pi/.cloudflared/a1b2c3d4-e5f6-7890-abcd-ef1234567890.json

ingress:
  - hostname: skincares.work
    service: http://localhost:5001
  - hostname: www.skincares.work
    service: http://localhost:5001
  - service: http_status:404
```

**To save the file:**
1. Press `Ctrl + X`
2. Press `Y` (yes to save)
3. Press `Enter` (confirm filename)

✅ Configuration saved!

---

## 🌐 Step 7: Configure DNS in Cloudflare Dashboard

**Open your browser** and go to:
```
https://dash.cloudflare.com
```

1. **Click on your domain:** `skincares.work`
2. **Go to DNS section** (left sidebar)
3. **Click "Add record"**

### Add First DNS Record:
- **Type:** CNAME
- **Name:** `@` (or `skincares.work`)
- **Target:** `<YOUR-TUNNEL-ID>.cfargotunnel.com`
  - Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890.cfargotunnel.com`
- **Proxy status:** ☁️ Proxied (orange cloud - should be ON)
- **TTL:** Auto
- Click **Save**

### Add Second DNS Record:
- **Type:** CNAME
- **Name:** `www`
- **Target:** `<YOUR-TUNNEL-ID>.cfargotunnel.com`
- **Proxy status:** ☁️ Proxied (orange cloud - should be ON)
- **TTL:** Auto
- Click **Save**

✅ DNS configured! You should see two CNAME records in your DNS list.

---

## 🧪 Step 8: Test the Tunnel

**Back in your SSH terminal**, run:
```bash
cloudflared tunnel run pra-tunnel
```

**Expected output:**
```
INFO  Registered tunnel connection     connIndex=0 connection=<ID>
INFO  Registered tunnel connection     connIndex=1 connection=<ID>
INFO  Registered tunnel connection     connIndex=2 connection=<ID>
INFO  Registered tunnel connection     connIndex=3 connection=<ID>
```

If you see "Registered tunnel connection", it's working! 🎉

**Test your website:**
- Open browser: `https://skincares.work`
- You should see your app!

**If it works:**
- Press `Ctrl + C` in the terminal to stop the tunnel
- Continue to Step 9 to make it permanent

**If it doesn't work:**
- Wait 2-3 minutes (DNS propagation)
- Try again
- Check troubleshooting section below

---

## 🔄 Step 9: Make Tunnel Auto-Start on Boot

Create systemd service file:
```bash
sudo nano /etc/systemd/system/cloudflared.service
```

**Paste this exactly:**
```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/cloudflared tunnel run pra-tunnel
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

**Save:** `Ctrl + X`, then `Y`, then `Enter`

Now enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

Check if it's running:
```bash
sudo systemctl status cloudflared
```

**Expected output:**
```
● cloudflared.service - Cloudflare Tunnel
   Loaded: loaded (/etc/systemd/system/cloudflared.service; enabled)
   Active: active (running) since ...
```

✅ If you see "active (running)", the tunnel is running and will auto-start on boot!

---

## ✅ Step 10: Final Verification

### Check tunnel status:
```bash
sudo systemctl status cloudflared
```
Should show: `active (running)`

### Check Flask app is running:
```bash
docker ps
```
Should show: `pra-app` container running

```bash
curl http://localhost:5001/health
```
Should return: `{"status":"healthy","message":"PRRA API is running"}`

### Test your domain:
Open in browser: `https://skincares.work`

**Expected:**
- Your app loads ✅
- HTTPS (padlock icon) ✅
- No certificate warnings ✅

---

## 🎉 SUCCESS!

If everything above worked, you now have:
- ✅ Custom domain: https://skincares.work
- ✅ Free SSL/TLS certificate
- ✅ CDN and DDoS protection
- ✅ Persistent URL (never changes)
- ✅ Auto-starts on Raspberry Pi reboot
- ✅ No monthly fees

---

## 🔧 Troubleshooting

### "Site can't be reached" after 5+ minutes

**Check DNS:**
```bash
nslookup skincares.work
```
Should show Cloudflare IPs (starting with 172.x or 104.x)

**Check tunnel logs:**
```bash
sudo journalctl -u cloudflared -f
```
Look for errors

**Restart tunnel:**
```bash
sudo systemctl restart cloudflared
```

---

### "502 Bad Gateway"

**Check Flask app:**
```bash
docker logs pra-app --tail 50
```

**Restart Flask app:**
```bash
docker restart pra-app
```

**Check if app is listening on port 5001:**
```bash
curl http://localhost:5001/health
```

---

### Tunnel shows as running but site doesn't load

**Verify config file:**
```bash
cat ~/.cloudflared/config.yml
```

Check:
- Tunnel ID matches what you created
- Port is 5001 (not 5000)
- Credentials file path is correct

**Test tunnel manually:**
```bash
sudo systemctl stop cloudflared
cloudflared tunnel run pra-tunnel
```
Watch for errors

---

### Certificate or authentication errors

**Re-authenticate:**
```bash
cloudflared tunnel login
```

**List your tunnels:**
```bash
cloudflared tunnel list
```
Verify "pra-tunnel" is listed

---

## 📋 Useful Commands Reference

```bash
# Check tunnel status
sudo systemctl status cloudflared

# View live logs
sudo journalctl -u cloudflared -f

# Restart tunnel
sudo systemctl restart cloudflared

# Stop tunnel
sudo systemctl stop cloudflared

# Start tunnel
sudo systemctl start cloudflared

# List tunnels
cloudflared tunnel list

# Test config
cloudflared tunnel run pra-tunnel

# Check Flask app
docker ps
docker logs pra-app
curl http://localhost:5001/health
```

---

## 🚀 Next Steps After Setup

1. **Test admin login:**
   - Go to: https://skincares.work/auth
   - Login with: admin@admin.com
   - Should redirect to analytics dashboard

2. **Enable admin security features** (when ready):
   ```bash
   nano ~/.env  # or wherever your .env file is
   ```
   Add:
   ```
   ENABLE_ADMIN_DASHBOARD=true
   ADMIN_DASHBOARD_PATH=a7f3k9m2x5b8c1d4e6g0h7
   ```
   Then: `docker restart pra-app`

3. **Remove ngrok** (if installed):
   ```bash
   pkill ngrok
   ```

4. **Push to GitHub** and let CI/CD deploy:
   ```bash
   git add .
   git commit -m "Add Cloudflare Tunnel configuration"
   git push origin master
   ```

---

## 📞 Need Help?

If you get stuck at any step, let me know:
1. What step number you're on
2. What command you ran
3. What error message you see
4. What the output looks like

I'll help you debug! 🔍

---

**Last Updated:** 2026-01-09
