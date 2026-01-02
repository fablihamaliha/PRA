import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
# Removed unused imports: ThreadPoolExecutor, as_completed, json

from services.gpt_service import GPTService

logger = logging.getLogger(__name__)


class DealFinderService:
    """
    Service for fetching product deals from multiple retail APIs
    Integrates with Google Shopping, Walmart, Target, Amazon, and other retailers
    """

    def __init__(self):
        # Only RapidAPI is active - other APIs commented out
        self.rapidapi_key = os.environ.get('RAPIDAPI_KEY', '')
        self.rapidapi_search_url = "https://real-time-product-search.p.rapidapi.com/search-v2"

        # GPT service for enhanced insights
        self.gpt_service = GPTService()

        # Cache settings
        self.cache = {}
        self.cache_ttl = timedelta(minutes=30)

        # COMMENTED OUT - Other API integrations not in use
        # self.google_api_key = os.environ.get('GOOGLE_API_KEY', '')
        # self.google_cx = os.environ.get('GOOGLE_CUSTOM_SEARCH_CX', '')
        # self.walmart_api_key = os.environ.get('WALMART_API_KEY', '')
        # self.target_api_key = os.environ.get('TARGET_API_KEY', '')
        # self.amazon_api_key = os.environ.get('AMAZON_API_KEY', '')
        # self.best_buy_api_key = os.environ.get('BEST_BUY_API_KEY', '')

    def search_deals(
        self,
        product_name: str,
        location: Optional[Dict[str, Any]] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for deals across multiple retailers

        Args:
            product_name: Name of the product to search
            location: User location dict with 'latitude', 'longitude', 'zip_code'
            max_results: Maximum number of results per source

        Returns:
            Dictionary containing deals from all sources
        """
        logger.info(f"Searching deals for: {product_name}")

        # Check cache
        cache_key = f"{product_name}_{location.get('zip_code') if location else 'global'}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.info("Returning cached results")
                return cached_data

        # Fetch from RapidAPI only (other sources commented out)
        deals = {
            'product_name': product_name,
            'location': location,
            'sources': [],
            'total_deals': 0,
            'best_deal': None,
            'timestamp': datetime.now().isoformat()
        }

        # Only using RapidAPI - fetches from multiple retailers (Amazon, Walmart, eBay, etc.)
        try:
            rapidapi_results = self._fetch_rapidapi_products(product_name, location, max_results)
            if rapidapi_results:
                deals['sources'].append({
                    'name': 'rapidapi',
                    'count': len(rapidapi_results),
                    'status': 'success'
                })
                all_deals = rapidapi_results
            else:
                deals['sources'].append({
                    'name': 'rapidapi',
                    'count': 0,
                    'status': 'no_results'
                })
                all_deals = []
        except Exception as e:
            logger.error(f"Error fetching from RapidAPI: {str(e)}")
            deals['sources'].append({
                'name': 'rapidapi',
                'count': 0,
                'status': 'error',
                'error': str(e)
            })
            all_deals = []

        # COMMENTED OUT - Other API sources
        # with ThreadPoolExecutor(max_workers=6) as executor:
        #     futures = {
        #         executor.submit(self._fetch_google_shopping, product_name, location, max_results): 'google_shopping',
        #         executor.submit(self._fetch_walmart, product_name, location, max_results): 'walmart',
        #         executor.submit(self._fetch_target, product_name, location, max_results): 'target',
        #         executor.submit(self._fetch_best_buy, product_name, location, max_results): 'best_buy',
        #         executor.submit(self._fetch_amazon_affiliate, product_name, location, max_results): 'amazon',
        #     }

        # Sort by price and prepare results
        all_deals.sort(key=lambda x: x.get('price', float('inf')))
        deals['total_deals'] = len(all_deals)

        if all_deals:
            deals['best_deal'] = all_deals[0]
            deals['all_deals'] = all_deals

            # Generate GPT insights about the deals
            if self.gpt_service.is_available():
                try:
                    insights = self.gpt_service.generate_deal_insights(
                        product_name,
                        all_deals
                    )
                    if insights:
                        deals['gpt_insights'] = insights
                        logger.info("Added GPT insights to deals")
                except Exception as e:
                    logger.error(f"Error generating GPT insights: {str(e)}")
        else:
            deals['all_deals'] = []

        # Cache results
        self.cache[cache_key] = (deals, datetime.now())

        return deals

    # COMMENTED OUT - Google Shopping API not in use
    # def _fetch_google_shopping(
    #     self,
    #     product_name: str,
    #     location: Optional[Dict[str, Any]],
    #     max_results: int
    # ) -> List[Dict[str, Any]]:
    #     """Fetch deals from Google Shopping API"""
    #     return []

    # COMMENTED OUT - Walmart API not in use
    # def _fetch_walmart(...): return []

    # COMMENTED OUT - Target API not in use
    # def _fetch_target(...): return []

    # COMMENTED OUT - Best Buy API not in use
    # def _fetch_best_buy(...): return []

    # COMMENTED OUT - Amazon Affiliate API not in use
    # def _fetch_amazon_affiliate(...): return []

    def _fetch_rapidapi_products(
        self,
        product_name: str,
        location: Optional[Dict[str, Any]],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch deals from multiple retailers using RapidAPI Real-Time Product Search API
        Searches across Amazon, Walmart, eBay, and other retailers
        Free tier: 100 requests/month
        """
        if not self.rapidapi_key:
            logger.warning("RapidAPI key not configured")
            return []

        try:
            # Search for products using the /search endpoint
            params = {
                'q': product_name,
                'country': 'us',
                'language': 'en',
                'limit': str(max_results)
            }

            headers = {
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': 'real-time-product-search.p.rapidapi.com'
            }

            response = requests.get(
                self.rapidapi_search_url,
                params=params,
                headers=headers,
                timeout=15
            )

            if response.status_code != 200:
                logger.error(f"RapidAPI Product Search error: {response.status_code} - {response.text}")
                return []

            data = response.json()
            deals = []

            # RapidAPI returns products in 'data.products' array
            products = data.get('data', {}).get('products', [])

            for item in products[:max_results]:
                deal = self._normalize_rapidapi_product(item)
                if deal:
                    deals.append(deal)

            logger.info(f"Fetched {len(deals)} deals from RapidAPI Product Search")
            return deals

        except Exception as e:
            logger.error(f"RapidAPI Product Search error: {str(e)}")
            return []

    # COMMENTED OUT - Google Shopping normalization not in use
    # def _normalize_google_product(self, item: Dict[str, Any], product_name: str) -> Optional[Dict[str, Any]]:
    #     """Normalize Google Shopping product data"""
    #     try:
    #         # Extract data from Google Custom Search result
    #         link = item.get('link', '')
    #
    #         # Determine seller from URL
    #         seller = 'Unknown'
    #         if 'walmart.com' in link:
    #             seller = 'Walmart'
    #         elif 'amazon.com' in link:
    #             seller = 'Amazon'
    #         elif 'target.com' in link:
    #             seller = 'Target'
    #         elif 'bestbuy.com' in link:
    #             seller = 'Best Buy'
    #
    #         return {
    #             'product_name': item.get('title', product_name),
    #             'seller': seller,
    #             'price': 0.0,  # Google CSE doesn't provide prices
    #             'url': link,
    #             'image_url': item.get('link', ''),
    #             'source': 'google_shopping',
    #             'rating': None,
    #             'reviews': 0,
    #             'shipping': 'Check website',
    #             'in_stock': True,
    #             'description': item.get('snippet', '')
    #         }
    #     except Exception as e:
    #         logger.error(f"Error normalizing Google product: {str(e)}")
    #         return None

    # COMMENTED OUT - Walmart normalization not in use
    # def _normalize_walmart_product(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    #     """Normalize Walmart product data"""
    #     try:
    #         return {
    #             'product_name': item.get('name', ''),
    #             'seller': 'Walmart',
    #             'price': float(item.get('salePrice', 0)),
    #             'original_price': float(item.get('msrp', item.get('salePrice', 0))),
    #             'url': item.get('productUrl', ''),
    #             'image_url': item.get('mediumImage', item.get('thumbnailImage', '')),
    #             'source': 'walmart',
    #             'rating': float(item.get('customerRating', 0)),
    #             'reviews': int(item.get('numReviews', 0)),
    #             'shipping': 'Free 2-day shipping' if item.get('availableOnline') else 'Check availability',
    #             'in_stock': item.get('availableOnline', False),
    #             'description': item.get('shortDescription', '')
    #         }
    #     except Exception as e:
    #         logger.error(f"Error normalizing Walmart product: {str(e)}")
    #         return None

    # COMMENTED OUT - Target normalization not in use
    # def _normalize_target_product(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    #     """Normalize Target product data"""
    #     try:
    #         price_data = item.get('price', {})
    #         return {
    #             'product_name': item.get('title', ''),
    #             'seller': 'Target',
    #             'price': float(price_data.get('current_retail', 0)),
    #             'original_price': float(price_data.get('reg_retail', price_data.get('current_retail', 0))),
    #             'url': f"https://www.target.com{item.get('url', '')}",
    #             'image_url': item.get('images', [{}])[0].get('base_url', ''),
    #             'source': 'target',
    #             'rating': float(item.get('ratings', {}).get('average', 0)),
    #             'reviews': int(item.get('ratings', {}).get('count', 0)),
    #             'shipping': 'Free on $35+',
    #             'in_stock': item.get('available', False),
    #             'description': item.get('description', '')
    #         }
    #     except Exception as e:
    #         logger.error(f"Error normalizing Target product: {str(e)}")
    #         return None

    # COMMENTED OUT - Best Buy normalization not in use
    # def _normalize_bestbuy_product(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    #     """Normalize Best Buy product data"""
    #     try:
    #         sale_price = float(item.get('salePrice', item.get('regularPrice', 0)))
    #         regular_price = float(item.get('regularPrice', sale_price))
    #
    #         return {
    #             'product_name': item.get('name', ''),
    #             'seller': 'Best Buy',
    #             'price': sale_price,
    #             'original_price': regular_price,
    #             'url': item.get('url', ''),
    #             'image_url': item.get('image', ''),
    #             'source': 'bestbuy',
    #             'rating': float(item.get('customerReviewAverage', 0)),
    #             'reviews': int(item.get('customerReviewCount', 0)),
    #             'shipping': 'Free' if sale_price > 35 else 'Standard shipping',
    #             'in_stock': item.get('onSale', True),
    #             'description': item.get('shortDescription', ''),
    #             'on_sale': item.get('onSale', False)
    #         }
    #     except Exception as e:
    #         logger.error(f"Error normalizing Best Buy product: {str(e)}")
    #         return None

    def _normalize_rapidapi_product(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize RapidAPI Product Search data (multi-retailer from Google Shopping)"""
        try:
            # Get offer (contains price and store info)
            offer = item.get('offer', {})
            if not offer:
                # Skip products without offers
                return None

            # Extract price from offer
            price_str = offer.get('price', '0')
            if isinstance(price_str, str):
                price = float(price_str.replace('$', '').replace(',', '').strip()) if price_str else 0.0
            else:
                price = float(price_str) if price_str else 0.0

            # Original price if on sale
            original_price_str = offer.get('original_price', '')
            if original_price_str:
                original_price = float(original_price_str.replace('$', '').replace(',', '').strip())
            else:
                original_price = price

            # Extract store/seller from offer
            store_name = offer.get('store_name', 'Unknown')

            # Rating (from product, not offer)
            rating = item.get('product_rating', 0) or 0
            if rating and isinstance(rating, (int, float)):
                rating = float(rating)
            else:
                rating = 0.0

            # Reviews
            reviews = item.get('product_num_reviews', 0) or 0
            if isinstance(reviews, str):
                reviews = int(reviews.replace(',', '')) if reviews else 0
            else:
                reviews = int(reviews) if reviews else 0

            # Product photos (array)
            photos = item.get('product_photos', [])
            image_url = photos[0] if photos else ''

            return {
                'product_name': item.get('product_title', ''),
                'seller': store_name,
                'price': price,
                'original_price': original_price,
                'url': offer.get('offer_page_url', item.get('product_page_url', '')),
                'image_url': image_url,
                'source': 'rapidapi',
                'rating': rating,
                'reviews': reviews,
                'shipping': offer.get('shipping', 'Check website'),
                'in_stock': True,  # Assume in stock if returned by API
                'description': item.get('product_description', ''),
                'on_sale': offer.get('on_sale', False)
            }
        except Exception as e:
            logger.error(f"Error normalizing RapidAPI product: {str(e)}")
            return None

    def get_user_location(self, ip_address: str) -> Dict[str, Any]:
        """
        Get user location from IP address using ipapi.co
        Free tier: 1000 requests/day
        """
        try:
            response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country_name'),
                    'zip_code': data.get('postal'),
                    'timezone': data.get('timezone')
                }
        except Exception as e:
            logger.error(f"Error getting location: {str(e)}")

        return None
