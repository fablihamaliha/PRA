"""
Routine Builder Service
Handles GPT-based routine generation, product search, and deal finding
"""

import os
import logging
import json
from typing import List, Dict, Optional
import openai

logger = logging.getLogger(__name__)


class RoutineBuilderService:
    """Service for building personalized skincare routines"""

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

    def generate_routine_structure(
        self,
        skin_type: str,
        concerns: List[str],
        budget: str,
        lifestyle: List[str],
        preferred_ingredients: List[str],
        avoided_ingredients: List[str]
    ) -> Dict:
        """
        Use GPT to generate a personalized routine structure with step names only.

        Args:
            skin_type: User's skin type (oily, dry, combination, normal, sensitive)
            concerns: List of skin concerns (acne, aging, hyperpigmentation, etc.)
            budget: Budget preference (budget, mid-range, luxury, mixed)
            lifestyle: Lifestyle factors (outdoors, makeup, minimal, extensive, gym, travel)
            preferred_ingredients: List of ingredients user prefers
            avoided_ingredients: List of ingredients to avoid

        Returns:
            Dictionary with AM and PM routine steps (no specific products)
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured, using default routine")
            return self._get_default_routine_structure()

        try:
            # Build the prompt for GPT
            prompt = self._build_gpt_prompt(
                skin_type, concerns, budget, lifestyle, preferred_ingredients, avoided_ingredients
            )

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional skincare expert who creates personalized skincare routines. Return responses in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )

            # Parse the response
            gpt_response = response.choices[0].message.content
            routine_structure = json.loads(gpt_response)

            logger.info(f"Generated routine structure for {skin_type} skin")
            return routine_structure

        except Exception as e:
            logger.error(f"Error generating routine with GPT: {str(e)}")
            return self._get_default_routine_structure()

    def _build_gpt_prompt(
        self,
        skin_type: str,
        concerns: List[str],
        budget: str,
        lifestyle: List[str],
        preferred_ingredients: List[str],
        avoided_ingredients: List[str]
    ) -> str:
        """Build the GPT prompt for routine generation - returns STEPS only, no specific products"""
        concerns_str = ", ".join(concerns) if concerns else "general healthy skin"
        lifestyle_str = ", ".join(lifestyle) if lifestyle else "typical daily routine"
        preferred_str = ", ".join(preferred_ingredients) if preferred_ingredients else "no specific preferences"
        avoided_str = ", ".join(avoided_ingredients) if avoided_ingredients else "none"

        prompt = f"""
You are a professional skincare expert creating a personalized routine structure.

User Profile:
- Skin Type: {skin_type}
- Main Concerns: {concerns_str}
- Budget Preference: {budget}
- Lifestyle: {lifestyle_str}
- Prefers Ingredients: {preferred_str}
- Wants to Avoid: {avoided_str}

Create a personalized AM and PM routine with STEP NAMES ONLY (no specific products).

For each step, specify:
1. step_name: The product category (e.g., "Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen")
2. order: Step number in routine
3. why_this_matters: Why this step is important for their specific skin concerns (1-2 sentences)
4. what_to_look_for: Key ingredients or product characteristics to seek (based on their skin type and concerns)
5. what_to_avoid: Ingredients to avoid (from their blacklist + skin-specific recommendations)
6. search_keywords: Keywords for product search (e.g., ["hydrating cleanser", "gentle cleanser"])

Important Guidelines:
- Adjust routine complexity based on lifestyle:
  * "minimal" preference → 3-4 steps max
  * "extensive" preference → 6-8 steps
- Always include SPF in AM routine (critical for all skin types)
- If they wear makeup daily, include "Makeup Remover" or "Cleansing Oil" as first PM step
- If outdoors often, emphasize "Antioxidant Serum" in AM and recommend SPF 50+
- For acne concerns, include BHA/salicylic acid products
- For aging concerns, include retinol (PM) and vitamin C (AM)
- For hyperpigmentation, include niacinamide, vitamin C, and AHAs

Return in this EXACT JSON format:
{{
    "AM": [
        {{
            "step_name": "Cleanser",
            "order": 1,
            "why_this_matters": "Removes overnight oils without stripping your combination skin's moisture",
            "what_to_look_for": ["gentle surfactants", "hyaluronic acid", "ceramides", "pH-balanced"],
            "what_to_avoid": ["sulfates", "fragrance", "alcohol"],
            "search_keywords": ["gentle cleanser combination skin", "hydrating cleanser"]
        }},
        {{
            "step_name": "Vitamin C Serum",
            "order": 2,
            "why_this_matters": "Brightens dark spots and protects against environmental damage",
            "what_to_look_for": ["L-ascorbic acid 10-20%", "ferulic acid", "vitamin E"],
            "what_to_avoid": ["fragrance", "essential oils"],
            "search_keywords": ["vitamin C serum hyperpigmentation", "brightening serum"]
        }}
    ],
    "PM": [
        {{
            "step_name": "Makeup Remover",
            "order": 1,
            "why_this_matters": "Essential first step to remove makeup before cleansing",
            "what_to_look_for": ["cleansing oil", "micellar water", "gentle surfactants"],
            "what_to_avoid": ["harsh alcohols", "fragrance"],
            "search_keywords": ["makeup remover oil", "cleansing balm"]
        }}
    ]
}}

Focus on creating the optimal routine structure based on their needs. No product recommendations - just the steps and guidance.
"""
        return prompt

    def _get_default_routine_structure(self) -> Dict:
        """Return a default routine structure if GPT is unavailable"""
        return {
            "AM": [
                {
                    "step_name": "Cleanser",
                    "order": 1,
                    "why_this_matters": "Removes overnight oils and prepares skin for treatment",
                    "what_to_look_for": ["gentle surfactants", "glycerin", "ceramides"],
                    "what_to_avoid": ["sulfates", "harsh alcohols"],
                    "search_keywords": ["gentle cleanser", "morning cleanser"]
                },
                {
                    "step_name": "Toner",
                    "order": 2,
                    "why_this_matters": "Balances pH and preps skin for better absorption",
                    "what_to_look_for": ["hyaluronic acid", "niacinamide", "glycerin"],
                    "what_to_avoid": ["alcohol", "fragrance"],
                    "search_keywords": ["hydrating toner", "balancing toner"]
                },
                {
                    "step_name": "Serum",
                    "order": 3,
                    "why_this_matters": "Delivers concentrated active ingredients",
                    "what_to_look_for": ["vitamin C", "antioxidants", "niacinamide"],
                    "what_to_avoid": ["fragrance", "essential oils"],
                    "search_keywords": ["vitamin C serum", "antioxidant serum"]
                },
                {
                    "step_name": "Moisturizer",
                    "order": 4,
                    "why_this_matters": "Locks in hydration and protects skin barrier",
                    "what_to_look_for": ["ceramides", "peptides", "hyaluronic acid"],
                    "what_to_avoid": ["heavy oils", "comedogenic ingredients"],
                    "search_keywords": ["day moisturizer", "hydrating cream"]
                },
                {
                    "step_name": "Sunscreen",
                    "order": 5,
                    "why_this_matters": "Protects against UV damage and premature aging",
                    "what_to_look_for": ["SPF 30+", "broad spectrum", "PA+++"],
                    "what_to_avoid": ["oxybenzone", "octinoxate"],
                    "search_keywords": ["facial sunscreen", "SPF moisturizer"]
                }
            ],
            "PM": [
                {
                    "step_name": "Cleanser",
                    "order": 1,
                    "why_this_matters": "Removes makeup, sunscreen, and daily buildup",
                    "what_to_look_for": ["gentle surfactants", "oil cleansers", "micellar water"],
                    "what_to_avoid": ["sulfates", "harsh scrubs"],
                    "search_keywords": ["double cleanse", "makeup remover cleanser"]
                },
                {
                    "step_name": "Toner",
                    "order": 2,
                    "why_this_matters": "Restores pH balance after cleansing",
                    "what_to_look_for": ["hyaluronic acid", "glycerin", "aloe vera"],
                    "what_to_avoid": ["alcohol", "fragrance"],
                    "search_keywords": ["hydrating toner", "soothing toner"]
                },
                {
                    "step_name": "Treatment Serum",
                    "order": 3,
                    "why_this_matters": "Targets specific concerns while skin repairs overnight",
                    "what_to_look_for": ["retinol", "niacinamide", "peptides"],
                    "what_to_avoid": ["fragrance", "essential oils"],
                    "search_keywords": ["night serum", "anti-aging serum"]
                },
                {
                    "step_name": "Moisturizer",
                    "order": 4,
                    "why_this_matters": "Seals in treatment and supports overnight repair",
                    "what_to_look_for": ["ceramides", "hyaluronic acid", "squalane"],
                    "what_to_avoid": ["heavy fragrances", "comedogenic oils"],
                    "search_keywords": ["night cream", "repair moisturizer"]
                }
            ]
        }

    def search_products_for_step(
        self,
        category: str,
        key_ingredients: List[str],
        avoided_ingredients: List[str],
        search_terms: List[str],
        limit: int = 3
    ) -> List[Dict]:
        """
        Search for products matching the routine step requirements.
        This will be implemented with a web scraper.

        Args:
            category: Product category (cleanser, toner, etc.)
            key_ingredients: Ingredients to look for
            avoided_ingredients: Ingredients to exclude
            search_terms: Search terms for finding products
            limit: Maximum number of products to return

        Returns:
            List of product dictionaries
        """
        # This will call the product scraper service
        # For now, return placeholder
        logger.info(f"Searching for {category} products")

        return [
            {
                "name": f"Sample {category.title()}",
                "brand": "Sample Brand",
                "price": 29.99,
                "why_matched": f"Contains {', '.join(key_ingredients[:2])} suitable for your skin",
                "ingredients": key_ingredients,
                "url": "https://example.com/product",
                "image_url": "https://via.placeholder.com/150"
            }
        ]

    def find_affordable_luxury_alternatives(
        self,
        products: List[Dict],
        affordable_max: float = 30.0,
        luxury_min: float = 100.0
    ) -> Dict[str, List[Dict]]:
        """
        Find affordable (<$30) and luxury (>$100) alternatives for products.

        Args:
            products: List of products from the routine
            affordable_max: Maximum price for affordable category
            luxury_min: Minimum price for luxury category

        Returns:
            Dictionary with 'affordable' and 'luxury' keys containing product lists
        """
        # This will be implemented with web scraping
        logger.info(f"Finding alternatives for {len(products)} products")

        return {
            "affordable": [],
            "luxury": []
        }
