import logging
from typing import Dict, Any, List
from datetime import datetime

from services.external_api import ExternalAPIService
from services.scoring import ScoringService
from config import Config

logger = logging.getLogger(__name__)


class RecommenderService:
    """
    Main recommendation service that orchestrates product fetching, scoring, and ranking
    """

    def __init__(self):
        self.config = Config()
        self.api_service = ExternalAPIService()
        self.scoring_service = ScoringService()
        self.max_recommendations = self.config.MAX_RECOMMENDATIONS

    def get_recommendations(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate product recommendations based on user profile

        Args:
            profile: User skin profile dictionary

        Returns:
            List of recommended products with scores and reasons
        """
        logger.info("Generating recommendations")

        # Step 1: Fetch products from external APIs
        raw_products = self._fetch_all_products(profile)

        if not raw_products:
            logger.warning("No products found from external APIs")
            return []

        # Step 2: Normalize products
        normalized_products = self._normalize_all_products(raw_products)

        # Step 3: Filter by budget
        filtered_products = self._filter_by_budget(normalized_products, profile)

        # Step 4: Score products
        scored_products = self._score_all_products(filtered_products, profile)

        # Step 5: Sort by score
        scored_products.sort(key=lambda x: x['score'], reverse=True)

        # Step 6: Get top N recommendations
        top_recommendations = scored_products[:self.max_recommendations]

        # Step 7: Save/update products in database
        self._save_products(top_recommendations)

        # Step 8: Format recommendations
        formatted_recommendations = self._format_recommendations(top_recommendations)

        logger.info(f"Generated {len(formatted_recommendations)} recommendations")

        return formatted_recommendations

    def _fetch_all_products(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch products from all available APIs"""
        all_products = []

        filters = {
            'skin_type': profile.get('skin_type'),
            'concerns': profile.get('concerns', []),
            'budget_min': profile.get('budget_min'),
            'budget_max': profile.get('budget_max')
        }

        # Fetch from Sephora
        try:
            sephora_products = self.api_service.fetch_sephora_products(filters)
            all_products.extend([{'source': 'sephora', 'data': p} for p in sephora_products])
        except Exception as e:
            logger.error(f"Error fetching Sephora products: {str(e)}")

        # Fetch from Amazon
        try:
            amazon_products = self.api_service.fetch_amazon_products(filters)
            all_products.extend([{'source': 'amazon', 'data': p} for p in amazon_products])
        except Exception as e:
            logger.error(f"Error fetching Amazon products: {str(e)}")

        return all_products

    def _normalize_all_products(self, raw_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize all products to standard format"""
        normalized = []

        for item in raw_products:
            source = item['source']
            product_data = item['data']

            try:
                normalized_product = self.api_service.normalize_products([product_data], source)[0]
                normalized.append(normalized_product)
            except Exception as e:
                logger.error(f"Error normalizing product: {str(e)}")
                continue

        return normalized

    def _filter_by_budget(self, products: List[Dict[str, Any]], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter products by budget range"""
        budget_min = profile.get('budget_min')
        budget_max = profile.get('budget_max')

        if budget_min is None and budget_max is None:
            return products

        filtered = []
        for product in products:
            price = product.get('price')

            if price is None:
                continue

            if budget_min is not None and price < budget_min:
                continue

            if budget_max is not None and price > budget_max:
                continue

            filtered.append(product)

        return filtered

    def _score_all_products(self, products: List[Dict[str, Any]], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score all products"""
        scored = []

        for product in products:
            try:
                score = self.scoring_service.score_product(product, profile)
                reason = self.scoring_service.generate_reason(product, profile, score)

                product['score'] = score
                product['reason'] = reason

                scored.append(product)
            except Exception as e:
                logger.error(f"Error scoring product {product.get('name')}: {str(e)}")
                continue

        return scored

    def _save_products(self, products: List[Dict[str, Any]]) -> None:
        """Save or update products in database"""
        # Import here to avoid circular imports
        from models.db import db
        from models.product import Product

        for product_data in products:
            try:
                # Check if product exists
                existing_product = Product.query.filter_by(
                    source=product_data['source'],
                    external_id=product_data['external_id']
                ).first()

                if existing_product:
                    # Update existing product
                    existing_product.name = product_data['name']
                    existing_product.brand = product_data['brand']
                    existing_product.price = product_data['price']
                    existing_product.currency = product_data['currency']
                    existing_product.url = product_data['url']
                    existing_product.image_url = product_data['image_url']
                    existing_product.skin_types = product_data['skin_types']
                    existing_product.tags = product_data['tags']
                    existing_product.ingredients = product_data['ingredients']
                    existing_product.rating = product_data['rating']
                    existing_product.num_reviews = product_data['num_reviews']
                    existing_product.last_seen_at = datetime.utcnow()

                    product_data['product_id'] = existing_product.id
                else:
                    # Create new product
                    # In _save_products method, update product creation:

                    new_product = Product(
                        external_id=product_data['external_id'],
                        name=product_data['name'],
                        brand=product_data['brand'],
                        price=product_data['price'],
                        currency=product_data['currency'],
                        url=product_data['url'],
                        image_url=product_data['image_url'],
                        source=product_data['source'],
                        rating=product_data['rating'],
                        num_reviews=product_data['num_reviews']
                    )
                    new_product.skin_types_list = product_data['skin_types']
                    new_product.tags_list = product_data['tags']
                    new_product.ingredients_list = product_data['ingredients']
                    db.session.add(new_product)
                    db.session.flush()

                    product_data['product_id'] = new_product.id

                db.session.commit()

            except Exception as e:
                logger.error(f"Error saving product: {str(e)}")
                db.session.rollback()
                continue

    def _format_recommendations(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format recommendations for API response"""
        formatted = []

        for product in products:
            formatted.append({
                'product_id': product.get('product_id'),
                'name': product['name'],
                'brand': product['brand'],
                'price': product['price'],
                'currency': product['currency'],
                'url': product['url'],
                'image_url': product['image_url'],
                'score': product['score'],
                'reason': product['reason']
            })

        return formatted