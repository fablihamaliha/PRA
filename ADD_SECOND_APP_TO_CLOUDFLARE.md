# Add Second App to Existing Cloudflare Tunnel Setup

You already have cloudflared installed for your portfolio app. Now you'll add the PRA app (skincares.work) alongside it.

---

## Option 1: Separate Tunnel (Recommended)

Create a separate tunnel for the PRA app. This keeps them independent.

### Step 1: SSH to Raspberry Pi
```bash
ssh pi@192.168.1.68
```

### Step 2: Create New Tunnel for PRA
```bash
cloudflared tunnel create pra-tunnel
```

**Expected output:**
```
Created tunnel pra-tunnel with id <PRA-TUNNEL-ID>
```

**Save this tunnel ID!** You'll need it in the next steps.

### Step 3: Create Config for PRA Tunnel
```bash
nano ~/.cloudflared/config-pra.yml
```

**Paste this** (replace `<PRA-TUNNEL-ID>` with your actual ID):
```yaml
tunnel: <PRA-TUNNEL-ID>
credentials-file: /home/pi/.cloudflared/<PRA-TUNNEL-ID>.json

ingress:
  - hostname: skincares.work
    service: http://localhost:5001
  - hostname: www.skincares.work
    service: http://localhost:5001
  - service: http_status:404
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 4: Add DNS Records in Cloudflare Dashboard

Go to: https://dash.cloudflare.com

1. **Select domain:** `skincares.work`
2. **Go to DNS**
3. **Add CNAME record #1:**
   - Type: CNAME
   - Name: `@`
   - Target: `<PRA-TUNNEL-ID>.cfargotunnel.com`
   - Proxy: ON (orange cloud)

4. **Add CNAME record #2:**
   - Type: CNAME
   - Name: `www`
   - Target: `<PRA-TUNNEL-ID>.cfargotunnel.com`
   - Proxy: ON (orange cloud)

### Step 5: Create Systemd Service for PRA Tunnel
```bash
sudo nano /etc/systemd/system/cloudflared-pra.service
```

**Paste this:**
```ini
[Unit]
Description=Cloudflare Tunnel - PRA App
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/cloudflared tunnel --config /home/pi/.cloudflared/config-pra.yml run pra-tunnel
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 6: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-pra
sudo systemctl start cloudflared-pra
sudo systemctl status cloudflared-pra
```

**Expected output:**
```
● cloudflared-pra.service - Cloudflare Tunnel - PRA App
   Active: active (running)
```

### Step 7: Verify
```bash
# Check PRA tunnel
sudo systemctl status cloudflared-pra

# Check portfolio tunnel (should still be running)
sudo systemctl status cloudflared

# List all tunnels
cloudflared tunnel list
```

**Test the website:**
```
https://skincares.work
```

✅ Both apps should now be running with their own tunnels!

---

## Option 2: Single Tunnel, Multiple Apps (Alternative)

Use your existing tunnel to route both domains. Simpler but both apps depend on one tunnel.

### Step 1: Find Your Existing Tunnel Config

```bash
# Check where your portfolio tunnel config is
cat ~/.cloudflared/config.yml
```

You should see something like:
```yaml
tunnel: <YOUR-PORTFOLIO-TUNNEL-ID>
credentials-file: /home/pi/.cloudflared/<YOUR-PORTFOLIO-TUNNEL-ID>.json

ingress:
  - hostname: yourportfolio.com
    service: http://localhost:XXXX
  - service: http_status:404
```

### Step 2: Add PRA App to Existing Config

```bash
nano ~/.cloudflared/config.yml
```

**Modify to add PRA routes** (keep your existing portfolio routes):
```yaml
tunnel: <YOUR-PORTFOLIO-TUNNEL-ID>
credentials-file: /home/pi/.cloudflared/<YOUR-PORTFOLIO-TUNNEL-ID>.json

ingress:
  # Your existing portfolio routes
  - hostname: yourportfolio.com
    service: http://localhost:XXXX
  - hostname: www.yourportfolio.com
    service: http://localhost:XXXX

  # Add PRA app routes
  - hostname: skincares.work
    service: http://localhost:5001
  - hostname: www.skincares.work
    service: http://localhost:5001

  # Catch-all (must be last)
  - service: http_status:404
```

**Note:** Change `XXXX` to your portfolio app's port.

Save: `Ctrl+X`, `Y`, `Enter`

### Step 3: Add DNS for skincares.work

Go to: https://dash.cloudflare.com

1. **Select:** `skincares.work` domain
2. **Add CNAME record #1:**
   - Type: CNAME
   - Name: `@`
   - Target: `<YOUR-PORTFOLIO-TUNNEL-ID>.cfargotunnel.com`
   - Proxy: ON

3. **Add CNAME record #2:**
   - Type: CNAME
   - Name: `www`
   - Target: `<YOUR-PORTFOLIO-TUNNEL-ID>.cfargotunnel.com`
   - Proxy: ON

### Step 4: Restart Your Existing Tunnel

```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

### Step 5: Verify

```bash
# Check both apps work
curl -I https://yourportfolio.com
curl -I https://skincares.work
```

Both should return `200 OK`

✅ Both apps now route through one tunnel!

---

## Which Option Should You Choose?

### Option 1: Separate Tunnels (Recommended)
**Pros:**
- Independent - if one fails, other keeps working
- Easier to manage and debug
- Can stop/restart each app separately

**Cons:**
- Two systemd services to manage
- Uses slightly more resources (minimal)

### Option 2: Single Tunnel
**Pros:**
- Simpler - one tunnel for everything
- Less configuration files

**Cons:**
- Single point of failure
- Both apps go down if tunnel fails
- Config file gets complex with many apps

**My recommendation:** Use **Option 1** (separate tunnels) for better isolation and reliability.

---

## Troubleshooting

### Check what tunnels you have:
```bash
cloudflared tunnel list
```

### Check what services are running:
```bash
sudo systemctl list-units | grep cloudflared
```

### View logs:
```bash
# Portfolio tunnel
sudo journalctl -u cloudflared -f

# PRA tunnel (if using Option 1)
sudo journalctl -u cloudflared-pra -f
```

### Check app is listening:
```bash
# Portfolio app
curl http://localhost:XXXX/

# PRA app
curl http://localhost:5001/health
```

### DNS issues:
```bash
# Check DNS for skincares.work
nslookup skincares.work

# Should show Cloudflare IPs
```

---

## Summary Commands for Option 1

```bash
# Create tunnel
cloudflared tunnel create pra-tunnel

# Create config
nano ~/.cloudflared/config-pra.yml

# Create service
sudo nano /etc/systemd/system/cloudflared-pra.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-pra
sudo systemctl start cloudflared-pra

# Check status
sudo systemctl status cloudflared-pra
```

Then add DNS records in Cloudflare dashboard.

---

## Need Help?

Tell me:
1. Which option you want to use (1 or 2)
2. Your portfolio app details (domain, port)
3. What your existing cloudflared config looks like

I'll help you configure it! 🚀

---

**Last Updated:** 2026-01-09
