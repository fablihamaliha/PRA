# Quick Start Guide - Product Deal Finder

Get your e-commerce deal finder running in 5 minutes!

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- At least one retailer API key (see below)

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup_deal_finder.sh

# Edit .env file with your API keys
nano .env

# Start the application
cd pra
python app.py
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Run the application
cd pra
python app.py
```

## Getting API Keys (Free Tier)

### 1. Google Custom Search API (5 minutes)
**Cost:** Free (100 searches/day)

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "Custom Search API"
4. Create API Key under Credentials
5. Go to https://programmablesearchengine.google.com/
6. Create a new search engine
7. Copy the Search Engine ID (CX)

Add to `.env`:
```
GOOGLE_API_KEY=your-api-key-here
GOOGLE_CUSTOM_SEARCH_CX=your-cx-id-here
```

### 2. Walmart Open API (3 minutes)
**Cost:** Free (5,000 calls/day)

1. Go to https://developer.walmart.com/
2. Sign up for an account
3. Create a new application
4. Copy your API Key

Add to `.env`:
```
WALMART_API_KEY=your-walmart-key-here
```

### 3. Best Buy API (3 minutes)
**Cost:** Free (50,000 calls/day, 5/second)

1. Go to https://developer.bestbuy.com/
2. Sign up and create API key
3. Copy your API Key

Add to `.env`:
```
BEST_BUY_API_KEY=your-bestbuy-key-here
```

## Test the Application

### 1. Start the Server
```bash
cd pra
python app.py
```

You should see:
```
============================================================
🚀 PRRA Server Starting...
============================================================
📍 Main App: http://localhost:5001
🔐 Auth Page: http://localhost:5001/auth
💰 Deals Finder: http://localhost:5001/deals
============================================================
```

### 2. Open in Browser
Navigate to: `http://localhost:5001/deals`

### 3. Try a Search
- Enter "iPhone 15" or "Nike Air Max"
- Click "Search Deals"
- Watch as it searches across retailers
- Click any "Buy here" button to go to the retailer's site

## API Configuration Status

Check which APIs are configured:
```bash
curl http://localhost:5001/deals/api/health
```

Response shows which services are active:
```json
{
  "success": true,
  "message": "Deals API is running",
  "services": {
    "google_shopping": true,
    "walmart": true,
    "best_buy": true,
    "target": false,
    "amazon": false
  }
}
```

## Common Issues

### "No deals found"
✅ **Solution:**
- Ensure at least one API key is configured
- Check API quotas haven't been exceeded
- Try a different product name

### Location not detected
✅ **Solution:**
- Localhost IPs can't be geolocated
- Uncheck "Use my location" for testing
- Will work properly when deployed with public IP

### API Rate Limit Exceeded
✅ **Solution:**
- Wait for quota reset (usually 24 hours)
- Add more API keys to distribute load
- Implement caching (already included, 30-min cache)

## Project Structure

```
pra/
├── app.py                          # Main Flask application
├── blueprints/
│   └── deals.py                    # Deals API endpoints
├── services/
│   └── deal_finder_service.py      # Retailer API integration
├── templates/
│   └── deal_finder.html            # Frontend interface
├── static/
│   └── css/
│       └── deal_finder.css         # Styling
└── config.py                       # Configuration
```

## Next Steps

### For Development
1. Review [DEAL_FINDER_README.md](DEAL_FINDER_README.md) for detailed documentation
2. Customize the UI in `deal_finder.css`
3. Add more retailers in `deal_finder_service.py`
4. Implement user authentication
5. Add product tracking and price alerts

### For Production
1. Set up PostgreSQL database
2. Configure Redis for caching
3. Set up HTTPS with SSL certificate
4. Configure environment variables on server
5. Set up monitoring and logging
6. Implement rate limiting
7. Add analytics tracking

## Testing the APIs

### Manual API Test
```bash
# Search for a product
curl -X POST http://localhost:5001/deals/api/search \
  -H "Content-Type: application/json" \
  -d '{"product_name": "iPhone 15", "use_location": false}'

# Get location info
curl http://localhost:5001/deals/api/location
```

## Features Checklist

- ✅ Multi-retailer price comparison
- ✅ Real-time API integration
- ✅ Location-based deals
- ✅ Mobile-responsive design
- ✅ Direct retailer links (opens in new tab)
- ✅ Loading states with progress
- ✅ Error handling
- ✅ Price sorting (cheapest first)
- ✅ Product images
- ✅ Ratings and reviews
- ✅ Shipping information
- ✅ Sale badges
- ✅ 30-minute caching

## Support

Need help? Check:
1. [DEAL_FINDER_README.md](DEAL_FINDER_README.md) - Full documentation
2. Application logs in the terminal
3. Browser developer console (F12)
4. Individual retailer API documentation

## Quick Commands

```bash
# Start application
cd pra && python app.py

# Stop application
Ctrl + C

# Activate virtual environment
source .venv/bin/activate

# Deactivate virtual environment
deactivate

# Install new dependencies
pip install package-name
pip freeze > requirements.txt

# Clear cache (restart server)
# Cache automatically expires after 30 minutes
```

---

**Ready to go?** Start the server and visit http://localhost:5001/deals to find the best deals! 🎉
