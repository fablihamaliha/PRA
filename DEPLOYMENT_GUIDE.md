# Complete Deployment Guide - Beginner Friendly

This guide will help you deploy your PRA application step-by-step, even if you've never used Docker, Kubernetes, or CI/CD before.

## Table of Contents
1. [Prerequisites & Setup](#prerequisites--setup)
2. [Part 1: Docker - Containerizing Your App](#part-1-docker---containerizing-your-app)
3. [Part 2: Git & CI/CD Pipeline](#part-2-git--cicd-pipeline)
4. [Part 3: Kubernetes & Helm](#part-3-kubernetes--helm)
5. [Part 4: Deploy to Raspberry Pi](#part-4-deploy-to-raspberry-pi)
6. [Part 5: Complete Deployment](#part-5-complete-deployment)

---

## Prerequisites & Setup

### What You'll Need

1. **A Raspberry Pi** (Model 4 with at least 4GB RAM recommended)
2. **A computer** (Mac/Windows/Linux) for development
3. **Basic command line knowledge** (we'll guide you through everything)
4. **Your PRA application** (you already have this!)

### Install Required Software on Your Computer

#### 1. Install Docker Desktop

**What is Docker?** Think of Docker as a way to package your entire application (code, dependencies, environment) into a container that runs the same everywhere.

**Mac:**
```bash
# Download Docker Desktop from:
# https://www.docker.com/products/docker-desktop

# Or install via Homebrew:
brew install --cask docker
```

**Windows:**
- Download from: https://www.docker.com/products/docker-desktop
- Run the installer
- Restart your computer

**Verify Installation:**
```bash
docker --version
# Should show: Docker version 24.x.x or higher
```

#### 2. Install kubectl (Kubernetes CLI)

**What is kubectl?** It's a command-line tool to control Kubernetes clusters (groups of servers running your apps).

**Mac:**
```bash
brew install kubectl
```

**Windows:**
```powershell
# Using Chocolatey package manager:
choco install kubernetes-cli
```

**Verify:**
```bash
kubectl version --client
```

#### 3. Install Helm

**What is Helm?** Think of it as a package manager for Kubernetes - like npm for Node.js or pip for Python.

**Mac:**
```bash
brew install helm
```

**Windows:**
```powershell
choco install kubernetes-helm
```

**Verify:**
```bash
helm version
```

#### 4. Install k3s (Lightweight Kubernetes)

**What is k3s?** A lightweight version of Kubernetes perfect for Raspberry Pi - it uses less memory and resources.

We'll install this on your Raspberry Pi later!

---

## Part 1: Docker - Containerizing Your App

### Step 1.1: Create a Dockerfile

A Dockerfile is like a recipe that tells Docker how to build your application container.

Create this file in your project root:

```bash
cd /Users/maliha/PycharmProjects/PRA
```

I'll create the Dockerfile for you in the next step.

### Step 1.2: Create Docker Compose File

Docker Compose lets you define and run multi-container applications (your app + database).

### Step 1.3: Build and Test Locally

```bash
# Build your Docker image
docker build -t pra-app:latest .

# Run it locally to test
docker-compose up

# Your app should be available at http://localhost:5001
```

**What's happening?**
- `docker build` creates a container image with your app
- `docker-compose up` starts your app and PostgreSQL database
- Everything runs in isolated containers

---

## Part 2: Git & CI/CD Pipeline

### Step 2.1: Initialize Git Repository (if not done)

```bash
cd /Users/maliha/PycharmProjects/PRA

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: PRA application with GPT integration"
```

### Step 2.2: Create GitHub Repository

1. Go to https://github.com
2. Click the "+" button → "New repository"
3. Name it: `PRA`
4. Don't initialize with README (you already have code)
5. Click "Create repository"

### Step 2.3: Push Your Code to GitHub

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/PRA.git

# Push your code
git branch -M master
git push -u origin master
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

### Step 2.4: Set Up GitHub Actions (CI/CD)

**What is CI/CD?**
- **CI (Continuous Integration)**: Automatically test your code when you push changes
- **CD (Continuous Deployment)**: Automatically deploy your code when tests pass

I'll create the GitHub Actions workflow in the next step.

---

## Part 3: Kubernetes & Helm

### Step 3.1: Understanding Kubernetes Concepts

**Key Concepts (explained simply):**

1. **Pod**: The smallest unit - a container running your app
2. **Deployment**: Manages multiple pods, ensures they stay running
3. **Service**: Exposes your pods to the network so users can access them
4. **ConfigMap**: Stores configuration (like environment variables)
5. **Secret**: Stores sensitive data (like API keys, passwords)
6. **Ingress**: Routes external traffic to your services (like a reverse proxy)

### Step 3.2: Create Helm Chart

**What's a Helm Chart?** A collection of files that describe a Kubernetes application.

I'll create the Helm chart structure in the next step.

### Step 3.3: Helm Chart Structure

```
helm/
├── Chart.yaml          # Metadata about your chart
├── values.yaml         # Default configuration values
└── templates/          # Kubernetes resource templates
    ├── deployment.yaml # How to run your app
    ├── service.yaml    # How to expose your app
    ├── ingress.yaml    # How to route traffic
    ├── configmap.yaml  # Non-sensitive config
    └── secrets.yaml    # Sensitive data
```

---

## Part 4: Deploy to Raspberry Pi

### Step 4.1: Set Up Your Raspberry Pi

**Initial Setup:**

1. **Flash Raspberry Pi OS:**
   - Download Raspberry Pi Imager: https://www.raspberrypi.com/software/
   - Flash "Raspberry Pi OS Lite (64-bit)" to SD card
   - Enable SSH in settings before flashing

2. **Boot and Connect:**
   ```bash
   # Find your Pi's IP address (from your router or use)
   ping raspberrypi.local

   # SSH into your Pi
   ssh pi@raspberrypi.local
   # Default password: raspberry
   ```

3. **Update System:**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

### Step 4.2: Install k3s on Raspberry Pi

**What is k3s?** A lightweight Kubernetes distribution perfect for Raspberry Pi.

```bash
# SSH into your Raspberry Pi
ssh pi@raspberrypi.local

# Install k3s (this takes 5-10 minutes)
curl -sfL https://get.k3s.io | sh -

# Verify installation
sudo k3s kubectl get nodes

# You should see your Raspberry Pi listed as a node
```

**Get the kubeconfig file to control from your computer:**

```bash
# On Raspberry Pi, copy the config
sudo cat /etc/rancher/k3s/k3s.yaml

# On your Mac, create the config
mkdir -p ~/.kube
# Paste the content into ~/.kube/config
# Replace 127.0.0.1 with your Raspberry Pi's IP address
```

### Step 4.3: Install PostgreSQL on Raspberry Pi

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE DATABASE prra_db;
CREATE USER prra_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE prra_db TO prra_user;
\q
```

### Step 4.4: Configure PostgreSQL for Network Access

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/15/main/postgresql.conf

# Find this line and change it to:
listen_addresses = '*'

# Edit access control
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Add this line at the end:
host    all             all             0.0.0.0/0               md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## Part 5: Complete Deployment

### Step 5.1: Build and Push Docker Image

**Option A: Use Docker Hub (Recommended for beginners)**

```bash
# Login to Docker Hub
docker login
# Enter your username and password

# Tag your image
docker tag pra-app:latest YOUR_DOCKERHUB_USERNAME/pra-app:latest

# Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/pra-app:latest
```

**Option B: Use GitHub Container Registry (Free)**

```bash
# Create GitHub Personal Access Token:
# 1. Go to GitHub → Settings → Developer settings → Personal access tokens
# 2. Generate new token with 'write:packages' permission
# 3. Copy the token

# Login
echo YOUR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Tag image
docker tag pra-app:latest ghcr.io/YOUR_USERNAME/pra-app:latest

# Push
docker push ghcr.io/YOUR_USERNAME/pra-app:latest
```

### Step 5.2: Configure Helm Values

Edit `helm/pra/values.yaml` with your specific values:

```yaml
image:
  repository: YOUR_DOCKERHUB_USERNAME/pra-app  # or ghcr.io/YOUR_USERNAME/pra-app
  tag: latest

database:
  host: YOUR_RASPBERRY_PI_IP  # e.g., 192.168.1.100
  port: 5432
  name: prra_db
  user: prra_user
  password: your_secure_password

secrets:
  rapidapiKey: "your-rapidapi-key"
  openaiKey: "your-openai-api-key"
  secretKey: "your-flask-secret-key"
```

### Step 5.3: Deploy with Helm

```bash
# Make sure kubectl is connected to your Raspberry Pi
kubectl get nodes
# Should show your Raspberry Pi

# Create namespace
kubectl create namespace pra

# Deploy using Helm
helm install pra ./helm/pra -n pra

# Watch the deployment
kubectl get pods -n pra -w
# Press Ctrl+C to stop watching
```

### Step 5.4: Access Your Application

```bash
# Get the service details
kubectl get svc -n pra

# If using NodePort, access at:
# http://RASPBERRY_PI_IP:30080

# If using LoadBalancer (with MetalLB), access at the external IP shown
```

### Step 5.5: Set Up Port Forwarding (Optional)

If you want to access from outside your network:

```bash
# On your router, forward port 80 to your Raspberry Pi's port 30080
# Instructions vary by router - Google "port forwarding [YOUR_ROUTER_MODEL]"
```

---

## Verification & Testing

### Check Everything is Running

```bash
# 1. Check pods are running
kubectl get pods -n pra
# All should show STATUS: Running

# 2. Check services
kubectl get svc -n pra

# 3. Check logs
kubectl logs -n pra deployment/pra-app

# 4. Access the app
# Open browser: http://RASPBERRY_PI_IP:30080
```

### Test the Application

1. **Sign up for an account**
2. **Fill out skincare preferences**
3. **Search for products** (e.g., "moisturizer")
4. **Get personalized recommendations**

---

## Troubleshooting

### Pod Won't Start

```bash
# Check pod details
kubectl describe pod POD_NAME -n pra

# Check logs
kubectl logs POD_NAME -n pra

# Common issues:
# 1. Image pull error → Check Docker Hub credentials
# 2. CrashLoopBackOff → Check environment variables
# 3. Database connection error → Check PostgreSQL is running
```

### Database Connection Issues

```bash
# Test PostgreSQL from Raspberry Pi
psql -h localhost -U prra_user -d prra_db
# Should connect successfully

# Test from another machine
psql -h RASPBERRY_PI_IP -U prra_user -d prra_db
# Should connect if network access is configured
```

### Application Not Accessible

```bash
# Check service
kubectl get svc pra-app -n pra

# Check if port is open
sudo netstat -tuln | grep 30080

# Check firewall (if enabled)
sudo ufw allow 30080
```

---

## Next Steps

### Monitoring & Maintenance

1. **Set up monitoring** with Prometheus & Grafana
2. **Enable automatic backups** for PostgreSQL
3. **Configure SSL/TLS** with Let's Encrypt
4. **Set up log aggregation** with Loki

### Scaling

```bash
# Scale your application
kubectl scale deployment pra-app --replicas=3 -n pra

# Your app now runs 3 copies for better performance!
```

### Updates & Rollbacks

```bash
# Update your app
docker build -t pra-app:v2 .
docker push YOUR_DOCKERHUB_USERNAME/pra-app:v2
helm upgrade pra ./helm/pra -n pra --set image.tag=v2

# Rollback if something goes wrong
helm rollback pra -n pra
```

---

## Cost Breakdown

**Total Setup Cost: ~$100-150**

- Raspberry Pi 4 (4GB): $55
- SD Card (64GB): $15
- Power Supply: $10
- Case: $10
- (Optional) Cooling fan: $10

**Monthly Costs: ~$5-10**

- Electricity for Raspberry Pi: ~$2-3/month
- OpenAI API (GPT): ~$5/month (for moderate usage)
- Domain name (optional): ~$10-15/year

**Free Services:**
- GitHub (code hosting & CI/CD)
- Docker Hub or GitHub Container Registry (image hosting)
- RapidAPI (100 requests/month free)

---

## Resources & Learning

### Beginner-Friendly Tutorials

1. **Docker**: https://docs.docker.com/get-started/
2. **Kubernetes**: https://kubernetes.io/docs/tutorials/kubernetes-basics/
3. **Helm**: https://helm.sh/docs/intro/quickstart/
4. **k3s**: https://k3s.io/

### Community Support

- Docker Community: https://forums.docker.com/
- Kubernetes Slack: https://kubernetes.slack.com/
- Raspberry Pi Forums: https://forums.raspberrypi.com/

---

**Congratulations!** You now have a production-ready application running on Kubernetes with CI/CD! 🎉
