"""
Product Scraper Service
Scrapes skincare product data from various sources
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import os
import openai
import json

logger = logging.getLogger(__name__)


class ProductScraperService:
    """Service for scraping skincare product information"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')
        self.sephora_host = 'sephora.p.rapidapi.com'
        self.skincare_host = 'skincare-api.p.rapidapi.com'
        self.sephora_search_url = 'https://sephora.p.rapidapi.com/us/products/search'
        self.skincare_search_url = 'https://skincare-api.p.rapidapi.com/skincare'

    def search_products(
        self,
        category: str,
        search_terms: List[str],
        preferred_ingredients: List[str] = None,
        avoided_ingredients: List[str] = None,
        limit: int = 3,
        price_range: Optional[tuple] = None
    ) -> List[Dict]:
        """
        Search for products across multiple sources.

        Args:
            category: Product category (cleanser, toner, serum, etc.)
            search_terms: Terms to search for
            preferred_ingredients: Ingredients that should be present
            avoided_ingredients: Ingredients to exclude
            limit: Maximum number of products to return

        Returns:
            List of product dictionaries
        """
        products = []

        # Try multiple sources
        products.extend(self._search_sephora(category, search_terms, limit, price_range))
        products.extend(self._search_skincare_api(category, search_terms, limit, price_range))
        products.extend(self._search_ulta(category, search_terms, limit, price_range))

        # Filter by ingredients if specified
        if preferred_ingredients or avoided_ingredients:
            products = self._filter_by_ingredients(
                products, preferred_ingredients, avoided_ingredients
            )

        # Filter by price range if requested
        if price_range:
            min_price, max_price = price_range
            products = [
                p for p in products
                if min_price <= (p.get('price') or 0) <= max_price
            ]

        return products[:limit]

    def _search_sephora(
        self,
        category: str,
        search_terms: List[str],
        limit: int = 3,
        price_range: Optional[tuple] = None
    ) -> List[Dict]:
        """
        Scrape products from Sephora (simplified version).
        Note: This is a placeholder - real implementation would need to handle
        Sephora's actual HTML structure and potentially their API.
        """
        products = []

        try:
            search_query = " ".join(search_terms)
            logger.info(f"Searching Sephora for: {search_query}")

            if not self.rapidapi_key:
                logger.warning("RAPIDAPI_KEY not configured, skipping Sephora API")
                return products

            headers = {
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': self.sephora_host
            }
            params = {
                'q': search_query,
                'limit': limit
            }

            response = requests.get(
                self.sephora_search_url,
                headers=headers,
                params=params,
                timeout=12
            )
            response.raise_for_status()

            payload = response.json()
            items = payload.get('products') or payload.get('items') or payload.get('data') or payload.get('results') or []

            for item in items[:limit]:
                products.append({
                    "name": item.get('name') or item.get('displayName') or "Sephora Product",
                    "brand": item.get('brand') or item.get('brandName') or "Sephora",
                    "price": item.get('price') or item.get('currentSku', {}).get('listPrice') or 0,
                    "url": item.get('url') or item.get('productUrl'),
                    "image_url": item.get('imageUrl') or item.get('heroImage') or item.get('thumbnailUrl'),
                    "source": "sephora",
                    "ingredients": item.get('ingredients') or [],
                    "rating": item.get('rating') or item.get('ratingValue'),
                    "num_reviews": item.get('reviews') or item.get('totalReviews') or 0
                })

        except Exception as e:
            logger.error(f"Error searching Sephora API: {str(e)}")

        return products

    def _search_skincare_api(
        self,
        category: str,
        search_terms: List[str],
        limit: int = 3,
        price_range: Optional[tuple] = None
    ) -> List[Dict]:
        """Search skincare products via RapidAPI skincare endpoint."""
        products = []

        try:
            search_query = " ".join(search_terms)
            logger.info(f"Searching Skincare API for: {search_query}")

            if not self.rapidapi_key:
                logger.warning("RAPIDAPI_KEY not configured, skipping Skincare API")
                return products

            headers = {
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': self.skincare_host
            }
            params = {
                'q': search_query,
                'limit': limit
            }

            response = requests.get(
                self.skincare_search_url,
                headers=headers,
                params=params,
                timeout=12
            )
            response.raise_for_status()

            payload = response.json()
            items = payload.get('data') if isinstance(payload, dict) else payload
            items = items or []

            for item in items[:limit]:
                products.append({
                    "name": item.get('name') or item.get('title') or "Skincare Product",
                    "brand": item.get('brand') or "Skincare",
                    "price": item.get('price') or 0,
                    "url": item.get('url') or item.get('link'),
                    "image_url": item.get('image') or item.get('image_url'),
                    "source": "skincare-api",
                    "ingredients": item.get('ingredients') or [],
                    "rating": item.get('rating') or item.get('ratingValue'),
                    "num_reviews": item.get('reviews') or item.get('reviews_count') or 0
                })

        except Exception as e:
            logger.error(f"Error searching Skincare API: {str(e)}")

        return products

    def _search_ulta(
        self,
        category: str,
        search_terms: List[str],
        limit: int = 3,
        price_range: Optional[tuple] = None
    ) -> List[Dict]:
        """
        Scrape products from Ulta (simplified version).
        """
        products = []

        try:
            search_query = " ".join(search_terms)
            logger.info(f"Searching Ulta for: {search_query}")

            # Placeholder data
            price = 24.99
            if price_range:
                min_price, max_price = price_range
                price = round((min_price + max_price) / 2, 2)

            products.append({
                "name": f"{category.title()} Product",
                "brand": "Sample Brand",
                "price": price,
                "url": "https://www.ulta.com/product/sample",
                "image_url": "https://via.placeholder.com/150",
                "source": "ulta",
                "ingredients": [],
                "rating": 4.3,
                "num_reviews": 890
            })

        except Exception as e:
            logger.error(f"Error searching Ulta: {str(e)}")

        return products

    def _filter_by_ingredients(
        self,
        products: List[Dict],
        preferred_ingredients: Optional[List[str]],
        avoided_ingredients: Optional[List[str]]
    ) -> List[Dict]:
        """
        Filter products by ingredient preferences using GPT analysis.

        Args:
            products: List of product dictionaries
            preferred_ingredients: Ingredients that should be present
            avoided_ingredients: Ingredients to exclude

        Returns:
            Filtered list of products with match scores
        """
        if not self.openai_api_key:
            # Fallback to simple string matching
            return self._simple_ingredient_filter(products, preferred_ingredients, avoided_ingredients)

        filtered = []

        for product in products:
            ingredient_list = product.get('ingredients', [])

            if not ingredient_list:
                # If no ingredients listed, keep the product but with low confidence
                product['ingredient_match_score'] = 0.5
                product['ingredient_analysis'] = "No ingredient information available"
                filtered.append(product)
                continue

            # Use GPT to analyze ingredients
            analysis = self._analyze_ingredients_with_gpt(
                ingredient_list,
                preferred_ingredients,
                avoided_ingredients
            )

            # Filter out products with avoided ingredients
            if analysis.get('has_avoided', False):
                logger.info(f"Filtering out {product['name']} - contains avoided ingredients")
                continue

            # Add analysis to product
            product['ingredient_match_score'] = analysis.get('match_score', 0.5)
            product['ingredient_analysis'] = analysis.get('explanation', '')
            product['has_preferred'] = analysis.get('has_preferred', False)

            filtered.append(product)

        # Sort by match score (highest first)
        filtered.sort(key=lambda x: x.get('ingredient_match_score', 0), reverse=True)

        return filtered

    def _simple_ingredient_filter(
        self,
        products: List[Dict],
        preferred_ingredients: Optional[List[str]],
        avoided_ingredients: Optional[List[str]]
    ) -> List[Dict]:
        """
        Simple string-based ingredient filtering (fallback when GPT unavailable).
        """
        filtered = []

        for product in products:
            ingredients = [ing.lower() for ing in product.get('ingredients', [])]

            # Check avoided ingredients
            if avoided_ingredients:
                has_avoided = any(
                    avoided.lower() in ' '.join(ingredients)
                    for avoided in avoided_ingredients
                )
                if has_avoided:
                    continue

            # Check preferred ingredients (optional match)
            if preferred_ingredients:
                has_preferred = any(
                    preferred.lower() in ' '.join(ingredients)
                    for preferred in preferred_ingredients
                )
                product['has_preferred'] = has_preferred
                product['ingredient_match_score'] = 0.7 if has_preferred else 0.5
            else:
                product['ingredient_match_score'] = 0.5

            filtered.append(product)

        return filtered

    def _analyze_ingredients_with_gpt(
        self,
        ingredient_list: List[str],
        preferred_ingredients: Optional[List[str]],
        avoided_ingredients: Optional[List[str]]
    ) -> Dict:
        """
        Use GPT to intelligently analyze product ingredients.

        Args:
            ingredient_list: List of ingredients in the product
            preferred_ingredients: Ingredients user prefers
            avoided_ingredients: Ingredients user wants to avoid

        Returns:
            Dictionary with analysis results
        """
        try:
            ingredients_str = ", ".join(ingredient_list[:20])  # Limit to first 20 ingredients
            preferred_str = ", ".join(preferred_ingredients) if preferred_ingredients else "none"
            avoided_str = ", ".join(avoided_ingredients) if avoided_ingredients else "none"

            prompt = f"""
Analyze this skincare product's ingredient list:

Product Ingredients: {ingredients_str}
User Prefers: {preferred_str}
User Wants to Avoid: {avoided_str}

Please analyze:
1. Does this product contain any of the avoided ingredients (or similar compounds)?
2. Does it contain any of the preferred ingredients (or similar beneficial compounds)?
3. How well does this product match the user's preferences (0.0 to 1.0 score)?
4. Provide a brief explanation of why this product is/isn't a good match.

Consider chemical similarities (e.g., retinol, retinyl palmitate, and retinaldehyde are all retinoids).

Return your analysis in this JSON format:
{{
    "has_avoided": true/false,
    "has_preferred": true/false,
    "match_score": 0.0-1.0,
    "explanation": "Brief explanation of the match"
}}
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Using 3.5 for faster/cheaper analysis
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skincare ingredient expert. Analyze ingredients and provide JSON responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )

            analysis_text = response.choices[0].message.content
            analysis = json.loads(analysis_text)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing ingredients with GPT: {str(e)}")
            # Return neutral analysis on error
            return {
                "has_avoided": False,
                "has_preferred": False,
                "match_score": 0.5,
                "explanation": "Unable to analyze ingredients"
            }

    def find_product_alternatives(
        self,
        product_name: str,
        category: str,
        price_range: tuple = None
    ) -> List[Dict]:
        """
        Find alternatives for a specific product.

        Args:
            product_name: Name of the product to find alternatives for
            category: Product category
            price_range: (min_price, max_price) tuple

        Returns:
            List of alternative products
        """
        products = []

        try:
            search_terms = [category, product_name.split()[0]]  # Use brand name
            products = self.search_products(category, search_terms, limit=5)

            # Filter by price range if specified
            if price_range:
                min_price, max_price = price_range
                products = [
                    p for p in products
                    if min_price <= p.get('price', 0) <= max_price
                ]

        except Exception as e:
            logger.error(f"Error finding alternatives: {str(e)}")

        return products

    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific product.

        Args:
            product_url: URL of the product page

        Returns:
            Dictionary with product details or None
        """
        try:
            response = requests.get(product_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # This would be customized based on the website
            # Placeholder return
            return {
                "name": "Product Name",
                "brand": "Brand Name",
                "price": 0.0,
                "ingredients": [],
                "description": "",
                "url": product_url
            }

        except Exception as e:
            logger.error(f"Error getting product details: {str(e)}")
            return None
