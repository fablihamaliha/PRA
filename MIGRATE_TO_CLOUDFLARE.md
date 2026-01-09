# 🚀 Quick Migration: ngrok → Cloudflare Tunnel

## Why Migrate?

| Feature | ngrok (current) | Cloudflare (new) |
|---------|----------------|------------------|
| Custom Domain | ❌ Paid ($8/mo) | ✅ Free |
| SSL Certificate | ✅ Auto | ✅ Auto |
| CDN | ❌ No | ✅ Global CDN |
| DDoS Protection | ⚠️ Limited | ✅ Enterprise |
| Session Timeout | ⚠️ Yes | ✅ No |
| **Monthly Cost** | **$0-20** | **$0** |

---

## Quick Start (15 Minutes)

### Step 1: Install Cloudflared (2 min)

```bash
# On your Raspberry Pi
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
chmod +x cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
cloudflared --version
```

### Step 2: Authenticate (1 min)

```bash
cloudflared tunnel login
# This opens browser - select skincares.work domain
```

### Step 3: Create Tunnel (1 min)

```bash
cloudflared tunnel create pra-tunnel
# SAVE THE TUNNEL ID that appears!
```

### Step 4: Configure Tunnel (3 min)

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Paste this (replace `<TUNNEL-ID>` and `<USERNAME>`):

```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /home/<YOUR-USERNAME>/.cloudflared/<YOUR-TUNNEL-ID>.json

ingress:
  - hostname: skincares.work
    service: http://localhost:5001
    originRequest:
      noTLSVerify: true
  
  - hostname: www.skincares.work
    service: http://localhost:5001
    originRequest:
      noTLSVerify: true
  
  - service: http_status:404
```

### Step 5: Set up DNS (2 min)

```bash
cloudflared tunnel route dns pra-tunnel skincares.work
cloudflared tunnel route dns pra-tunnel www.skincares.work
```

### Step 6: Test (1 min)

```bash
cloudflared tunnel run pra-tunnel
# Open browser: https://skincares.work
# If it works, press Ctrl+C and continue
```

### Step 7: Install as Service (3 min)

```bash
sudo nano /etc/systemd/system/cloudflared.service
```

Paste this (replace `User=pi` with your username):

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/cloudflared tunnel run pra-tunnel
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
sudo systemctl status cloudflared
```

### Step 8: Verify (2 min)

Test these URLs:
- ✅ https://skincares.work
- ✅ https://www.skincares.work
- ✅ https://skincares.work/auth
- ✅ https://skincares.work/analytics/dashboard

### Step 9: Stop ngrok (1 min)

```bash
# Once Cloudflare is working, stop ngrok
sudo systemctl stop ngrok
sudo systemctl disable ngrok
```

---

## ✅ Done!

Your app is now live at: **https://skincares.work**

**Benefits you now have:**
- ✅ Professional custom domain
- ✅ Free SSL certificate
- ✅ Cloudflare CDN (faster worldwide)
- ✅ DDoS protection
- ✅ No monthly fees
- ✅ No session timeouts

---

## Cloudflare Dashboard Configuration (Optional)

### 1. SSL/TLS Settings
- Go to: https://dash.cloudflare.com
- SSL/TLS → **Full (strict)**
- Always Use HTTPS → **ON**

### 2. Speed Settings
- Speed → Auto Minify → **ON** (JS, CSS, HTML)
- Speed → Brotli → **ON**

### 3. Security (Optional)
- Security → WAF → Enable managed rules
- Security → Rate Limiting → Add custom rules

---

## Troubleshooting

### Tunnel not connecting?
```bash
sudo journalctl -u cloudflared -f
```

### 502 Bad Gateway?
```bash
# Check if PRA app is running
docker ps | grep pra-app
docker logs pra-app
```

### DNS not resolving?
```bash
# Wait 5-10 minutes for DNS propagation
dig skincares.work
```

---

## Complete Guide

For detailed setup instructions, see: [CLOUDFLARE_SETUP_GUIDE.md](CLOUDFLARE_SETUP_GUIDE.md)

---

**Congratulations!** 🎉

You now have a professional domain with enterprise-grade infrastructure at **zero cost**!
