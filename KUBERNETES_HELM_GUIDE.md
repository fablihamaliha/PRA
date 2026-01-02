## Kubernetes & Helm Deployment Guide

Complete guide for deploying PRA application to Kubernetes using Helm charts.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Helm Chart Overview](#helm-chart-overview)
3. [Quick Start](#quick-start)
4. [Deploy to Raspberry Pi (k3s)](#deploy-to-raspberry-pi-k3s)
5. [Configuration](#configuration)
6. [Production Setup](#production-setup)

---

## Prerequisites

### Install Kubectl

**Mac:**
```bash
brew install kubectl
```

**Verify:**
```bash
kubectl version --client
```

### Install Helm

**Mac:**
```bash
brew install helm
```

**Verify:**
```bash
helm version
```

---

## Helm Chart Overview

### Chart Structure

```
helm/pra/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration
└── templates/
    ├── deployment.yaml     # Pod deployment
    ├── service.yaml        # Service (load balancer)
    ├── ingress.yaml        # External access
    ├── secrets.yaml        # Sensitive data
    ├── serviceaccount.yaml # Service account
    ├── pvc.yaml            # Persistent storage
    └── _helpers.tpl        # Template helpers
```

### What's Included

- ✅ **Deployment** - Runs 2 replicas (high availability)
- ✅ **Service** - Load balances traffic
- ✅ **Ingress** - HTTPS with cert-manager
- ✅ **Secrets** - Secure API keys and passwords
- ✅ **PVC** - Persistent storage for logs
- ✅ **Health checks** - Liveness and readiness probes
- ✅ **Resource limits** - CPU and memory management
- ✅ **Auto-scaling** - Optional HPA support

---

## Quick Start

### Step 1: Install k3s on Raspberry Pi

```bash
# SSH to Raspberry Pi
ssh pi@YOUR_PI_IP

# Install k3s (lightweight Kubernetes)
curl -sfL https://get.k3s.io | sh -

# Verify installation
sudo k3s kubectl get nodes
# Should show: Ready
```

### Step 2: Get kubeconfig

```bash
# On Raspberry Pi
sudo cat /etc/rancher/k3s/k3s.yaml

# On your Mac
mkdir -p ~/.kube
# Copy the content to ~/.kube/config
# Replace 127.0.0.1 with YOUR_PI_IP
```

### Step 3: Verify Connection

```bash
# On your Mac
kubectl get nodes

# Should show your Raspberry Pi
```

### Step 4: Set Up PostgreSQL

```bash
# SSH to Raspberry Pi
ssh pi@YOUR_PI_IP

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start and enable
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql << EOF
CREATE DATABASE prra_db;
CREATE USER prra_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE prra_db TO prra_user;
\q
EOF

# Allow network access
sudo nano /etc/postgresql/15/main/postgresql.conf
# Change: listen_addresses = '*'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add: host all all 0.0.0.0/0 md5

# Restart
sudo systemctl restart postgresql
```

### Step 5: Deploy with Helm

```bash
# On your Mac
cd /Users/maliha/PycharmProjects/PRA

# Install the Helm chart
helm install pra ./helm/pra \
  --set secrets.secretKey="$(openssl rand -hex 32)" \
  --set secrets.dbPassword="your_secure_password" \
  --set database.host="YOUR_PI_IP" \
  --set secrets.rapidapiKey="your-rapidapi-key" \
  --set secrets.openaiApiKey="your-openai-key" \
  --set image.repository="ghcr.io/fablihamaliha/pra" \
  --set image.tag="v1.0.0" \
  --namespace pra \
  --create-namespace
```

### Step 6: Verify Deployment

```bash
# Check pods
kubectl get pods -n pra

# Should show:
# NAME                   READY   STATUS    RESTARTS   AGE
# pra-xxxxx              1/1     Running   0          1m
# pra-yyyyy              1/1     Running   0          1m

# Check service
kubectl get svc -n pra

# Check logs
kubectl logs -n pra deployment/pra
```

### Step 7: Access Your App

```bash
# Get service details
kubectl get svc -n pra

# If using NodePort:
# http://YOUR_PI_IP:30080

# Port forward for testing
kubectl port-forward -n pra svc/pra 8080:80

# Access at: http://localhost:8080
```

---

## Deploy to Raspberry Pi (k3s)

### Complete Setup from Scratch

**1. Prepare Raspberry Pi**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install k3s
curl -sfL https://get.k3s.io | sh -

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
```

**2. Configure Database**

```bash
# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE prra_db;
CREATE USER prra_user WITH PASSWORD 'changeme123';
GRANT ALL PRIVILEGES ON DATABASE prra_db TO prra_user;
\q
```

```bash
# Enable network access
echo "listen_addresses = '*'" | sudo tee -a /etc/postgresql/15/main/postgresql.conf
echo "host all all 0.0.0.0/0 md5" | sudo tee -a /etc/postgresql/15/main/pg_hba.conf
sudo systemctl restart postgresql
```

**3. Set Up kubectl Access (from your Mac)**

```bash
# Get k3s config from Pi
ssh pi@YOUR_PI_IP "sudo cat /etc/rancher/k3s/k3s.yaml" > ~/.kube/config-pi

# Edit config to replace 127.0.0.1 with Pi IP
sed -i '' 's/127.0.0.1/YOUR_PI_IP/g' ~/.kube/config-pi

# Use this config
export KUBECONFIG=~/.kube/config-pi

# Or merge with existing config
KUBECONFIG=~/.kube/config:~/.kube/config-pi kubectl config view --flatten > ~/.kube/config.new
mv ~/.kube/config.new ~/.kube/config
```

**4. Deploy Application**

```bash
# Create values file with your config
cat > my-values.yaml << EOF
replicaCount: 2

image:
  repository: ghcr.io/fablihamaliha/pra
  tag: v1.0.0

database:
  host: YOUR_PI_IP
  name: prra_db
  user: prra_user

secrets:
  secretKey: "$(openssl rand -hex 32)"
  dbPassword: "changeme123"
  rapidapiKey: "your-rapidapi-key"
  openaiApiKey: "your-openai-key"

ingress:
  enabled: false  # Disable for Raspberry Pi

service:
  type: NodePort  # Expose via node port
EOF

# Install
helm install pra ./helm/pra \
  -f my-values.yaml \
  --namespace pra \
  --create-namespace

# Wait for pods
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=pra -n pra --timeout=300s
```

**5. Access Application**

```bash
# Get NodePort
kubectl get svc pra -n pra

# Output example:
# PORT(S): 80:30123/TCP
# Access at: http://YOUR_PI_IP:30123
```

---

## Configuration

### values.yaml Customization

**Minimal Configuration:**

```yaml
image:
  repository: ghcr.io/fablihamaliha/pra
  tag: v1.0.0

database:
  host: YOUR_DB_HOST
  name: prra_db
  user: prra_user

secrets:
  secretKey: your-secret-key
  dbPassword: your-db-password
```

**Production Configuration:**

```yaml
replicaCount: 3

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: pra.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: pra-tls
      hosts:
        - pra.yourdomain.com
```

### Environment Variables

Set via `values.yaml`:

```yaml
app:
  flaskEnv: production
  flaskDebug: false
  logLevel: INFO
  maxRecommendations: 3
  minProductRating: 3.5
```

### Secrets Management

**Option 1: Via Helm values (Quick)**

```bash
helm install pra ./helm/pra \
  --set secrets.secretKey="$(openssl rand -hex 32)" \
  --set secrets.dbPassword="mypassword"
```

**Option 2: External Secrets (Production)**

Use [External Secrets Operator](https://external-secrets.io/):

```yaml
# Install external-secrets
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace

# Create secret store (e.g., AWS Secrets Manager, Vault)
# Then reference in values.yaml
```

---

## Production Setup

### 1. Install Ingress Controller

```bash
# Install Nginx Ingress
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

### 2. Install Cert-Manager (HTTPS)

```bash
# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true

# Create Let's Encrypt issuer
kubectl apply -f - << EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 3. Set Up Monitoring

```bash
# Install Prometheus & Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Open: http://localhost:3000
# User: admin, Password: prom-operator
```

### 4. Database Backups

```bash
# Create backup CronJob
kubectl apply -f - << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: pra
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h YOUR_DB_HOST -U prra_user prra_db > /backup/prra_db_\$(date +%Y%m%d_%H%M%S).sql
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: pra-secrets
                  key: database-url
            volumeMounts:
            - name: backup
              mountPath: /backup
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: postgres-backup-pvc
          restartPolicy: OnFailure
EOF
```

---

## Upgrade & Rollback

### Upgrade Application

```bash
# Pull new image version
docker pull ghcr.io/fablihamaliha/pra:v1.1.0

# Upgrade Helm release
helm upgrade pra ./helm/pra \
  --set image.tag=v1.1.0 \
  --namespace pra

# Or upgrade from values file
helm upgrade pra ./helm/pra \
  -f my-values.yaml \
  --namespace pra
```

### Rollback

```bash
# View history
helm history pra -n pra

# Rollback to previous version
helm rollback pra -n pra

# Rollback to specific revision
helm rollback pra 1 -n pra
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod pra-xxxxx -n pra

# Check logs
kubectl logs pra-xxxxx -n pra

# Common issues:
# - Image pull error → Check image exists
# - CrashLoopBackOff → Check environment variables
# - Database connection → Check DB is accessible
```

### Database Connection Issues

```bash
# Test from pod
kubectl exec -it pra-xxxxx -n pra -- /bin/bash
apt-get update && apt-get install -y postgresql-client
psql -h YOUR_DB_HOST -U prra_user -d prra_db
```

### Can't Access Application

```bash
# Check service
kubectl get svc -n pra

# Check ingress
kubectl get ingress -n pra
kubectl describe ingress pra -n pra

# Port forward for debugging
kubectl port-forward -n pra svc/pra 8080:80
```

---

## Useful Commands

```bash
# View all resources
kubectl get all -n pra

# Watch pod status
kubectl get pods -n pra -w

# View logs (all pods)
kubectl logs -n pra -l app.kubernetes.io/name=pra --tail=100 -f

# Exec into pod
kubectl exec -it -n pra deployment/pra -- /bin/bash

# Scale deployment
kubectl scale deployment pra -n pra --replicas=5

# Delete everything
helm uninstall pra -n pra
kubectl delete namespace pra
```

---

## Cost & Performance

### Raspberry Pi Resources

**Recommended:**
- Raspberry Pi 4 (4GB RAM minimum, 8GB preferred)
- 32GB+ SD card
- Stable power supply
- Ethernet connection

**Limits:**
- Can run 2-3 replicas comfortably
- Suitable for 50-100 concurrent users
- Database on same Pi or separate server

### Scaling

**Horizontal (More Pods):**
```bash
kubectl scale deployment pra -n pra --replicas=3
```

**Vertical (More Resources):**
Edit values.yaml:
```yaml
resources:
  limits:
    cpu: 2000m
    memory: 2Gi
```

---

## Next Steps

1. ✅ **Deploy to k3s** on Raspberry Pi
2. ✅ **Set up monitoring** with Prometheus
3. ✅ **Configure backups** for database
4. ✅ **Add HTTPS** with cert-manager
5. ✅ **Set up CI/CD** to auto-deploy

---

**You now have production-grade Kubernetes deployment! 🚀**
