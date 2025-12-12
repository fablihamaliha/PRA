# PRRA - Personal Routine & Recommendation Assistant

## Skincare Recommendation Module

A Flask-based REST API that provides personalized skincare product recommendations based on user skin profiles, concerns, and preferences.

## Architecture
```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────┐
│   Flask API         │
│  (app.py)           │
└──────┬──────────────┘
       │
       ├──► Blueprints (skincare.py)
       │
       ├──► Services
       │    ├─► external_api.py (Fetch products)
       │    ├─► scoring.py (Score matching)
       │    └─► recommender.py (Generate recommendations)
       │
       ├──► Models (SQLAlchemy)
       │    ├─► User
       │    ├─► SkinProfile
       │    ├─► Product
       │    └─► Recommendation
       │
       └──► Database (PostgreSQL)
```

## Features

- **User Profile Management**: Store and update skin type, concerns, and preferences
- **Product Scoring**: Intelligent matching algorithm based on multiple factors
- **Multi-Source Integration**: Extensible architecture for multiple product APIs
- **Recommendation History**: Track all recommendation sessions
- **Docker Support**: Full containerization with Docker Compose

## Setup & Installation

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if running locally)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repo-url>
cd prra
```

2. Start services:
```bash
docker-compose up -d
```

3. Verify health:
```bash
curl http://localhost:5000/health
```

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/prra_db
export SECRET_KEY=your-secret-key
```

4. Run application:
```bash
python app.py
```

## API Usage

### 1. Create/Update Skin Profile

**Endpoint:** `POST /skincare/quiz`

**Request:**
```json
{
  "user_id": 1,
  "skin_type": "oily",
  "concerns": ["acne", "redness"],
  "budget_min": 10,
  "budget_max": 40,
  "preferred_ingredients": ["niacinamide", "cica"],
  "avoided_ingredients": ["fragrance"]
}
```

**Response:**
```json
{
  "message": "Skin profile saved successfully",
  "profile_id": 123
}
```

### 2. Get Recommendations

**Endpoint:** `POST /skincare/recommend`

**Request (with user_id):**
```json
{
  "user_id": 1
}
```

**Request (with full profile):**
```json
{
  "skin_type": "oily",
  "concerns": ["acne", "redness"],
  "budget_min": 10,
  "budget_max": 40,
  "preferred_ingredients": ["niacinamide"],
  "avoided_ingredients": ["fragrance"]
}
```

**Response:**
```json
{
  "session_id": 456,
  "recommendations": [
    {
      "product_id": 789,
      "name": "CeraVe Foaming Facial Cleanser",
      "brand": "CeraVe",
      "price": 14.99,
      "currency": "USD",
      "url": "https://example.com/product",
      "image_url": "https://example.com/image.jpg",
      "score": 0.93,
      "reason": "Great for acne and oily skin, contains niacinamide, fragrance-free"
    },
    {
      "product_id": 790,
      "name": "The Ordinary Niacinamide 10% + Zinc 1%",
      "brand": "The Ordinary",
      "price": 5.90,
      "currency": "USD",
      "url": "https://example.com/product2",
      "image_url": "https://example.com/image2.jpg",
      "score": 0.91,
      "reason": "Contains preferred ingredient niacinamide, excellent for oily skin and acne"
    }
  ]
}
```

## Database Schema

### Users
- id (PK)
- email
- name
- created_at

### SkinProfile
- id (PK)
- user_id (FK)
- skin_type
- concerns (JSON)
- budget_min, budget_max
- preferred_ingredients (JSON)
- avoided_ingredients (JSON)
- updated_at

### Product
- id (PK)
- external_id
- name, brand
- price, currency
- url, image_url
- source
- skin_types (JSON)
- tags (JSON)
- ingredients (JSON)
- rating, num_reviews
- last_seen_at

### RecommendationSession
- id (PK)
- user_id (FK)
- skin_profile_id (FK)
- created_at

### RecommendationItem
- id (PK)
- session_id (FK)
- product_id (FK)
- rank
- match_score
- reason

## Scoring Algorithm

Products are scored on a 0-1 scale based on:

- **+0.4**: Skin type match
- **+0.3**: Concern match
- **+0.2**: Preferred ingredients present
- **-0.1**: Avoided ingredients present
- **+0.1**: High rating (>4.0)

## Configuration

Environment variables:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# API Keys
SEPHORA_API_KEY=your_key
AMAZON_API_KEY=your_key

# App Settings
MAX_RECOMMENDATIONS=3
MIN_PRODUCT_RATING=3.5
LOG_LEVEL=INFO
```

## Development

### Running Tests
```bash
pytest tests/
```

### Database Migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Code Formatting
```bash
black .
flake8 .
```

## Future Enhancements

- [ ] User authentication & authorization
- [ ] Product caching with Redis
- [ ] Real API integrations (Sephora, Amazon)
- [ ] ML-based recommendation improvements
- [ ] User feedback loop
- [ ] Product review aggregation
- [ ] Price tracking & alerts
- [ ] Ingredient analysis API

## License

MIT

## Support

For issues and questions, please open a GitHub issue.