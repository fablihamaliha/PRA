# Complete Troubleshooting Commands Reference

**Project:** PRA - Product Recommendation Application
**Environment:** Raspberry Pi with Cloudflare Tunnel
**Date:** 2026-01-09

---

## Table of Contents

1. [System Information](#system-information)
2. [Cloudflare Tunnel Troubleshooting](#cloudflare-tunnel-troubleshooting)
3. [Docker Container Troubleshooting](#docker-container-troubleshooting)
4. [Network and DNS Troubleshooting](#network-and-dns-troubleshooting)
5. [Git and Deployment Troubleshooting](#git-and-deployment-troubleshooting)
6. [Database Troubleshooting](#database-troubleshooting)
7. [Log Analysis](#log-analysis)
8. [Service Management](#service-management)
9. [Emergency Fixes](#emergency-fixes)

---

## System Information

### Check System Details
```bash
# Current username
whoami

# Home directory
echo $HOME

# System hostname
hostname

# OS information
uname -a

# Disk space
df -h

# Memory usage
free -h

# CPU info
lscpu

# Check running processes
top
# Or for better view:
htop
```

### Check Network Configuration
```bash
# IP address
ip addr show

# Network interfaces
ifconfig

# Default gateway
ip route

# Check if internet is working
ping -c 4 8.8.8.8
ping -c 4 google.com
```

---

## Cloudflare Tunnel Troubleshooting

### Check Tunnel Status

```bash
# Check if cloudflared is installed
cloudflared --version

# List all tunnels
cloudflared tunnel list

# Get detailed tunnel info
cloudflared tunnel info pra-tunnel

# Check specific tunnel by ID
cloudflared tunnel info ce08136f-44de-47a5-8535-02ae50451922
```

### Service Status

```bash
# Check PRA tunnel service status
sudo systemctl status cloudflared-pra

# Check if service is enabled
sudo systemctl is-enabled cloudflared-pra

# Check if service is active
sudo systemctl is-active cloudflared-pra

# List all cloudflared services
sudo systemctl list-units | grep cloudflared
```

### View Tunnel Logs

```bash
# View last 50 lines
sudo journalctl -u cloudflared-pra -n 50 --no-pager

# View logs in real-time (follow mode)
sudo journalctl -u cloudflared-pra -f

# View logs from last 1 hour
sudo journalctl -u cloudflared-pra --since "1 hour ago"

# View logs from specific time
sudo journalctl -u cloudflared-pra --since "2026-01-09 12:00:00"

# View logs with priority (errors only)
sudo journalctl -u cloudflared-pra -p err

# Export logs to file
sudo journalctl -u cloudflared-pra -n 200 > /tmp/cloudflared-logs.txt
```

### Restart Tunnel

```bash
# Restart PRA tunnel
sudo systemctl restart cloudflared-pra

# Stop tunnel
sudo systemctl stop cloudflared-pra

# Start tunnel
sudo systemctl start cloudflared-pra

# Reload systemd configuration
sudo systemctl daemon-reload
```

### Test Tunnel Manually (Without Service)

```bash
# Stop the service first
sudo systemctl stop cloudflared-pra

# Run tunnel manually for debugging
cloudflared tunnel --config ~/.cloudflared/config-pra.yml run pra-tunnel

# Press Ctrl+C to stop when done

# Restart service after testing
sudo systemctl start cloudflared-pra
```

### Check Tunnel Configuration

```bash
# View config file
cat ~/.cloudflared/config-pra.yml

# Check if credentials file exists
ls -la ~/.cloudflared/ce08136f-44de-47a5-8535-02ae50451922.json

# List all cloudflared files
ls -la ~/.cloudflared/

# Verify config syntax (no output = good)
cloudflared tunnel --config ~/.cloudflared/config-pra.yml validate
```

### Re-authenticate Cloudflare

```bash
# If certificate errors occur
cloudflared tunnel login

# Check certificate
ls -la ~/.cloudflared/cert.pem

# View certificate details
openssl x509 -in ~/.cloudflared/cert.pem -text -noout
```

---

## Docker Container Troubleshooting

### Check Container Status

```bash
# List all containers
docker ps -a

# List running containers only
docker ps

# Check specific container
docker ps | grep pra-app

# Get detailed container info
docker inspect pra-app

# Check container resource usage
docker stats pra-app --no-stream
```

### View Container Logs

```bash
# View last 50 lines
docker logs pra-app --tail 50

# Follow logs in real-time
docker logs pra-app -f

# View logs with timestamps
docker logs pra-app -t

# View logs from last 10 minutes
docker logs pra-app --since 10m

# Export logs to file
docker logs pra-app > /tmp/pra-app-logs.txt 2>&1
```

### Restart Container

```bash
# Restart container
docker restart pra-app

# Stop container
docker stop pra-app

# Start container
docker start pra-app

# Remove and recreate (careful!)
docker stop pra-app
docker rm pra-app
# Then recreate with docker run command
```

### Access Container Shell

```bash
# Execute bash in running container
docker exec -it pra-app bash

# Or if bash not available:
docker exec -it pra-app sh

# Run single command
docker exec pra-app ls -la /app

# Check Flask app inside container
docker exec pra-app python -c "from pra.app import create_app; app = create_app(); print('App OK')"
```

### Test App Locally

```bash
# Test health endpoint
curl http://localhost:5001/health

# Test with verbose output
curl -v http://localhost:5001/health

# Test with headers
curl -I http://localhost:5001/health

# Test specific route
curl http://localhost:5001/

# Test from inside container
docker exec pra-app curl http://localhost:5001/health
```

### Check Docker Images

```bash
# List images
docker images

# Check image size
docker images | grep pra

# Pull latest image
docker pull ghcr.io/fablihamaliha/pra:latest

# Remove old images
docker image prune -f
```

### Container Network Troubleshooting

```bash
# Check container network
docker network ls

# Inspect network
docker network inspect bridge

# Check container IP
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' pra-app

# Test connectivity from host to container
docker exec pra-app ping -c 4 host.docker.internal
```

---

## Network and DNS Troubleshooting

### Check DNS Resolution

```bash
# Check DNS for main domain
nslookup skincares.work

# Check with specific DNS server
nslookup skincares.work 8.8.8.8

# Detailed DNS query
dig skincares.work

# Check DNS propagation
dig skincares.work +trace

# Check CNAME records
dig CNAME skincares.work

# Check from multiple DNS servers
for server in 8.8.8.8 1.1.1.1 208.67.222.222; do
  echo "=== DNS Server: $server ==="
  nslookup skincares.work $server
done
```

### Test Website Connectivity

```bash
# Test HTTPS connection
curl -I https://skincares.work

# Test with full response
curl https://skincares.work

# Test with timing information
curl -w "@-" -o /dev/null -s https://skincares.work <<'EOF'
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
EOF

# Test with verbose output
curl -v https://skincares.work

# Test SSL certificate
curl -vI https://skincares.work 2>&1 | grep -A 10 "SSL certificate"

# Check SSL certificate details
openssl s_client -connect skincares.work:443 -servername skincares.work < /dev/null
```

### Check Port Availability

```bash
# Check if port 5001 is listening
netstat -tuln | grep 5001

# Or using ss
ss -tuln | grep 5001

# Check what's using port 5001
sudo lsof -i :5001

# Check all listening ports
netstat -tuln

# Test connection to localhost port
telnet localhost 5001

# Or using nc
nc -zv localhost 5001
```

### Flush DNS Cache (If Needed)

```bash
# On Raspberry Pi
sudo systemd-resolve --flush-caches

# Or restart DNS service
sudo systemctl restart systemd-resolved

# Check DNS status
systemd-resolve --status
```

---

## Git and Deployment Troubleshooting

### Check Git Status

```bash
# Current branch
git branch

# Check status
git status

# Check remote
git remote -v

# View recent commits
git log -5 --oneline

# Check if local is behind remote
git fetch
git status
```

### View Deployment Logs (GitHub Actions)

```bash
# From your local machine, open:
# https://github.com/fablihamaliha/PRA/actions

# Or use GitHub CLI if installed:
gh run list
gh run view <run-id>
gh run view --log
```

### Pull Latest Changes

```bash
# Fetch and pull latest
git fetch origin
git pull origin master

# Force pull (careful - overwrites local changes)
git fetch origin
git reset --hard origin/master

# Check what will be pulled
git fetch origin
git diff master origin/master
```

### Push Changes

```bash
# Check what will be pushed
git status
git diff --cached

# Push to master
git push origin master

# Push specific branch
git push origin <branch-name>

# Force push (very careful!)
git push --force origin master
```

### Git Troubleshooting

```bash
# If push fails, check remote
git remote show origin

# Update remote URL if needed
git remote set-url origin https://github.com/fablihamaliha/PRA.git

# Check git config
git config --list

# Reset to specific commit
git reset --hard <commit-hash>
```

---

## Database Troubleshooting

### PostgreSQL Status

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Or check with docker if in container
docker ps | grep postgres

# Connect to database
psql -U prra_user -d prra_db -h localhost

# Check database size
psql -U prra_user -d prra_db -h localhost -c "SELECT pg_size_pretty(pg_database_size('prra_db'));"

# List tables
psql -U prra_user -d prra_db -h localhost -c "\dt"

# Check table row counts
psql -U prra_user -d prra_db -h localhost -c "
SELECT schemaname,relname,n_live_tup
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
"
```

### Database Connection Test

```bash
# Test database connection
docker exec pra-app python -c "
from pra.models.db import db
from pra.app import create_app
app = create_app()
with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print('✅ Database connection OK')
    except Exception as e:
        print(f'❌ Database error: {e}')
"
```

### Run Database Migrations

```bash
# Check migration status
docker exec pra-app python -m flask db current

# Run migrations
docker exec pra-app python -m flask db upgrade

# Downgrade migration
docker exec pra-app python -m flask db downgrade

# Create new migration
docker exec pra-app python -m flask db migrate -m "description"
```

### Backup Database

```bash
# Backup database
docker exec -t postgres-container pg_dump -U prra_user prra_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Or if PostgreSQL is on host:
pg_dump -U prra_user -h localhost prra_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql -U prra_user -h localhost prra_db < backup_20260109_120000.sql
```

---

## Log Analysis

### Application Logs

```bash
# Flask app logs (from container)
docker logs pra-app | grep ERROR
docker logs pra-app | grep WARNING
docker logs pra-app | grep Exception

# Search for specific error
docker logs pra-app 2>&1 | grep "ModuleNotFoundError"

# Count error occurrences
docker logs pra-app 2>&1 | grep -c ERROR

# Show errors with context (5 lines before and after)
docker logs pra-app 2>&1 | grep -A 5 -B 5 ERROR
```

### System Logs

```bash
# View all system logs
journalctl -n 100

# Filter by time
journalctl --since "1 hour ago"
journalctl --since "2026-01-09 10:00:00" --until "2026-01-09 12:00:00"

# Follow system logs
journalctl -f

# View boot logs
journalctl -b

# View kernel logs
journalctl -k
```

### Analyze Logs for Patterns

```bash
# Find most common errors in app logs
docker logs pra-app 2>&1 | grep ERROR | sort | uniq -c | sort -rn | head -10

# Check for memory issues
docker logs pra-app 2>&1 | grep -i "memory"

# Check for connection issues
docker logs pra-app 2>&1 | grep -i "connection"

# Check for timeout issues
docker logs pra-app 2>&1 | grep -i "timeout"
```

---

## Service Management

### List All Services

```bash
# List all services
sudo systemctl list-units --type=service

# List only active services
sudo systemctl list-units --type=service --state=active

# List only failed services
sudo systemctl list-units --type=service --state=failed
```

### Enable/Disable Services

```bash
# Enable service (start on boot)
sudo systemctl enable cloudflared-pra

# Disable service
sudo systemctl disable cloudflared-pra

# Check if enabled
sudo systemctl is-enabled cloudflared-pra
```

### Service Dependencies

```bash
# Check service dependencies
systemctl list-dependencies cloudflared-pra

# Show what would start/stop with service
systemctl show cloudflared-pra
```

---

## Emergency Fixes

### If Site is Down

```bash
# Quick diagnostic sequence
echo "=== 1. Check app container ==="
docker ps | grep pra-app

echo "=== 2. Check tunnel service ==="
sudo systemctl status cloudflared-pra

echo "=== 3. Test app locally ==="
curl -I http://localhost:5001/health

echo "=== 4. Check tunnel connection ==="
cloudflared tunnel list

echo "=== 5. Check DNS ==="
nslookup skincares.work

echo "=== 6. Test external access ==="
curl -I https://skincares.work
```

### Quick Restart Everything

```bash
# Restart all components
echo "Restarting app container..."
docker restart pra-app
sleep 5

echo "Restarting tunnel..."
sudo systemctl restart cloudflared-pra
sleep 3

echo "Checking status..."
docker ps | grep pra-app
sudo systemctl status cloudflared-pra
curl http://localhost:5001/health
```

### Nuclear Option (Full Reset)

```bash
# WARNING: This restarts everything

# 1. Stop services
sudo systemctl stop cloudflared-pra
docker stop pra-app

# 2. Wait
sleep 5

# 3. Start services
docker start pra-app
sleep 10
sudo systemctl start cloudflared-pra

# 4. Verify
docker logs pra-app --tail 30
sudo journalctl -u cloudflared-pra -n 30
curl http://localhost:5001/health
```

### Rollback to Previous Version

```bash
# Pull previous image version
docker pull ghcr.io/fablihamaliha/pra:<previous-sha>

# Stop current container
docker stop pra-app
docker rm pra-app

# Run previous version
docker run -d \
  --name pra-app \
  --restart unless-stopped \
  --network host \
  -e DATABASE_URL="postgresql://prra_user:prra_password_123@localhost:5432/prra_db" \
  -e SECRET_KEY="your-secret" \
  -e FLASK_ENV="production" \
  ghcr.io/fablihamaliha/pra:<previous-sha>
```

---

## Common Issues Quick Reference

### Issue: Tunnel won't start

```bash
# Check logs
sudo journalctl -u cloudflared-pra -n 50

# Verify config
cat ~/.cloudflared/config-pra.yml
cloudflared tunnel list

# Test manually
sudo systemctl stop cloudflared-pra
cloudflared tunnel --config ~/.cloudflared/config-pra.yml run pra-tunnel
```

### Issue: App container crashed

```bash
# Check why it stopped
docker ps -a | grep pra-app
docker logs pra-app --tail 100

# Restart it
docker restart pra-app

# If won't start, check database
docker exec pra-app env | grep DATABASE_URL
```

### Issue: Site loads but gets 502 error

```bash
# App is probably down
docker ps | grep pra-app
docker logs pra-app --tail 50

# Check if app is listening
curl http://localhost:5001/health

# Restart app
docker restart pra-app
```

### Issue: DNS not resolving

```bash
# Check DNS records in Cloudflare dashboard
# https://dash.cloudflare.com

# Test DNS
nslookup skincares.work
dig skincares.work

# Wait 5 minutes and try again (propagation time)
```

### Issue: Changes not deploying

```bash
# Check GitHub Actions
# https://github.com/fablihamaliha/PRA/actions

# Check if code was pushed
git log -1

# Manually pull and restart on Pi
cd /path/to/code
git pull origin master
docker restart pra-app
```

---

## Monitoring Commands (Run Regularly)

```bash
#!/bin/bash
# Save as: ~/check-pra-status.sh
# Run: bash ~/check-pra-status.sh

echo "==================================="
echo "PRA Status Check - $(date)"
echo "==================================="

echo ""
echo "1. Docker Container Status:"
docker ps | grep pra-app || echo "❌ Container not running"

echo ""
echo "2. Tunnel Service Status:"
sudo systemctl is-active cloudflared-pra || echo "❌ Tunnel not running"

echo ""
echo "3. App Health Check:"
curl -s http://localhost:5001/health || echo "❌ App not responding"

echo ""
echo "4. Tunnel Connections:"
cloudflared tunnel list | grep pra-tunnel

echo ""
echo "5. DNS Check:"
nslookup skincares.work | head -5

echo ""
echo "6. External Access:"
curl -Is https://skincares.work | head -1 || echo "❌ Site not accessible"

echo ""
echo "==================================="
echo "Check complete"
echo "==================================="
```

Make it executable:
```bash
chmod +x ~/check-pra-status.sh
```

Run it:
```bash
bash ~/check-pra-status.sh
```

---

## Getting Help

### Collect Debug Information

```bash
#!/bin/bash
# Save as: ~/collect-debug-info.sh

OUTPUT_FILE="/tmp/pra-debug-$(date +%Y%m%d_%H%M%S).txt"

echo "Collecting debug information..." | tee $OUTPUT_FILE
echo "======================================" | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "System Info:" | tee -a $OUTPUT_FILE
uname -a | tee -a $OUTPUT_FILE
whoami | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "Docker Status:" | tee -a $OUTPUT_FILE
docker ps -a | grep pra | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "App Logs (last 50):" | tee -a $OUTPUT_FILE
docker logs pra-app --tail 50 2>&1 | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "Tunnel Status:" | tee -a $OUTPUT_FILE
sudo systemctl status cloudflared-pra | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "Tunnel Logs (last 50):" | tee -a $OUTPUT_FILE
sudo journalctl -u cloudflared-pra -n 50 --no-pager | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "Tunnel List:" | tee -a $OUTPUT_FILE
cloudflared tunnel list | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "DNS Check:" | tee -a $OUTPUT_FILE
nslookup skincares.work | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "Local Health Check:" | tee -a $OUTPUT_FILE
curl -v http://localhost:5001/health 2>&1 | tee -a $OUTPUT_FILE

echo "" | tee -a $OUTPUT_FILE
echo "======================================" | tee -a $OUTPUT_FILE
echo "Debug info saved to: $OUTPUT_FILE"
```

Make executable and run:
```bash
chmod +x ~/collect-debug-info.sh
bash ~/collect-debug-info.sh
```

---

**Last Updated:** 2026-01-09

**Need More Help?**
- Check ERRORS_AND_SOLUTIONS.md for specific error fixes
- Check CLOUDFLARE_SETUP_INTERACTIVE.md for setup steps
- Run the monitoring script above to get current status
