# PRA - Product Recommendation Application

A full-stack skincare product recommendation and deal-finding application built with Flask, PostgreSQL, and OpenAI GPT integration. Deployed on Raspberry Pi with complete CI/CD automation using GitHub Actions.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Local Development Setup](#local-development-setup)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [Public Access](#public-access)
- [Contributing](#contributing)

---

## 🎯 Overview

PRA (Product Recommendation Application) is an intelligent skincare recommendation system that:
- Analyzes user skin profiles to provide personalized product recommendations
- Finds the best deals across multiple retailers using real-time APIs
- Uses OpenAI GPT for intelligent product analysis and recommendations
- Provides a responsive web interface for users to manage their skincare routines

**Live Application:** https://skincares.work

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐
│   Client (Web)  │
│  Browser/Mobile │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ngrok Tunnel  │ ◄── Public HTTPS access
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Raspberry Pi   │
│  (ARM64 Linux)  │
├─────────────────┤
│  Docker: Flask  │ ◄── Port 5001
│  + Gunicorn     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │ ◄── Port 5432
│  Database (DB)  │
└─────────────────┘
```

### CI/CD Pipeline Flow

```
Developer pushes to master
         │
         ▼
┌─────────────────────────────────┐
│  GitHub Actions: CI Workflow    │
│  (Runs on GitHub Hosted Runner) │
├─────────────────────────────────┤
│  1. Run tests                   │
│  2. Check code quality          │
│  3. Build ARM64 Docker image    │
│  4. Push to ghcr.io             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  GitHub Actions: CD Workflow    │
│  (Runs on Raspberry Pi Runner)  │
├─────────────────────────────────┤
│  1. Wait for Docker image       │
│  2. Pull latest image           │
│  3. Run migrations              │
│  4. Stop old container          │
│  5. Start new container         │
│  6. Health check                │
└─────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **Flask 3.0.0** - Web framework
- **SQLAlchemy 2.0.23** - ORM for database interactions
- **PostgreSQL 16** - Primary database
- **Flask-Login** - User authentication and session management
- **OpenAI API** - GPT-4 integration for intelligent recommendations

### Security & Monitoring
- **Advanced Security Middleware** - Threat detection and prevention
- **Email Notification Service** - SMTP-based alerting system
- **Real-time Analytics** - Visitor tracking and monitoring
- **Rate Limiting** - DDoS protection
- **User Agent Parsing** - Device and browser detection

### External APIs
- **RapidAPI** - Real-time product search
- **Google Custom Search API** - Product discovery
- **Walmart/Amazon/Target APIs** - Deal aggregation

### Infrastructure
- **Docker** - Containerization
- **GitHub Actions** - CI/CD automation
- **GitHub Container Registry (ghcr.io)** - Docker image hosting
- **Cloudflare** - Custom domain, CDN, DDoS protection, SSL/TLS
- **Cloudflare Tunnel** - Secure public HTTPS access
- **Raspberry Pi** - Self-hosted deployment target

### Development Tools
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Linting
- **python-dotenv** - Environment variable management

---

## ✨ Features

### User Features
1. **Authentication System**
   - User registration and login
   - Password hashing with bcrypt
   - Session management with Flask-Login
   - Remember me functionality

2. **Skin Profile Management**
   - Create detailed skin profiles (type, concerns, goals)
   - Update profiles based on changing needs
   - Track skin journey over time

3. **Product Recommendations**
   - AI-powered recommendations using GPT-4
   - Personalized based on skin profile
   - Multi-factor scoring algorithm
   - Real-time product analysis

4. **Deal Finder**
   - Search across multiple retailers
   - Price comparison
   - Real-time availability checking
   - Deal aggregation and ranking

### Technical Features
1. **Automated Deployment**
   - Push to master triggers full CI/CD
   - Automatic image building and pushing
   - Zero-downtime deployments
   - Health checks and rollback capability

2. **Security & Monitoring**
   - HTTPS via Cloudflare (with free SSL/TLS)
   - Custom domain with Cloudflare CDN
   - Secure password hashing
   - HTTP-only cookies
   - Environment-based secrets management
   - Enterprise-grade security monitoring
   - Real-time threat detection and prevention
   - Rate limiting and IP blocking
   - Email notifications for critical issues

3. **Admin Dashboard**
   - Real-time application insights
   - Visitor analytics and tracking
   - Security event monitoring
   - System health monitoring
   - Email alerts for critical events (Dynatrace-style)

4. **Scalability**
   - Containerized architecture
   - Database connection pooling
   - Prepared for horizontal scaling

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Docker (optional for container testing)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/fablihamaliha/PRA.git
cd PRA
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Up PostgreSQL Database
```bash
# Create database and user
psql postgres
CREATE DATABASE prra_db;
CREATE USER prra_user WITH PASSWORD 'prra_password_123';
GRANT ALL PRIVILEGES ON DATABASE prra_db TO prra_user;
\q
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database
DATABASE_URL=postgresql://prra_user:prra_password_123@localhost:5432/prra_db

# API Keys
RAPIDAPI_KEY=your-rapidapi-key
OPENAI_API_KEY=your-openai-api-key

# Optional API Keys
GOOGLE_API_KEY=
GOOGLE_CUSTOM_SEARCH_CX=
WALMART_API_KEY=
BEST_BUY_API_KEY=
```

### Step 5: Initialize Database
```bash
# Run the application (this creates tables)
python -m pra.app

# Or use Flask CLI
flask --app pra.app run
```

### Step 6: Run the Application
```bash
python -m pra.app
```

Access the application at:
- Main app: http://localhost:5001
- Auth page: http://localhost:5001/auth
- Deals finder: http://localhost:5001/deals
- Health check: http://localhost:5001/health

---

## 📁 Project Structure

```
PRA/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # CI pipeline (build & test)
│       └── deploy-pi.yml          # CD pipeline (deploy to Pi)
│
├── pra/                           # Main application package
│   ├── __init__.py
│   ├── app.py                     # Flask app factory
│   ├── config.py                  # Configuration classes
│   │
│   ├── blueprints/                # Route blueprints
│   │   ├── __init__.py
│   │   ├── skincare.py            # Skincare recommendation routes
│   │   └── deals.py               # Deal finder routes
│   │
│   ├── models/                    # Database models
│   │   ├── __init__.py
│   │   ├── db.py                  # SQLAlchemy setup
│   │   ├── user.py                # User model
│   │   ├── skin_profile.py        # Skin profile model
│   │   ├── product.py             # Product model
│   │   └── recommendation.py      # Recommendation model
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── gpt_service.py         # OpenAI GPT integration
│   │   ├── recommender.py         # Recommendation engine
│   │   ├── deal_finder_service.py # Deal aggregation
│   │   ├── external_api.py        # External API clients
│   │   ├── scoring.py             # Product scoring algorithm
│   │   └── selenium_automation.py # Web scraping (optional)
│   │
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py          # Input validation
│   │   └── helper.py              # Helper functions
│   │
│   ├── static/                    # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   └── templates/                 # HTML templates
│       ├── index.html
│       ├── auth.html
│       └── ...
│
├── Dockerfile                     # Docker image configuration
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (local)
├── .gitignore
└── README.md
```

---

## 🗄️ Database Schema

### User Table
```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Skin Profile Table
```sql
CREATE TABLE skin_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user(id) ON DELETE CASCADE,
    skin_type VARCHAR(50),         -- oily, dry, combination, sensitive
    concerns TEXT[],                -- acne, aging, hyperpigmentation, etc.
    goals TEXT[],                   -- hydration, anti-aging, brightening, etc.
    allergies TEXT[],
    budget_range VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Product Table
```sql
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10, 2),
    rating DECIMAL(3, 2),
    ingredients TEXT[],
    product_url TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Recommendation Table
```sql
CREATE TABLE recommendation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
    score DECIMAL(5, 2),            -- Calculated recommendation score
    reason TEXT,                     -- Why this was recommended
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📡 API Documentation

### Authentication Endpoints

#### POST /login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful!",
  "redirect": "/deals",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

#### POST /signup
Create a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "password123"
}
```

#### POST /logout
Logout current user (requires authentication).

#### GET /current-user
Get current authenticated user info.

---

### Skincare Endpoints

#### POST /skincare/profile
Create or update skin profile (requires authentication).

**Request:**
```json
{
  "skin_type": "combination",
  "concerns": ["acne", "hyperpigmentation"],
  "goals": ["clear_skin", "even_tone"],
  "allergies": ["fragrance"],
  "budget_range": "medium"
}
```

#### GET /skincare/recommendations
Get personalized product recommendations (requires authentication).

**Query Parameters:**
- `limit` (optional): Number of recommendations (default: 3)

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "product": {
        "name": "CeraVe Hydrating Cleanser",
        "brand": "CeraVe",
        "price": 14.99,
        "rating": 4.7
      },
      "score": 9.2,
      "reason": "Perfect for combination skin with gentle hydrating formula"
    }
  ]
}
```

---

### Deals Endpoints

#### GET /deals/search
Search for product deals across retailers.

**Query Parameters:**
- `q`: Search query (required)
- `max_results`: Maximum results (default: 10)

**Response:**
```json
{
  "success": true,
  "query": "cerave cleanser",
  "results": [
    {
      "title": "CeraVe Hydrating Facial Cleanser",
      "price": "$14.99",
      "rating": 4.7,
      "link": "https://...",
      "source": "Amazon"
    }
  ]
}
```

---

## 🔄 CI/CD Pipeline

### Continuous Integration (CI)

**File:** [.github/workflows/ci.yml](.github/workflows/ci.yml)

**Triggers:**
- Push to `master`, `main`, or `develop` branches
- Pull requests to `master` or `main`

**Jobs:**

1. **Test Job** (runs on Ubuntu)
   - Sets up Python 3.12
   - Spins up PostgreSQL test database
   - Installs dependencies
   - Runs tests (when available)
   - Checks code quality with black and flake8

2. **Build Job** (runs on Ubuntu, after tests pass)
   - Builds ARM64 Docker image for Raspberry Pi
   - Pushes to GitHub Container Registry (ghcr.io)
   - Tags: `latest` and `<commit-sha>`
   - Uses build caching for faster builds

3. **Security Job** (runs on Ubuntu, parallel)
   - Scans code with Trivy for vulnerabilities
   - Reports CRITICAL and HIGH severity issues

### Continuous Deployment (CD)

**File:** [.github/workflows/deploy-pi.yml](.github/workflows/deploy-pi.yml)

**Triggers:**
- Push to `master` branch (runs after CI completes)
- Manual trigger via `workflow_dispatch`

**Jobs:**

1. **Deploy Job** (runs on self-hosted Raspberry Pi runner)
   - Logs into GitHub Container Registry
   - Waits for Docker image with current commit SHA
   - Stops existing container
   - Pulls latest image
   - Runs database migrations
   - Starts new container with production environment variables
   - Performs health check
   - Shows logs and cleans up old images

**Key Features:**
- Zero-downtime deployments
- Automatic rollback on health check failure
- Migration support
- Image cleanup to save disk space

---

## 🚢 Deployment

### Raspberry Pi Setup

#### 1. Install PostgreSQL
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql

CREATE DATABASE prra_db;
CREATE USER prra_user WITH PASSWORD 'prra_password_123';
GRANT ALL PRIVILEGES ON DATABASE prra_db TO prra_user;
\q
```

#### 2. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 3. Set Up GitHub Actions Runner
```bash
# Create runner directory
mkdir ~/actions-runner && cd ~/actions-runner

# Download runner (ARM64)
curl -o actions-runner-linux-arm64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-arm64-2.311.0.tar.gz

# Extract
tar xzf actions-runner-linux-arm64-2.311.0.tar.gz

# Configure (get token from GitHub repo settings > Actions > Runners)
./config.sh --url https://github.com/fablihamaliha/PRA --token YOUR_TOKEN

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
```

#### 4. Set Up GitHub Secrets
In GitHub repo settings > Secrets and variables > Actions, add:
- `SECRET_KEY`: Flask secret key
- `RAPIDAPI_KEY`: RapidAPI key
- `OPENAI_API_KEY`: OpenAI API key

#### 5. Deploy
Simply push to master:
```bash
git add .
git commit -m "Your changes"
git push origin master
```

The CI/CD pipeline will automatically:
1. Build the Docker image
2. Push to ghcr.io
3. Deploy to Raspberry Pi
4. Restart the application

---

## 🌐 Public Access

### ngrok Setup

#### 1. Install ngrok
```bash
# Download and install
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Or download directly
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz
sudo tar -xvzf ngrok-v3-stable-linux-arm64.tgz -C /usr/local/bin
```

#### 2. Configure ngrok
```bash
# Add auth token (get from https://dashboard.ngrok.com)
ngrok config add-authtoken YOUR_TOKEN
```

#### 3. Set Up as System Service
Create `/etc/systemd/system/ngrok.service`:
```ini
[Unit]
Description=ngrok tunnel
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
ExecStart=/usr/local/bin/ngrok http 5001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ngrok
sudo systemctl start ngrok
sudo systemctl status ngrok
```

#### 4. Get Your Public URL
```bash
curl http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
```

Your app is now publicly accessible at the ngrok URL!

---

## 🤝 Contributing

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test locally**
   ```bash
   python -m pra.app
   ```

3. **Format code**
   ```bash
   black pra/
   flake8 pra/
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

6. **Merge to master** triggers automatic deployment

### Code Style
- Use **black** for formatting (line length: 88)
- Follow **PEP 8** guidelines
- Write descriptive commit messages
- Add docstrings to functions and classes

### Testing
```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pra --cov-report=html
```

---

## 📝 Environment Variables Reference

### Core Configuration
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | Yes | localhost |
| `FLASK_ENV` | Environment (development/production) | No | development |
| `FLASK_DEBUG` | Enable debug mode | No | False |

### API Keys
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `RAPIDAPI_KEY` | RapidAPI key for product search | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key for GPT | Yes | - |
| `GOOGLE_API_KEY` | Google Custom Search API key | No | - |
| `WALMART_API_KEY` | Walmart API key | No | - |
| `BEST_BUY_API_KEY` | Best Buy API key | No | - |

### Email Notifications (Optional)
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `EMAIL_NOTIFICATIONS_ENABLED` | Enable email alerts | No | false |
| `SMTP_SERVER` | SMTP server hostname | No | smtp.gmail.com |
| `SMTP_PORT` | SMTP server port | No | 587 |
| `SMTP_USERNAME` | SMTP login username | No | - |
| `SMTP_PASSWORD` | SMTP login password | No | - |
| `ADMIN_EMAIL` | Admin email for alerts | No | admin@example.com |
| `FROM_EMAIL` | Sender email address | No | SMTP_USERNAME |

**Note:** For Gmail, use [App Passwords](https://support.google.com/accounts/answer/185833) instead of your regular password.

---

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U prra_user -d prra_db -h localhost
```

### Docker Issues
```bash
# Check container logs
docker logs pra-app

# Restart container
docker restart pra-app

# Check container status
docker ps -a
```

### GitHub Actions Runner Issues
```bash
# Check runner status
sudo systemctl status actions.runner.fablihamaliha-PRA.Malsi123.service

# View logs
journalctl -u actions.runner.fablihamaliha-PRA.Malsi123.service -f

# Restart runner
sudo ./svc.sh stop
sudo ./svc.sh start
```

### ngrok Issues
```bash
# Check ngrok status
sudo systemctl status ngrok

# View ngrok dashboard
curl http://localhost:4040/api/tunnels

# Restart ngrok
sudo systemctl restart ngrok
```

---

## 📄 License

This project is private and proprietary.

---

## 👥 Team

Built by [Your Name] as part of [Your Project/Course].

---

## 🔗 Links

- **GitHub Repository:** https://github.com/fablihamaliha/PRA
- **Live Application:** https://skincares.work
- **Docker Image:** ghcr.io/fablihamaliha/pra:latest

---

**Last Updated:** 2026-01-02
