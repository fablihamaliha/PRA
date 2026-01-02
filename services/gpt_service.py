import logging
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class GPTService:
    """
    Service for integrating OpenAI GPT to enhance product recommendations
    with natural language explanations and personalized advice
    """

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.client = None

        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("GPT service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        else:
            logger.warning("OPENAI_API_KEY not configured - GPT features will be disabled")

    def generate_skincare_advice(
        self,
        profile: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate personalized skincare advice based on user profile

        Args:
            profile: User skin profile with skin_type, concerns, preferences

        Returns:
            Personalized skincare advice as a string
        """
        if not self.client:
            logger.warning("GPT service not available")
            return None

        try:
            skin_type = profile.get('skin_type', 'unknown')
            concerns = profile.get('concerns', [])
            preferred_ingredients = profile.get('preferred_ingredients', [])
            avoided_ingredients = profile.get('avoided_ingredients', [])

            # Build context for GPT
            concerns_text = ", ".join(concerns) if concerns else "general skin health"
            preferred_text = ", ".join(preferred_ingredients) if preferred_ingredients else "none specified"
            avoided_text = ", ".join(avoided_ingredients) if avoided_ingredients else "none specified"

            prompt = f"""You are a skincare expert. Provide personalized skincare advice for someone with the following profile:

Skin Type: {skin_type}
Main Concerns: {concerns_text}
Preferred Ingredients: {preferred_text}
Ingredients to Avoid: {avoided_text}

Provide 3-4 concise, actionable tips for their skincare routine. Be specific and helpful. Keep the response under 200 words."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful skincare expert who provides personalized, evidence-based skincare advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )

            advice = response.choices[0].message.content.strip()
            logger.info("Generated skincare advice successfully")
            return advice

        except Exception as e:
            logger.error(f"Error generating skincare advice: {str(e)}")
            return None

    def explain_product_recommendation(
        self,
        product: Dict[str, Any],
        profile: Dict[str, Any],
        score: float
    ) -> Optional[str]:
        """
        Generate a natural language explanation for why a product is recommended

        Args:
            product: Product details (name, brand, ingredients, etc.)
            profile: User skin profile
            score: Recommendation score (0-100)

        Returns:
            Natural language explanation
        """
        if not self.client:
            logger.warning("GPT service not available")
            return None

        try:
            product_name = product.get('name', 'this product')
            brand = product.get('brand', 'Unknown')
            skin_type = profile.get('skin_type', 'your skin type')
            concerns = profile.get('concerns', [])

            concerns_text = ", ".join(concerns[:3]) if concerns else "your skin concerns"

            prompt = f"""You are a skincare expert. Explain in 1-2 sentences why {product_name} by {brand} (match score: {score:.0f}/100) is a good fit for someone with {skin_type} skin who is concerned about {concerns_text}.

Be specific, warm, and encouraging. Mention key benefits."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a friendly skincare advisor who explains product recommendations clearly and warmly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )

            explanation = response.choices[0].message.content.strip()
            return explanation

        except Exception as e:
            logger.error(f"Error explaining product recommendation: {str(e)}")
            return None

    def enhance_product_descriptions(
        self,
        products: List[Dict[str, Any]],
        profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enhance multiple product recommendations with GPT-generated explanations

        Args:
            products: List of recommended products with scores
            profile: User skin profile

        Returns:
            Products with enhanced 'reason' field
        """
        if not self.client:
            return products

        enhanced_products = []

        for product in products[:5]:  # Only enhance top 5 to save API costs
            try:
                gpt_explanation = self.explain_product_recommendation(
                    product,
                    profile,
                    product.get('score', 0)
                )

                if gpt_explanation:
                    product['reason'] = gpt_explanation
                    product['gpt_enhanced'] = True

                enhanced_products.append(product)

            except Exception as e:
                logger.error(f"Error enhancing product {product.get('name')}: {str(e)}")
                enhanced_products.append(product)

        # Add remaining products without GPT enhancement
        enhanced_products.extend(products[5:])

        return enhanced_products

    def generate_deal_insights(
        self,
        product_name: str,
        deals: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Generate insights about deals found for a product

        Args:
            product_name: Name of the product searched
            deals: List of deals found

        Returns:
            Natural language insights about the deals
        """
        if not self.client or not deals:
            return None

        try:
            # Extract key deal info
            prices = [d.get('price', 0) for d in deals if d.get('price', 0) > 0]
            sellers = list(set([d.get('seller', 'Unknown') for d in deals[:5]]))

            if not prices:
                return None

            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            sellers_text = ", ".join(sellers[:3])

            prompt = f"""You are a shopping advisor. Provide a brief, helpful insight about these deals for "{product_name}":

- Found {len(deals)} deals
- Price range: ${min_price:.2f} - ${max_price:.2f}
- Average price: ${avg_price:.2f}
- Top sellers: {sellers_text}

In 1-2 sentences, highlight the best value and any notable findings. Be concise and actionable."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful shopping advisor who provides quick, actionable insights about product deals."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80,
                temperature=0.7
            )

            insights = response.choices[0].message.content.strip()
            logger.info("Generated deal insights successfully")
            return insights

        except Exception as e:
            logger.error(f"Error generating deal insights: {str(e)}")
            return None

    def is_available(self) -> bool:
        """Check if GPT service is available"""
        return self.client is not None
