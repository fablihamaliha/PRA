# Product Deal Finder - E-Commerce Platform

A production-ready product deal finder that searches across multiple retailers (Google Shopping, Walmart, Target, Best Buy, Amazon) to find the best prices for products. Features location-based deals, real-time price comparison, and direct retailer links.

## Features

### Core Functionality
- **Multi-Retailer Search**: Integrates with Google Shopping, Walmart, Target, Best Buy, and Amazon APIs
- **Real-Time Price Comparison**: Fetches live prices from multiple sources concurrently
- **Location-Based Deals**: Uses IP geolocation to show local deals and availability
- **Direct Purchase Links**: Clicking "Buy" takes users directly to the retailer's product page in a new tab
- **Smart Caching**: 30-minute cache to reduce API calls and improve performance
- **Responsive Design**: Mobile-first design that works on all devices

### User Experience
- **Clean Modern UI**: Gradient hero, rounded cards, subtle shadows, accessible typography
- **Loading States**: Real-time progress showing which retailers have been checked
- **Error Handling**: Graceful error states with retry functionality
- **Empty State**: Helpful guidance with example searches
- **Best Deal Highlighting**: Top deal prominently displayed with savings calculation
- **Alternative Offers**: Grid view of other available deals sorted by price

## Architecture

### Backend Services

#### 1. Deal Finder Service (`services/deal_finder_service.py`)
- Handles API integration with multiple retailers
- Concurrent API calls using ThreadPoolExecutor for fast response times
- Data normalization across different API formats
- Caching layer for improved performance
- IP-based geolocation service

#### 2. Flask Blueprint (`blueprints/deals.py`)
- RESTful API endpoints:
  - `POST /deals/api/search` - Search for product deals
  - `GET /deals/api/location` - Get user location from IP
  - `GET /deals/api/health` - Health check for API services

### Frontend

#### Components
1. **Search Interface** - Hero section with prominent search bar
2. **Loading State** - Animated spinner with source status badges
3. **Results Display** - Best deal card + alternative offers grid
4. **Error Handling** - User-friendly error messages with retry

## Setup Instructions

### 1. Install Dependencies

```bash
pip install flask flask-cors requests
```

### 2. Configure API Keys

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required for Google Shopping
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CUSTOM_SEARCH_CX=your-custom-search-engine-id

# Required for Walmart
WALMART_API_KEY=your-walmart-api-key

# Required for Best Buy
BEST_BUY_API_KEY=your-bestbuy-api-key

# Optional - requires partnership
TARGET_API_KEY=your-target-api-key
AMAZON_API_KEY=your-amazon-api-key
```

### 3. Getting API Keys

#### Google Custom Search API (Google Shopping)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Custom Search API"
4. Create credentials (API Key)
5. Create a Custom Search Engine at [Programmable Search Engine](https://programmablesearchengine.google.com/)
6. Get your Search Engine ID (CX)

#### Walmart Open API
1. Register at [Walmart Developer Portal](https://developer.walmart.com/)
2. Create an application
3. Get your API key from the dashboard

#### Best Buy API
1. Register at [Best Buy Developer Portal](https://developer.bestbuy.com/)
2. Create an API key
3. Review rate limits (5 requests/second, 50,000/day for free tier)

#### Target RedCircle API
1. Apply for partnership at [Target Partners](https://partners.target.com/)
2. Requires business verification
3. Not required for basic functionality

#### Amazon Product Advertising API
1. Join [Amazon Associates Program](https://affiliate-program.amazon.com/)
2. Apply for Product Advertising API access
3. Requires active affiliate account with qualifying sales

### 4. Run the Application

```bash
cd pra
python app.py
```

The server will start on `http://localhost:5001`

Access the deal finder at: `http://localhost:5001/deals`

## API Integration Details

### Data Flow

1. **User Search** → Frontend sends product name + location preference
2. **Backend Processing**:
   - Gets user location from IP (if enabled)
   - Makes concurrent API calls to all configured retailers
   - Normalizes data from different API formats
   - Sorts results by price
   - Caches results for 30 minutes
3. **Response** → Returns structured deal data with best deal highlighted
4. **User Click** → Opens retailer's product page in new tab

### API Response Format

```json
{
  "success": true,
  "data": {
    "product_name": "iPhone 15",
    "location": {
      "city": "New York",
      "region": "New York",
      "zip_code": "10001"
    },
    "total_deals": 5,
    "best_deal": {
      "product_name": "iPhone 15 Pro 256GB",
      "seller": "Best Buy",
      "price": 999.99,
      "original_price": 1099.99,
      "url": "https://www.bestbuy.com/...",
      "image_url": "https://...",
      "rating": 4.8,
      "reviews": 12345,
      "shipping": "Free",
      "in_stock": true
    },
    "all_deals": [...],
    "sources": [
      {"name": "google_shopping", "count": 10, "status": "success"},
      {"name": "walmart", "count": 5, "status": "success"},
      ...
    ]
  }
}
```

## Performance Optimization

### Backend
- **Concurrent API Calls**: Uses ThreadPoolExecutor to call all APIs in parallel
- **Caching**: 30-minute cache reduces redundant API calls
- **Timeout Management**: 10-second timeout per API call
- **Error Handling**: Graceful fallback when APIs fail

### Frontend
- **Lazy Loading**: Images load only when visible
- **Debouncing**: Prevents multiple rapid searches
- **Optimistic UI**: Shows loading states immediately
- **Fallback Images**: Placeholder images if product images fail

## Production Considerations

### Security
- Store API keys in environment variables (never commit to git)
- Use HTTPS in production
- Implement rate limiting on API endpoints
- Validate and sanitize user input

### Monitoring
- Log API response times and error rates
- Track which retailers have the most successful results
- Monitor cache hit rates
- Set up alerts for API failures

### Scaling
- Consider Redis for distributed caching
- Implement request queuing for high traffic
- Use CDN for static assets
- Database for search history and analytics

### Legal Compliance
- Review each retailer's API Terms of Service
- Respect rate limits and caching requirements
- Display proper attribution where required
- Don't cache prices beyond allowed timeframes

## Customization

### Adding New Retailers

1. Add API credentials to `config.py`
2. Create fetch method in `deal_finder_service.py`:
```python
def _fetch_new_retailer(self, product_name, location, max_results):
    # API integration code
    pass
```
3. Add normalization method:
```python
def _normalize_new_retailer_product(self, item):
    # Data normalization
    pass
```
4. Add to concurrent executor in `search_deals()`

### Styling
- Colors: Modify CSS variables in `:root`
- Layout: Adjust grid template in `.deals-grid`
- Typography: Update font-family in `body`

## Troubleshooting

### "No deals found"
- Check API keys are correctly configured
- Verify API quotas haven't been exceeded
- Check network connectivity
- Review API service status pages

### Location not working
- Localhost IPs (127.0.0.1) can't be geolocated
- Test with a public IP or disable location feature
- ipapi.co has rate limits (1000 requests/day free)

### Slow response times
- Check individual API response times in logs
- Some APIs may be slower than others
- Consider increasing timeout values
- Enable caching to reduce API calls

## Future Enhancements

- [ ] User accounts and saved searches
- [ ] Price tracking and alerts
- [ ] Product comparison feature
- [ ] Wishlist functionality
- [ ] Price history charts
- [ ] Email notifications for price drops
- [ ] Browser extension
- [ ] Mobile app (React Native)

## License

This is a production-ready e-commerce tool. Ensure compliance with all retailer API terms of service before deploying.

## Support

For issues or questions:
1. Check API documentation for each retailer
2. Review application logs
3. Verify environment configuration
4. Test individual API endpoints

---

Built with Flask, JavaScript, and modern CSS. Ready for production deployment.
