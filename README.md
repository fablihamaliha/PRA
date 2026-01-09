# PRA - Product Recommendation Application

> **Note:** This is a private production application. The repository is public for portfolio purposes only. Configuration, documentation, and certain implementation details are not included.

---

## Overview

An intelligent skincare product recommendation system that analyzes user profiles to provide personalized product suggestions and finds the best deals across multiple retailers.

**Status:** 🔴 Private Production Application
**Live:** https://skincares.work

---

## Technology Stack

### Backend
- **Framework:** Python 3.12 + Flask 3.0
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0
- **Authentication:** Flask-Login with secure session management
- **API Integration:** OpenAI GPT-4 for intelligent recommendations

### Frontend
- **UI:** Vanilla JavaScript with responsive design
- **Styling:** Custom CSS with modern animations
- **Templates:** Jinja2 templating engine

### Infrastructure
- **Deployment:** Docker containers on Raspberry Pi
- **CI/CD:** GitHub Actions with automated testing and deployment
- **Database:** Self-hosted PostgreSQL
- **Domain:** Custom domain with Cloudflare Tunnel
- **SSL/TLS:** Automatic HTTPS via Cloudflare

### Security
- **Authentication:** Session-based with secure cookies
- **Rate Limiting:** Built-in DDoS protection
- **Threat Detection:** Real-time security monitoring
- **Admin Access:** Role-based authentication (`@admin.com`)
- **Environment Security:** All secrets managed via environment variables

### Monitoring & Analytics
- **Real-time Analytics:** Visitor tracking and behavior analysis
- **Security Events:** Automated threat detection and logging
- **Admin Dashboard:** SOC-style security operations center
- **Email Alerts:** SMTP-based notification system

---

## Features

### User Features
- ✅ Personalized skincare routine builder
- ✅ AI-powered product recommendations
- ✅ Multi-retailer deal finder (Amazon, Walmart, Target, etc.)
- ✅ Product wardrobe management
- ✅ Shopping list creation
- ✅ Community features and reviews

### Admin Features
- 🔒 Real-time visitor analytics
- 🔒 Security event monitoring
- 🔒 Threat detection dashboard
- 🔒 System health monitoring
- 🔒 Email notification system

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare CDN + DDoS                    │
│                 (Custom Domain: skincares.work)             │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ Cloudflare      │
                    │ Tunnel          │
                    └────────┬────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│              Raspberry Pi (Self-Hosted)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Docker Container: PRA Application                   │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  Flask Application (Port 5001)                 │  │  │
│  │  │  - Routes & Blueprints                         │  │  │
│  │  │  - Security Middleware                         │  │  │
│  │  │  - Analytics Middleware                        │  │  │
│  │  └────────────────┬───────────────────────────────┘  │  │
│  └───────────────────┼──────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │  PostgreSQL Database (Port 5432)                     │  │
│  │  - User data                                         │  │
│  │  - Analytics logs                                    │  │
│  │  - Security events                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
PRA/
├── pra/                          # Main application package
│   ├── app.py                    # Flask application factory
│   ├── config.py                 # Configuration management
│   ├── models/                   # SQLAlchemy models
│   │   ├── user.py              # User model
│   │   ├── analytics.py         # Analytics models
│   │   └── ...
│   ├── blueprints/              # Feature modules
│   │   ├── skincare/           # Skincare recommendations
│   │   ├── deals/              # Deal finder
│   │   └── community/          # Community features
│   ├── middleware/             # Security & analytics
│   ├── services/               # External integrations
│   ├── templates/              # Jinja2 templates
│   └── static/                 # CSS, JS, images
├── Dockerfile                   # Container configuration
├── requirements.txt            # Python dependencies
└── .github/workflows/          # CI/CD pipelines
```

---

## What's NOT Included

This repository is for **portfolio demonstration only**. The following are **not included**:

### ❌ Configuration Files
- Environment variable templates (`.env.example`)
- Database connection strings
- API keys and secrets
- SMTP configuration
- Security settings

### ❌ Documentation
- Setup and installation guides
- Deployment procedures
- Architecture documentation
- Troubleshooting guides
- API integration details

### ❌ Admin Features
- Admin dashboard templates
- Analytics route implementations
- Security monitoring details
- Admin authentication details

### ❌ Credentials
- Database passwords
- API keys (OpenAI, RapidAPI, etc.)
- SMTP credentials
- Admin user accounts
- Secret keys

---

## Why This Approach?

This is a **production application** serving real users. For security and privacy:

1. **Configuration is private** - Prevents unauthorized use of API keys and services
2. **Architecture details are private** - Protects security implementation
3. **Admin features are private** - Prevents unauthorized access attempts
4. **Source code is public** - Demonstrates coding skills and architecture

---

## Tech Highlights

### Security Features
- 🔒 **Multi-layer security middleware** with threat detection
- 🔒 **Automated IP blocking** for suspicious activity
- 🔒 **Rate limiting** per IP address
- 🔒 **Security event logging** with admin notifications
- 🔒 **Role-based access control** for admin features
- 🔒 **Secure session management** with HTTP-only cookies
- 🔒 **HTTPS enforcement** in production

### DevOps Features
- 🚀 **Automated CI/CD** pipeline with GitHub Actions
- 🚀 **Containerized deployment** with Docker
- 🚀 **Zero-downtime deployments** with health checks
- 🚀 **Automated testing** before deployment
- 🚀 **Repository owner verification** in workflows
- 🚀 **Automatic image building** and pushing to GHCR

### Performance Features
- ⚡ **CDN acceleration** via Cloudflare
- ⚡ **DDoS protection** automatic
- ⚡ **Database connection pooling**
- ⚡ **Optimized queries** with SQLAlchemy
- ⚡ **Efficient caching** strategies

---

## API Integrations

### Configured (Keys Not Included)
- **OpenAI GPT-4** - Intelligent product recommendations
- **RapidAPI** - Real-time product search
- **Google Custom Search** - Product discovery
- **Amazon Product API** - E-commerce integration
- **Walmart API** - Deal aggregation
- **Target API** - Price comparison
- **SMTP Service** - Email notifications

---

## Database Schema

### Main Tables
- `users` - User accounts and authentication
- `skin_profiles` - User skin type and concerns
- `recommendations` - AI-generated recommendations
- `saved_routines` - User skincare routines
- `wardrobe` - User product collections
- `shopping_lists` - Shopping list management
- `visitor_logs` - Analytics tracking (🔒 Admin only)
- `security_events` - Threat detection logs (🔒 Admin only)

---

## Development Workflow

### CI/CD Pipeline
1. **Push to GitHub** - Triggers workflow
2. **Repository owner verification** - Security check
3. **Automated testing** - Code quality checks
4. **Docker image build** - Containerization
5. **Push to GHCR** - Image registry
6. **Deploy to Raspberry Pi** - Self-hosted runner
7. **Health checks** - Verify deployment
8. **Automatic rollback** - On failure

---

## Contact

**This is a private production application.** If you're interested in:
- Using this application
- Understanding the implementation
- Accessing the documentation
- Collaborating on similar projects

**Please contact me:**

📧 **Email:** [Your Email]
💼 **LinkedIn:** [Your LinkedIn]
🐙 **GitHub:** [@fablihamaliha](https://github.com/fablihamaliha)

---

## Legal

### License
This software is proprietary and confidential. Unauthorized copying, modification, distribution, or use is strictly prohibited.

### Terms
- ❌ **No redistribution** - Do not copy or redistribute this code
- ❌ **No commercial use** - Cannot be used for commercial purposes without permission
- ❌ **No modification** - Cannot create derivative works
- ❌ **No reverse engineering** - Cannot attempt to reverse engineer
- ✅ **Portfolio viewing only** - May be viewed for portfolio assessment

### Copyright
© 2026 Fabliha Maliha. All rights reserved.

---

## Acknowledgments

Built with:
- Flask & Python
- PostgreSQL
- Docker
- GitHub Actions
- Cloudflare
- OpenAI

---

## Status

- **Development:** Active
- **Deployment:** Production (Self-Hosted)
- **Access:** Private
- **Documentation:** Private
- **Source Code:** Public (Limited)

---

**Note:** This repository serves as a portfolio demonstration. The application is fully functional in production but requires private configuration and documentation to run. For access or inquiries, please contact me directly.

---

**Last Updated:** 2026-01-09
