# GPT Integration Guide

## Overview

Your PRA application now has GPT (ChatGPT) integration powered by OpenAI! This adds intelligent, personalized features to enhance both product recommendations and deal finding.

## What's New

### 1. Enhanced Product Recommendations
- **GPT-powered explanations**: Each recommended skincare product comes with a personalized explanation of why it's perfect for your skin type and concerns
- **Natural language insights**: Instead of generic scores, you get warm, encouraging advice about why each product is a good match

### 2. Smart Deal Insights
- **Price analysis**: GPT analyzes all deals found and highlights the best value
- **Shopping advice**: Get actionable insights about deals, like "Best value is from Target at $11.99"
- **Comparison insights**: Understand price ranges and make informed decisions

### 3. Personalized Skincare Advice
- **Profile-based tips**: Get 3-4 actionable skincare tips based on your unique profile
- **Ingredient recommendations**: Learn which ingredients work best for your skin
- **Routine suggestions**: Receive guidance on building an effective skincare routine

## Setup Instructions

### Step 1: Get Your OpenAI API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (you won't be able to see it again!)

### Step 2: Add API Key to Environment

Open your `.env` file and add:

```bash
OPENAI_API_KEY=your-actual-api-key-here
```

**Example:**
```bash
OPENAI_API_KEY=sk-proj-abc123xyz...
```

### Step 3: Test the Integration

Run the test script to verify everything works:

```bash
source .venv/bin/activate
python test_gpt.py
```

You should see:
- ✅ GPT service is available
- ✅ Skincare advice generated successfully
- ✅ Product explanation generated successfully
- ✅ Deal insights generated successfully

### Step 4: Start Your Application

```bash
source .venv/bin/activate
./start_app.sh
```

## Features in Detail

### 1. Deal Search with GPT Insights

When you search for products (e.g., "moisturizer"), you'll see:

**Before GPT:**
- Simple list of deals
- Price comparisons
- Basic product info

**With GPT:**
- **Intelligent insights** displayed at the top: "Best value is from Target at $11.99, saving you $3 compared to the average price. Amazon and Walmart also have competitive prices."
- Same great deal list, but with smarter guidance

### 2. Personalized Recommendations with Explanations

When you get skincare recommendations:

**Before GPT:**
- Product name, price, score
- Generic "Good match for your skin type" message

**With GPT:**
- **Personalized explanations** like: "This CeraVe Hydrating Moisturizer (85/100 match) is perfect for your oily skin! It contains niacinamide which helps control excess oil and minimize pores, two of your main concerns. Plus, it's fragrance-free as you prefer."
- Warm, encouraging tone that makes skincare feel approachable

### 3. Cost Management

The integration is designed to be cost-effective:

- **Model used**: GPT-4o-mini (very affordable)
- **Smart limiting**: Only top 5 recommendations get GPT enhancements
- **Optional feature**: GPT features gracefully degrade if API key is missing
- **Caching**: Deal results are cached for 30 minutes to reduce API calls

**Estimated costs:**
- Deal insights: ~$0.001 per search (1/10th of a cent)
- Product explanations: ~$0.005 per recommendation set (1/2 cent)
- Typical monthly cost: **Under $5** for moderate usage

## How It Works Technically

### Architecture

```
User Request
    ↓
Backend Service (Flask)
    ↓
GPT Service → OpenAI API
    ↓
Enhanced Results
    ↓
Frontend Display (Beautiful UI)
```

### Files Modified/Created

**New Files:**
- `pra/services/gpt_service.py` - Core GPT integration service
- `test_gpt.py` - Test script for verification
- `GPT_INTEGRATION_GUIDE.md` - This guide

**Modified Files:**
- `requirements.txt` - Added openai==1.54.0
- `.env.example` - Added OPENAI_API_KEY configuration
- `pra/services/recommender.py` - Integrated GPT for product explanations
- `pra/services/deal_finder_service.py` - Integrated GPT for deal insights
- `pra/static/js/main.js` - Display GPT insights in UI
- `pra/static/css/main.css` - Styled GPT insights beautifully

### GPT Service Methods

```python
GPTService()
    .generate_skincare_advice(profile)          # Get personalized skincare tips
    .explain_product_recommendation(product, profile, score)  # Explain why product matches
    .enhance_product_descriptions(products, profile)  # Enhance multiple products
    .generate_deal_insights(product_name, deals)  # Analyze deals and provide insights
    .is_available()  # Check if GPT is configured
```

## Troubleshooting

### Issue: "GPT service not available"

**Solution:**
1. Check `.env` file has `OPENAI_API_KEY=...`
2. Key should start with `sk-proj-` or `sk-`
3. No quotes around the key
4. Restart the application after adding the key

### Issue: "API key invalid"

**Solution:**
1. Verify key is correct (copy-paste from OpenAI)
2. Check your OpenAI account has billing set up
3. Key might have been deleted - create a new one

### Issue: Rate limit errors

**Solution:**
1. Wait a few minutes and try again
2. OpenAI free tier has limits
3. Consider upgrading to paid tier if you use it heavily

### Issue: High costs

**Solution:**
1. GPT features are optional - app works without them
2. Costs should be minimal (~$5/month for normal use)
3. Check OpenAI usage dashboard: https://platform.openai.com/usage

## Disabling GPT Features

If you want to disable GPT features:

1. **Temporary**: Remove or comment out `OPENAI_API_KEY` in `.env`
2. **Permanent**: The app will work normally without GPT, just without the enhanced insights

The application gracefully handles missing GPT integration - all core features (deal finding, recommendations, authentication) work perfectly without it.

## Privacy & Security

- API key is **never** exposed to frontend
- All GPT calls happen server-side
- User data sent to OpenAI: skin type, concerns, product info only
- No personal info (name, email) is sent to OpenAI
- OpenAI's data policy: https://openai.com/policies/privacy-policy

## Examples of GPT Output

### Deal Insights Example
**Input:** Search for "moisturizer", 4 deals found
**GPT Output:** "Best deal is Target at $11.99, saving you $2 compared to average. Amazon offers fast shipping at $12.99, while CVS has it at $13.49. Great options across the board!"

### Product Recommendation Example
**Input:** CeraVe Moisturizer, score 85, user has oily skin with acne concerns
**GPT Output:** "Perfect for oily, acne-prone skin! This gentle moisturizer contains niacinamide to control oil and ceramides to strengthen your skin barrier without clogging pores. It's fragrance-free, which means it won't irritate breakout-prone skin."

## Future Enhancements

Possible additions (not implemented yet):
- Conversational chatbot for skincare questions
- Ingredient analysis and education
- Routine builder with GPT guidance
- Comparison explanations ("Why product A vs B?")

## Support

If you encounter issues:
1. Check this guide first
2. Run `python test_gpt.py` to diagnose
3. Check OpenAI API status: https://status.openai.com/
4. Review application logs for errors

---

**Enjoy your GPT-enhanced shopping experience!** ✨
