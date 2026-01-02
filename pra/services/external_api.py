import requests
import logging
from typing import List, Dict, Any
from config import Config

logger = logging.getLogger(__name__)


class ExternalAPIService:
    """
    Service for fetching products from external APIs
    """

    def __init__(self):
        self.config = Config()

    def fetch_sephora_products(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch products from Sephora API

        Args:
            filters: Dictionary containing skin_type, concerns, budget, etc.

        Returns:
            List of product dictionaries
        """
        logger.info("Fetching products from Sephora API")

        # Placeholder implementation
        # In production, this would make actual API calls to Sephora

        # Example API call structure:
        # url = "https://api.sephora.com/v1/products"
        # headers = {
        #     'Authorization': f'Bearer {self.config.SEPHORA_API_KEY}',
        #     'Content-Type': 'application/json'
        # }
        # params = {
        #     'skin_type': filters.get('skin_type'),
        #     'concerns': ','.join(filters.get('concerns', [])),
        #     'price_min': filters.get('budget_min'),
        #     'price_max': filters.get('budget_max')
        # }
        # response = requests.get(url, headers=headers, params=params)
        # return response.json()['products']

        # Mock data for demonstration
        return self._get_mock_sephora_products()

    def fetch_amazon_products(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch products from Amazon Product Advertising API

        Args:
            filters: Dictionary containing skin_type, concerns, budget, etc.

        Returns:
            List of product dictionaries
        """
        logger.info("Fetching products from Amazon API")

        # Placeholder implementation
        # In production, use Amazon Product Advertising API

        # Mock data for demonstration
        return self._get_mock_amazon_products()

    def fetch_ulta_products(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch products from Ulta API
        """
        logger.info("Fetching products from Ulta API")
        return []

    def normalize_products(self, raw_products: List[Dict[str, Any]], source: str) -> List[Dict[str, Any]]:
        """
        Normalize products from different sources to a standard format

        Args:
            raw_products: Raw product data from API
            source: Source name ('sephora', 'amazon', etc.)

        Returns:
            List of normalized product dictionaries
        """
        normalized = []

        for product in raw_products:
            try:
                if source == 'sephora':
                    normalized_product = self._normalize_sephora_product(product)
                elif source == 'amazon':
                    normalized_product = self._normalize_amazon_product(product)
                else:
                    normalized_product = self._normalize_generic_product(product, source)

                normalized.append(normalized_product)
            except Exception as e:
                logger.error(f"Error normalizing product from {source}: {str(e)}")
                continue

        return normalized

    def _normalize_sephora_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Sephora product format"""
        return {
            'external_id': product.get('id'),
            'name': product.get('name'),
            'brand': product.get('brand'),
            'price': product.get('price'),
            'currency': 'USD',
            'url': product.get('url'),
            'image_url': product.get('image_url'),
            'source': 'sephora',
            'skin_types': product.get('skin_types', []),
            'tags': product.get('tags', []),
            'ingredients': product.get('ingredients', []),
            'rating': product.get('rating'),
            'num_reviews': product.get('num_reviews', 0)
        }

    def _normalize_amazon_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Amazon product format"""
        return {
            'external_id': product.get('asin'),
            'name': product.get('title'),
            'brand': product.get('brand'),
            'price': product.get('price'),
            'currency': 'USD',
            'url': product.get('detail_url'),
            'image_url': product.get('image_url'),
            'source': 'amazon',
            'skin_types': product.get('skin_types', []),
            'tags': product.get('categories', []),
            'ingredients': product.get('ingredients', []),
            'rating': product.get('rating'),
            'num_reviews': product.get('reviews_count', 0)
        }

    def _normalize_generic_product(self, product: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Normalize generic product format"""
        return {
            'external_id': product.get('id'),
            'name': product.get('name'),
            'brand': product.get('brand'),
            'price': product.get('price'),
            'currency': product.get('currency', 'USD'),
            'url': product.get('url'),
            'image_url': product.get('image_url'),
            'source': source,
            'skin_types': product.get('skin_types', []),
            'tags': product.get('tags', []),
            'ingredients': product.get('ingredients', []),
            'rating': product.get('rating'),
            'num_reviews': product.get('num_reviews', 0)
        }

    def _get_mock_sephora_products(self) -> List[Dict[str, Any]]:
        """Mock Sephora products for demonstration"""
        return [
            {
                'id': 'SEP001',
                'name': 'CeraVe Foaming Facial Cleanser',
                'brand': 'CeraVe',
                'price': 14.99,
                'url': 'https://www.sephora.com/product/foaming-facial-cleanser',
                'image_url': 'https://example.com/cerave-cleanser.jpg',
                'skin_types': ['oily', 'combination', 'normal'],
                'tags': ['cleanser', 'daily-use', 'fragrance-free'],
                'ingredients': ['niacinamide', 'hyaluronic acid', 'ceramides'],
                'rating': 4.5,
                'num_reviews': 1250
            },
            {
                'id': 'SEP002',
                'name': 'The Ordinary Niacinamide 10% + Zinc 1%',
                'brand': 'The Ordinary',
                'price': 5.90,
                'url': 'https://www.sephora.com/product/niacinamide-zinc',
                'image_url': 'https://example.com/ordinary-niacinamide.jpg',
                'skin_types': ['oily', 'combination'],
                'tags': ['serum', 'acne', 'pore-minimizing'],
                'ingredients': ['niacinamide', 'zinc'],
                'rating': 4.3,
                'num_reviews': 2100
            },
            {
                'id': 'SEP003',
                'name': 'La Roche-Posay Effaclar Duo',
                'brand': 'La Roche-Posay',
                'price': 19.99,
                'url': 'https://www.sephora.com/product/effaclar-duo',
                'image_url': 'https://example.com/lrp-effaclar.jpg',
                'skin_types': ['oily', 'acne-prone'],
                'tags': ['moisturizer', 'acne-treatment'],
                'ingredients': ['benzoyl peroxide', 'niacinamide'],
                'rating': 4.6,
                'num_reviews': 890
            }
        ]

    def _get_mock_amazon_products(self) -> List[Dict[str, Any]]:
        """Mock Amazon products for demonstration"""
        return [
            {
                'asin': 'AMZ001',
                'title': 'Neutrogena Oil-Free Acne Wash',
                'brand': 'Neutrogena',
                'price': 8.99,
                'detail_url': 'https://www.amazon.com/dp/AMZ001',
                'image_url': 'https://example.com/neutrogena-wash.jpg',
                'skin_types': ['oily', 'acne-prone'],
                'categories': ['cleanser', 'acne'],
                'ingredients': ['salicylic acid'],
                'rating': 4.4,
                'reviews_count': 3500
            },
            {
                'asin': 'AMZ002',
                'title': 'Paula\'s Choice 2% BHA Liquid Exfoliant',
                'brand': 'Paula\'s Choice',
                'price': 32.00,
                'detail_url': 'https://www.amazon.com/dp/AMZ002',
                'image_url': 'https://example.com/paulas-choice.jpg',
                'skin_types': ['all'],
                'categories': ['exfoliant', 'toner'],
                'ingredients': ['salicylic acid', 'green tea'],
                'rating': 4.7,
                'reviews_count': 5200
            }
        ]