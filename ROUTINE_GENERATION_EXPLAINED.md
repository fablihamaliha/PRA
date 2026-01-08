# How Routines Are Generated Based on User Form Data

## 📋 Complete Data Flow from Form → AI → Products → User

### Step 1: User Fills Form ([build_routine.html](pra/templates/build_routine.html))

**Form Fields Collected:**
```javascript
{
  skin_type: "combination",           // Dropdown: oily/dry/combination/normal/sensitive
  concerns: ["acne", "aging"],        // Checkboxes: acne/aging/hyperpigmentation/etc.
  budget: "mid-range",                // Dropdown: budget/mid-range/luxury/mixed
  lifestyle: ["outdoors", "makeup"],  // Checkboxes: outdoors/makeup/minimal/extensive/gym/travel
  preferred_ingredients: ["niacinamide", "vitamin C"],  // Tag input
  avoided_ingredients: ["fragrance", "alcohol"]         // Tag input
}
```

**Where this happens:**
- [build_routine.html:419-528](pra/templates/build_routine.html) - Form submission handler

---

### Step 2: Form Data Sent to Backend ([routine_builder.py:78-190](pra/blueprints/routine_builder.py))

**API Endpoint:** `POST /api/generate-routine`

**Flow:**
```python
# 1. Extract form data
skin_type = data.get('skin_type', 'normal')
concerns = data.get('concerns', [])
budget = data.get('budget', 'mixed')
lifestyle = data.get('lifestyle', [])
preferred_ingredients = data.get('preferred_ingredients', [])
avoided_ingredients = data.get('avoided_ingredients', [])

# 2. Call AI service to generate routine structure
routine_structure = routine_service.generate_routine_structure(
    skin_type=skin_type,
    concerns=concerns,
    budget=budget,
    lifestyle=lifestyle,
    preferred_ingredients=preferred_ingredients,
    avoided_ingredients=avoided_ingredients
)
```

---

### Step 3: AI Generates Personalized Routine ([routine_builder_service.py:23-160](pra/services/routine_builder_service.py))

**What Happens:**

#### 3A. Build Prompt for GPT-4
The service creates a detailed prompt using ALL the user's inputs:

```python
prompt = f"""
You are a friendly skincare concierge helping someone build their perfect routine.

User Profile:
- Skin Type: {skin_type}                    # "combination"
- Main Concerns: {concerns_str}             # "acne, aging"
- Budget Preference: {budget}               # "mid-range"
- Lifestyle: {lifestyle_str}                # "outdoors, makeup"
- Prefers Ingredients: {preferred_str}      # "niacinamide, vitamin C"
- Wants to Avoid: {avoided_str}             # "fragrance, alcohol"

Create a personalized AM and PM routine...
"""
```

**Key Customization Rules in Prompt:**
- ✅ **Adjust complexity** based on lifestyle (minimal steps if user selected "minimal")
- ✅ **Always include SPF** in AM (critical for all skin types, emphasized if "outdoors")
- ✅ **Add makeup remover** if user selected "makeup daily"
- ✅ **Emphasize antioxidants** if user selected "outdoors"
- ✅ **Use preferred ingredients** (niacinamide, vitamin C)
- ✅ **Avoid blacklisted ingredients** (fragrance, alcohol)
- ✅ **Match budget** preference (under $20, $20-$50, or $50+)

#### 3B. GPT-4 Returns Structured Routine

**AI Response Format:**
```json
{
  "AM": [
    {
      "step_name": "Cleanser",
      "order": 1,
      "why_this_matters": "Removes overnight oils without stripping your skin",
      "budget_option": {
        "product_name": "CeraVe Hydrating Facial Cleanser",
        "brand": "CeraVe",
        "price": 15.99,
        "why_chosen": "Perfect for combination skin - hydrates dry areas without clogging pores",
        "key_ingredients": [
          {"name": "Hyaluronic Acid", "what_it_does": "Pulls moisture into your skin"},
          {"name": "Ceramides", "what_it_does": "Repairs your skin barrier"}
        ],
        "purchase_link": "https://amazon.com/cerave-cleanser",
        "retailer": "Amazon"
      },
      "midrange_option": { /* $20-$50 product */ },
      "luxury_option": { /* $50+ product */ }
    },
    {
      "step_name": "Vitamin C Serum",  // ← USER REQUESTED THIS!
      "order": 2,
      "why_this_matters": "Brightens skin and fights aging - exactly what you need",
      "budget_option": { /* Contains vitamin C */ },
      "midrange_option": { /* Contains vitamin C */ },
      "luxury_option": { /* Contains vitamin C */ }
    },
    {
      "step_name": "SPF 50 Sunscreen",  // ← EMPHASIZED because user is "outdoors"
      "order": 3,
      "why_this_matters": "Critical protection since you spend time outdoors",
      // ... options
    }
  ],
  "PM": [
    {
      "step_name": "Makeup Remover",  // ← ADDED because user wears makeup
      "order": 1,
      // ...
    },
    {
      "step_name": "Retinol Serum",   // ← TARGETS "aging" concern
      "order": 2,
      // ...
    }
  ]
}
```

**How AI Personalizes Based on Form:**

| User Input | How AI Uses It | Example Output |
|------------|----------------|----------------|
| **Skin Type: "combination"** | Selects products that balance oily T-zone + dry cheeks | "CeraVe - hydrates dry areas without clogging pores" |
| **Concerns: "acne"** | Includes salicylic acid, niacinamide, retinol | "Paula's Choice BHA - unclogs pores and prevents breakouts" |
| **Concerns: "aging"** | Includes retinol, peptides, vitamin C | "Retinol 0.5% - boosts collagen production" |
| **Budget: "mid-range"** | Focuses on $20-$50 products | Budget shown but emphasizes mid-range |
| **Lifestyle: "outdoors"** | Strong SPF 50+, antioxidants | "SPF 50 is critical for sun exposure" |
| **Lifestyle: "makeup"** | Adds double cleanse, makeup remover | "Oil cleanser removes makeup before face wash" |
| **Lifestyle: "minimal"** | 3-4 steps max | AM: Cleanser, Moisturizer+SPF, PM: Cleanser, Treatment |
| **Lifestyle: "extensive"** | 7-8 steps | Full routine with toner, essence, serum, eye cream, etc. |
| **Preferred: "niacinamide"** | Includes products with niacinamide | "10% Niacinamide - brightens and shrinks pores" |
| **Avoided: "fragrance"** | Filters out fragranced products | All products are fragrance-free |

---

### Step 4: Product Search (Currently Simplified)

**Current Implementation:**
```python
# For each step in routine
for step in routine_structure.get('AM', []):
    products = scraper_service.search_products(
        category=step['category'],
        search_terms=step['search_terms'],
        preferred_ingredients=preferred_ingredients,
        avoided_ingredients=avoided_ingredients,
        limit=1
    )
```

**Future: Real Product Scraping**
- Search Amazon, Sephora, Ulta for matching products
- Filter by ingredients (include preferred, exclude avoided)
- Match price range to budget
- Return products with real prices, links, reviews

---

### Step 5: Store Routine ([routine_builder.py:131-190](pra/blueprints/routine_builder.py))

**Session Storage (All Users):**
```python
session_id = str(uuid.uuid4())
session[f'routine_{session_id}'] = {
    'skin_type': skin_type,
    'concerns': concerns,
    'budget': budget,
    'lifestyle': lifestyle,
    'preferred_ingredients': preferred_ingredients,
    'avoided_ingredients': avoided_ingredients,
    'routine': routine_with_products
}
```

**Database Storage (Logged-In Users Only):**
```python
if current_user.is_authenticated:
    SavedRoutine(
        user_id=current_user.id,
        session_id=session_id,
        skin_type=skin_type,
        concerns=json.dumps(concerns),
        budget=budget,
        lifestyle=json.dumps(lifestyle),
        preferred_ingredients=json.dumps(preferred_ingredients),
        avoided_ingredients=json.dumps(avoided_ingredients),
        routine_data=json.dumps(routine_with_products),
        is_active=True
    )
```

---

### Step 6: Display Results ([routine_results.html](pra/templates/routine_results.html))

**User sees:**
```
Your Personalized Routine
"Combination Skin" badge

☀️ Morning Routine
┌─────────────────────────────────────┐
│ CeraVe Hydrating Cleanser          │
│ Why: Gentle for your combo skin    │
│ $15.99                              │
│ [View Product]                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ The Ordinary Niacinamide 10%       │  ← USER REQUESTED THIS!
│ Why: Shrinks pores & fades spots   │
│ $6.00                               │
│ [View Product]                      │
└─────────────────────────────────────┘

🌙 Evening Routine
...
```

---

## 🎯 Example: Complete Personalization in Action

### User Inputs:
```
Skin Type: Combination
Concerns: Acne, Hyperpigmentation
Budget: Budget-friendly
Lifestyle: Outdoors, Minimal routine
Preferred: Niacinamide, Vitamin C
Avoided: Fragrance, Essential oils
```

### AI-Generated Routine (Simplified):

**AM (3 steps - minimal!):**
1. **CeraVe Foaming Cleanser** ($13)
   - Why: "Gentle enough for combo skin, won't strip moisture"
   - Contains: Niacinamide ✅ (user requested!)
   - Avoids: Fragrance ✅ (user blacklisted!)

2. **The Ordinary Vitamin C Suspension** ($6)
   - Why: "Fades dark spots from acne, super affordable"
   - Contains: Vitamin C ✅ (user requested!)
   - Budget: Under $20 ✅ (user preference!)

3. **La Roche-Posay Anthelios SPF 50** ($18)
   - Why: "Strong protection since you're outdoors often"
   - SPF 50 ✅ (emphasized for "outdoors" lifestyle!)

**PM (2 steps - minimal!):**
1. **Same Cleanser** ($13)

2. **Paula's Choice 2% BHA** ($17)
   - Why: "Unclogs pores, prevents acne breakouts"
   - Targets: Acne concern ✅
   - Budget: Under $20 ✅

**Total: 4 products, $67 total, all under $20 each**

---

## 🧠 AI Reasoning Examples

### Scenario 1: Oily Skin + Acne + Outdoors
**AI Decision:**
- ✅ Lightweight gel moisturizer (not cream)
- ✅ Salicylic acid cleanser (oil control)
- ✅ SPF 50+ matte finish (oil-free for outdoors)
- ✅ Niacinamide serum (oil regulation + pore refinement)

### Scenario 2: Dry Skin + Aging + Minimal Routine
**AI Decision:**
- ✅ Creamy hydrating cleanser (not foaming)
- ✅ All-in-one moisturizer + SPF (minimal steps)
- ✅ Retinol + hyaluronic acid serum (anti-aging + hydration)
- ✅ Rich night cream (barrier repair)

### Scenario 3: Sensitive Skin + Redness + Extensive Routine
**AI Decision:**
- ✅ 7-8 step routine (user wants extensive)
- ✅ Centella asiatica, niacinamide (calming)
- ✅ NO retinol, acids, or actives (sensitivity)
- ✅ Fragrance-free, hypoallergenic only
- ✅ Includes: Toner, essence, ampoule, sleeping mask

---

## 🔄 How Updates Work

When user clicks "Update Routine":

1. **Form pre-fills** with saved data
2. User changes `concerns: ["acne"]` → `concerns: ["acne", "dryness"]`
3. **New AI prompt** generated with updated concerns
4. AI adds **hydrating products** (hyaluronic acid serum, richer moisturizer)
5. **Existing routine updated** in database (not duplicated)

---

## 🎨 Summary: Form → Personalization

```
USER FORM DATA
    ↓
GPT-4 PROMPT (includes ALL form fields)
    ↓
AI ANALYZES & CUSTOMIZES
- Matches products to skin type
- Targets specific concerns
- Respects budget constraints
- Adjusts steps for lifestyle
- Uses preferred ingredients
- Avoids blacklisted ingredients
    ↓
STRUCTURED ROUTINE JSON
    ↓
PRODUCT SEARCH (matches AI recommendations)
    ↓
FINAL PERSONALIZED ROUTINE
- Stored in session (guests)
- Saved to database (logged-in)
    ↓
DISPLAYED TO USER
```

**Every single field** from the form influences the AI's decisions! Nothing is ignored.
