# PRA Application - Complete File Connection Map

**A Visual Guide to Understanding How Everything Connects**

---

## 🎯 The Big Picture

Your PRA application follows a **layered architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Browser)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: ROUTES & TEMPLATES (Entry Points)             │
│  - app.py (main routes: /, /auth, /login, /signup)      │
│  - blueprints/skincare.py (/skincare/*)                 │
│  - blueprints/deals.py (/deals/*)                       │
│  - templates/ (HTML pages)                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: BUSINESS LOGIC (Services)                     │
│  - services/recommender.py (orchestrates recommendations)│
│  - services/scoring.py (calculates product scores)      │
│  - services/deal_finder_service.py (finds deals)        │
│  - services/gpt_service.py (AI enhancements)            │
│  - services/external_api.py (fetches products)          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: DATA MODELS (Database Structure)              │
│  - models/user.py (user accounts)                       │
│  - models/skin_profile.py (user preferences)            │
│  - models/product.py (product catalog)                  │
│  - models/recommendation.py (recommendation history)    │
│  - models/db.py (database connection)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 4: DATABASE (PostgreSQL / SQLite)                │
│  Tables: users, skin_profiles, products,                │
│          recommendation_sessions, recommendation_items  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔗 Detailed Connection Map

### **1. Application Entry Point: app.py**

```
app.py (Main Flask Application)
   │
   ├──→ Imports & Uses:
   │    │
   │    ├─→ config.py
   │    │   └─ Config class
   │    │      ├─ SECRET_KEY (from .env)
   │    │      ├─ DATABASE_URL (from .env)
   │    │      ├─ API keys (OPENAI_API_KEY, RAPIDAPI_KEY, etc.)
   │    │      └─ Application settings (MAX_RECOMMENDATIONS, LOG_LEVEL)
   │    │
   │    ├─→ models/db.py
   │    │   └─ db = SQLAlchemy()
   │    │      └─ db.init_app(app)  ← Connects database to Flask
   │    │
   │    ├─→ models/user.py
   │    │   └─ User class
   │    │      └─ Used by:
   │    │         ├─ @login_manager.user_loader (line 48-51)
   │    │         ├─ /login route (line 121)
   │    │         └─ /signup route (line 186)
   │    │
   │    ├─→ blueprints/skincare.py
   │    │   └─ skincare_bp
   │    │      └─ app.register_blueprint(skincare_bp, url_prefix='/skincare')
   │    │         Creates routes:
   │    │         ├─ POST /skincare/quiz
   │    │         ├─ POST /skincare/recommend
   │    │         ├─ GET /skincare/profile/<user_id>
   │    │         └─ GET /skincare/history/<user_id>
   │    │
   │    └─→ blueprints/deals.py
   │        └─ deals_bp
   │           └─ app.register_blueprint(deals_bp, url_prefix='/deals')
   │              Creates routes:
   │              ├─ GET /deals/
   │              ├─ POST /deals/api/search
   │              ├─ GET /deals/api/location
   │              └─ GET /deals/api/health
   │
   └──→ Defines Routes:
        ├─ GET / → renders templates/index.html
        ├─ GET /auth → renders templates/auth.html
        ├─ POST /login → authenticates user
        ├─ POST /signup → creates new user
        ├─ POST /logout → logs out user
        └─ GET /current-user → returns current user info
```

---

### **2. Configuration Flow: config.py**

```
config.py
   │
   ├─→ Loads from Environment (.env file):
   │   ├─ SECRET_KEY
   │   ├─ DATABASE_URL
   │   ├─ OPENAI_API_KEY
   │   ├─ RAPIDAPI_KEY
   │   └─ Other API keys (SEPHORA, AMAZON, etc.)
   │
   └─→ Used by:
       ├─ app.py → app.config.from_object(Config)
       ├─ services/recommender.py → Config()
       ├─ services/external_api.py → Config()
       └─ services/gpt_service.py → os.getenv('OPENAI_API_KEY')
```

---

### **3. Database Layer: models/**

```
models/db.py
   │
   └─→ db = SQLAlchemy()
       │
       ├─→ Used by ALL models:
       │   ├─ models/user.py → class User(db.Model)
       │   ├─ models/skin_profile.py → class SkinProfile(db.Model)
       │   ├─ models/product.py → class Product(db.Model)
       │   └─ models/recommendation.py → class RecommendationSession(db.Model)
       │
       └─→ Connected to app in app.py:
           └─ db.init_app(app)

┌──────────────────────────────────────────────────────────────┐
│                    DATABASE RELATIONSHIPS                     │
└──────────────────────────────────────────────────────────────┘

User (models/user.py)
   │
   ├─→ One-to-Many with SkinProfile
   │   └─ user.skin_profiles (list of profiles)
   │
   └─→ One-to-Many with RecommendationSession
       └─ user.recommendation_sessions (list of sessions)

SkinProfile (models/skin_profile.py)
   │
   ├─→ Many-to-One with User
   │   └─ skin_profile.user (the user object)
   │
   └─→ One-to-Many with RecommendationSession
       └─ skin_profile.recommendation_sessions (list of sessions)

RecommendationSession (models/recommendation.py)
   │
   ├─→ Many-to-One with User
   │   └─ session.user (the user object)
   │
   ├─→ Many-to-One with SkinProfile
   │   └─ session.skin_profile (the profile used)
   │
   └─→ One-to-Many with RecommendationItem
       └─ session.items (list of recommended products)

RecommendationItem (models/recommendation.py)
   │
   ├─→ Many-to-One with RecommendationSession
   │   └─ item.session (the session it belongs to)
   │
   └─→ Many-to-One with Product
       └─ item.product (the product details)

Product (models/product.py)
   │
   └─→ One-to-Many with RecommendationItem
       └─ product.recommendation_items (list of recommendations)
```

---

### **4. Skincare Blueprint: blueprints/skincare.py**

```
blueprints/skincare.py
   │
   ├──→ Imports:
   │    ├─ models/db.py → db
   │    ├─ models/user.py → User
   │    ├─ models/skin_profile.py → SkinProfile
   │    ├─ models/product.py → Product
   │    ├─ models/recommendation.py → RecommendationSession, RecommendationItem
   │    ├─ services/recommender.py → RecommenderService
   │    └─ utils/validators.py → validate_quiz_input, validate_recommend_input
   │
   └──→ Routes:
        │
        ├─ POST /skincare/quiz
        │  └─→ Flow:
        │     1. Validate input with validators.validate_quiz_input()
        │     2. Find or create SkinProfile for user
        │     3. Save to database using db.session
        │     4. Return profile_id
        │
        ├─ POST /skincare/recommend
        │  └─→ Flow:
        │     1. Validate input with validators.validate_recommend_input()
        │     2. Get SkinProfile from database OR use provided data
        │     3. Call RecommenderService().get_recommendations()
        │        │
        │        └─→ RecommenderService (services/recommender.py)
        │            ├─→ ExternalAPIService.fetch_sephora_products()
        │            ├─→ ExternalAPIService.fetch_amazon_products()
        │            ├─→ ExternalAPIService.normalize_products()
        │            ├─→ ScoringService.score_product()
        │            ├─→ ScoringService.generate_reason()
        │            ├─→ GPTService.enhance_product_descriptions()
        │            └─→ Saves products to database (Product model)
        │     4. Create RecommendationSession
        │     5. Create RecommendationItems for each product
        │     6. Save to database
        │     7. Return recommendations
        │
        ├─ GET /skincare/profile/<user_id>
        │  └─→ Query SkinProfile from database
        │     └─ Return SkinProfile.to_dict()
        │
        └─ GET /skincare/history/<user_id>
           └─→ Query RecommendationSessions from database
              └─ Return list of sessions with items
```

---

### **5. Deals Blueprint: blueprints/deals.py**

```
blueprints/deals.py
   │
   ├──→ Imports:
   │    └─ services/deal_finder_service.py → DealFinderService
   │
   └──→ Routes:
        │
        ├─ GET /deals/
        │  └─→ Renders templates/deal_finder.html
        │
        ├─ POST /deals/api/search
        │  └─→ Flow:
        │     1. Get product_name from request
        │     2. Optionally get user location
        │        └─→ DealFinderService.get_user_location(ip)
        │     3. Call DealFinderService.search_deals()
        │        │
        │        └─→ DealFinderService (services/deal_finder_service.py)
        │            ├─→ Check cache
        │            ├─→ Call RapidAPI (external API)
        │            ├─→ Normalize products
        │            ├─→ Sort by price
        │            ├─→ GPTService.generate_deal_insights()
        │            └─→ Cache results
        │     4. Return deals JSON
        │
        ├─ GET /deals/api/location
        │  └─→ Get user IP
        │     └─→ DealFinderService.get_user_location(ip)
        │        └─→ Calls ipapi.co (external service)
        │
        └─ GET /deals/api/health
           └─→ Returns API service status
```

---

### **6. Service Layer Connection Map**

```
┌─────────────────────────────────────────────────────────┐
│         RecommenderService (services/recommender.py)     │
│         The Main Orchestrator for Recommendations        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├──→ Uses Config (config.py)
                   │    └─ Gets MAX_RECOMMENDATIONS, MIN_PRODUCT_RATING
                   │
                   ├──→ Uses ExternalAPIService (services/external_api.py)
                   │    │
                   │    └─→ ExternalAPIService
                   │        ├─→ Uses Config for API keys
                   │        ├─ fetch_sephora_products()
                   │        ├─ fetch_amazon_products()
                   │        └─ normalize_products()
                   │           └─ Converts different API formats to standard
                   │
                   ├──→ Uses ScoringService (services/scoring.py)
                   │    │
                   │    └─→ ScoringService
                   │        ├─ score_product(product, profile)
                   │        │  └─ Calculates match score (0.0-1.0)
                   │        │     Based on:
                   │        │     ├─ Skin type match (40%)
                   │        │     ├─ Concerns addressed (30%)
                   │        │     ├─ Preferred ingredients (20%)
                   │        │     ├─ Avoided ingredients penalty (10%)
                   │        │     └─ Rating bonus (10%)
                   │        │
                   │        └─ generate_reason(product, profile, score)
                   │           └─ Creates human-readable explanation
                   │
                   ├──→ Uses GPTService (services/gpt_service.py)
                   │    │
                   │    └─→ GPTService
                   │        ├─→ Uses OpenAI API (OPENAI_API_KEY from env)
                   │        ├─ generate_skincare_advice(profile)
                   │        ├─ explain_product_recommendation()
                   │        └─ enhance_product_descriptions(products)
                   │           └─ Adds GPT-generated explanations
                   │
                   └──→ Saves to Database
                        └─ models/product.py → Product model
                           └─ db.session.add() / db.session.commit()

┌─────────────────────────────────────────────────────────┐
│      DealFinderService (services/deal_finder_service.py) │
│         Finds Product Deals from Multiple Retailers      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├──→ Uses RAPIDAPI_KEY (from environment)
                   │    └─ Calls RapidAPI Real-Time Product Search
                   │       └─ Searches Amazon, Walmart, eBay, etc.
                   │
                   ├──→ Uses GPTService (services/gpt_service.py)
                   │    └─ generate_deal_insights()
                   │       └─ AI-generated shopping advice
                   │
                   ├──→ Uses ipapi.co (external service)
                   │    └─ get_user_location(ip)
                   │       └─ Gets user's city, region, country
                   │
                   └──→ Caching
                        └─ In-memory cache (30 min TTL)
```

---

### **7. Templates & Frontend Flow**

```
templates/index.html (Main Landing Page)
   ├─→ Served by: app.py route GET /
   ├─→ Links to: static/css/main.css
   ├─→ Links to: static/js/main.js
   └─→ Makes API calls to:
       ├─ GET /current-user (check if logged in)
       ├─ POST /deals/api/search (search for deals)
       └─ POST /skincare/recommend (get recommendations)

templates/auth.html (Login/Signup Page)
   ├─→ Served by: app.py route GET /auth
   ├─→ Links to: static/css/auth.css
   └─→ Makes API calls to:
       ├─ POST /login (authenticate user)
       └─ POST /signup (create new account)

templates/deal_finder.html (Deal Finder Page)
   ├─→ Served by: blueprints/deals.py route GET /deals/
   ├─→ Links to: static/css/deal_finder.css
   └─→ Makes API calls to:
       ├─ POST /deals/api/search (search for deals)
       └─ GET /deals/api/location (get user location)

static/js/main.js (Frontend JavaScript)
   └─→ Handles:
       ├─ User authentication (login/signup/logout)
       ├─ API communication (fetch)
       ├─ DOM manipulation
       └─ State management (currentUser)
```

---

### **8. Data Flow: Complete User Journey**

#### **Journey 1: User Signup & Login**

```
1. User visits http://localhost:5001/auth
   └─→ app.py: GET /auth
       └─→ Renders templates/auth.html

2. User fills signup form
   └─→ JavaScript POSTs to /signup
       └─→ app.py: POST /signup (line 155)
           ├─ Validates email & password
           ├─ Creates User object (models/user.py)
           ├─ user.set_password(password) - hashes password
           ├─ db.session.add(user)
           ├─ db.session.commit()
           └─ login_user(user) - Flask-Login creates session
           └─ Returns: { success: true, user: {...} }

3. Browser receives response
   └─→ JavaScript redirects to /deals

4. Subsequent requests include session cookie
   └─→ Flask-Login automatically loads user
       └─→ @login_manager.user_loader (app.py line 48)
           └─→ User.query.get(user_id)
```

#### **Journey 2: Getting Skincare Recommendations**

```
1. User fills skincare quiz
   └─→ JavaScript POSTs to /skincare/quiz
       └─→ blueprints/skincare.py: POST /skincare/quiz
           ├─ validators.validate_quiz_input(data)
           ├─ Finds or creates SkinProfile (models/skin_profile.py)
           ├─ Sets: skin_type, concerns, budget, ingredients
           ├─ db.session.commit()
           └─ Returns: { profile_id: 123 }

2. User clicks "Get Recommendations"
   └─→ JavaScript POSTs to /skincare/recommend
       └─→ blueprints/skincare.py: POST /skincare/recommend
           │
           ├─ Gets SkinProfile from database
           │
           └─→ RecommenderService.get_recommendations(profile)
               │
               ├─→ ExternalAPIService.fetch_sephora_products()
               │   └─ Returns mock products (would call API in prod)
               │
               ├─→ ExternalAPIService.fetch_amazon_products()
               │   └─ Returns mock products
               │
               ├─→ ExternalAPIService.normalize_products()
               │   └─ Converts to standard format
               │
               ├─ Filters by budget range
               │
               ├─→ ScoringService.score_product() for each
               │   ├─ Calculates match score (0-1)
               │   └─ ScoringService.generate_reason()
               │
               ├─ Sorts by score (highest first)
               │
               ├─→ GPTService.enhance_product_descriptions()
               │   └─ Adds AI explanations (if OpenAI key available)
               │
               └─→ Saves products to database
                   └─ Product model (models/product.py)

           ├─ Creates RecommendationSession
           │  └─ Links to user_id and skin_profile_id
           │
           ├─ Creates RecommendationItems
           │  └─ For each recommended product:
           │     ├─ session_id
           │     ├─ product_id
           │     ├─ rank (1, 2, 3...)
           │     ├─ match_score
           │     └─ reason
           │
           ├─ db.session.commit()
           │
           └─ Returns: { session_id, recommendations: [...] }

3. Browser receives recommendations
   └─→ JavaScript displays products with scores & reasons
```

#### **Journey 3: Searching for Deals**

```
1. User searches for "face moisturizer"
   └─→ JavaScript POSTs to /deals/api/search
       └─→ blueprints/deals.py: POST /deals/api/search
           │
           ├─ Gets client IP address
           │
           ├─→ DealFinderService.get_user_location(ip)
           │   └─ Calls ipapi.co API
           │   └─ Returns: { city, region, country, ... }
           │
           └─→ DealFinderService.search_deals("face moisturizer", location)
               │
               ├─ Checks cache (30 min TTL)
               │
               ├─→ Calls RapidAPI Real-Time Product Search
               │   └─ Searches across Amazon, Walmart, eBay
               │   └─ Returns: list of products with prices
               │
               ├─ Normalizes each product
               │  └─ Extracts: name, price, url, seller, rating
               │
               ├─ Sorts by price (lowest first)
               │
               ├─→ GPTService.generate_deal_insights()
               │   └─ AI analyzes deals
               │   └─ Returns shopping advice
               │
               ├─ Caches results
               │
               └─ Returns: {
                     product_name,
                     best_deal: {...},
                     all_deals: [...],
                     gpt_insights: "..."
                   }

2. Browser receives deals
   └─→ JavaScript displays sorted deals with prices & links
```

---

### **9. Import Dependency Tree**

```
app.py
 ├─→ flask
 ├─→ flask_cors
 ├─→ flask_login
 ├─→ dotenv
 ├─→ config.py
 ├─→ models/db.py
 │    └─→ flask_sqlalchemy
 ├─→ models/user.py
 │    ├─→ models/db.py
 │    ├─→ flask_login.UserMixin
 │    └─→ werkzeug.security
 ├─→ blueprints/skincare.py
 │    ├─→ flask
 │    ├─→ models/db.py
 │    ├─→ models/user.py
 │    ├─→ models/skin_profile.py
 │    │    └─→ models/db.py
 │    ├─→ models/product.py
 │    │    └─→ models/db.py
 │    ├─→ models/recommendation.py
 │    │    └─→ models/db.py
 │    ├─→ services/recommender.py
 │    │    ├─→ config.py
 │    │    ├─→ services/external_api.py
 │    │    │    ├─→ config.py
 │    │    │    └─→ requests
 │    │    ├─→ services/scoring.py
 │    │    ├─→ services/gpt_service.py
 │    │    │    └─→ openai
 │    │    └─→ models/product.py
 │    └─→ utils/validators.py
 └─→ blueprints/deals.py
      ├─→ flask
      └─→ services/deal_finder_service.py
           ├─→ requests
           └─→ services/gpt_service.py
```

---

### **10. External Connections**

```
Your PRA Application
    │
    ├─→ PostgreSQL Database (Production)
    │   └─ postgresql://prra_user:***@192.168.1.68:5432/prra_db
    │
    ├─→ SQLite Database (Development)
    │   └─ instance/pra.db
    │
    ├─→ OpenAI API (GPT Service)
    │   └─ api.openai.com
    │      Model: gpt-4o-mini
    │
    ├─→ RapidAPI (Deal Finder)
    │   └─ real-time-product-search.p.rapidapi.com
    │      └─ Searches: Amazon, Walmart, eBay, Target, Best Buy
    │
    └─→ IP Location Service (Deal Finder)
        └─ ipapi.co
           └─ Returns: city, region, country from IP
```

---

## 🎨 Visual Summary: The Connection Flow

```
┌────────────────────────────────────────────────────────────┐
│                         BROWSER                             │
│  (User Interface - HTML, CSS, JavaScript)                   │
└──────────────────────┬─────────────────────────────────────┘
                       │ HTTP Requests (GET, POST)
                       ↓
┌────────────────────────────────────────────────────────────┐
│                       app.py                                │
│  (Flask Application - Routes & Initialization)              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Uses: config.py, models/db.py                      │    │
│  │ Registers: skincare_bp, deals_bp                   │    │
│  │ Routes: /, /auth, /login, /signup, /logout         │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬─────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ↓                             ↓
┌─────────────────┐         ┌─────────────────────┐
│ skincare_bp     │         │ deals_bp            │
│ (Skincare)      │         │ (Deal Finder)       │
└────────┬────────┘         └────────┬────────────┘
         │                           │
         ↓                           ↓
┌──────────────────┐        ┌──────────────────────┐
│ RecommenderService│       │ DealFinderService    │
└────────┬─────────┘        └────────┬─────────────┘
         │                           │
         ├─→ ExternalAPIService       ├─→ RapidAPI
         ├─→ ScoringService           └─→ GPTService
         ├─→ GPTService
         └─→ Product model
                  │
                  ↓
         ┌────────────────────┐
         │   DATABASE          │
         │   (PostgreSQL)      │
         │                     │
         │ Tables:             │
         │  - users            │
         │  - skin_profiles    │
         │  - products         │
         │  - recommendation_  │
         │    sessions         │
         │  - recommendation_  │
         │    items            │
         └─────────────────────┘
```

---

## 📝 Key Takeaways

### **1. Clear Separation of Concerns**

- **Routes** (app.py, blueprints/) handle HTTP requests
- **Services** (services/) contain business logic
- **Models** (models/) define data structure
- **Utils** (utils/) provide helper functions

### **2. Database as Central Hub**

- All models connect through `db` (models/db.py)
- `db.init_app(app)` connects everything
- Relationships allow easy navigation (user.skin_profiles, session.items)

### **3. Service Layer Orchestration**

- RecommenderService orchestrates the entire recommendation flow
- Each service has a single responsibility
- Services can call other services (RecommenderService → GPTService)

### **4. Configuration Flows Everywhere**

- config.py is the single source of truth
- Environment variables keep secrets safe
- Different configs for dev/prod/test

### **5. External Dependencies**

- OpenAI for AI enhancements
- RapidAPI for real-time product search
- PostgreSQL for production data storage

---

**Created: January 6, 2026**
**For: PRA (Personal Recommendation Assistant) Project**
**Location: /Users/maliha/Desktop/PRA/**
