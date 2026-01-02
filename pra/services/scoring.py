import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ScoringService:
    """
    Service for scoring product matches based on user profile
    """

    # Scoring weights
    SKIN_TYPE_WEIGHT = 0.4
    CONCERNS_WEIGHT = 0.3
    PREFERRED_INGREDIENTS_WEIGHT = 0.2
    AVOIDED_INGREDIENTS_PENALTY = 0.1
    RATING_BONUS = 0.1

    RATING_THRESHOLD = 4.0

    def score_product(self, product: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """
        Calculate match score for a product based on user profile

        Args:
            product: Product dictionary
            profile: User skin profile dictionary

        Returns:
            Score between 0 and 1
        """
        score = 0.0

        # Skin type match
        score += self._score_skin_type(product, profile)

        # Concerns match
        score += self._score_concerns(product, profile)

        # Preferred ingredients
        score += self._score_preferred_ingredients(product, profile)

        # Avoided ingredients penalty
        score -= self._score_avoided_ingredients(product, profile)

        # Rating bonus
        score += self._score_rating(product)

        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))

        return round(score, 2)

    def _score_skin_type(self, product: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """Score based on skin type match"""
        user_skin_type = profile.get('skin_type', '').lower()
        product_skin_types = [st.lower() for st in product.get('skin_types', [])]

        if not user_skin_type or not product_skin_types:
            return 0.0

        # Full match
        if user_skin_type in product_skin_types:
            return self.SKIN_TYPE_WEIGHT

        # Partial match for 'all' or 'universal'
        if 'all' in product_skin_types or 'universal' in product_skin_types:
            return self.SKIN_TYPE_WEIGHT * 0.5

        return 0.0

    def _score_concerns(self, product: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """Score based on skin concern matches"""
        user_concerns = set(c.lower() for c in profile.get('concerns', []))
        product_tags = set(t.lower() for t in product.get('tags', []))

        if not user_concerns:
            return 0.0

        # Count matching concerns
        matching_concerns = user_concerns.intersection(product_tags)

        if not matching_concerns:
            return 0.0

        # Proportional score based on how many concerns are addressed
        match_ratio = len(matching_concerns) / len(user_concerns)
        return self.CONCERNS_WEIGHT * match_ratio

    def _score_preferred_ingredients(self, product: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """Score based on preferred ingredient presence"""
        preferred = set(i.lower() for i in profile.get('preferred_ingredients', []))
        product_ingredients = set(i.lower() for i in product.get('ingredients', []))

        if not preferred:
            return 0.0

        # Count matching ingredients
        matching = preferred.intersection(product_ingredients)

        if not matching:
            return 0.0

        # Proportional score
        match_ratio = len(matching) / len(preferred)
        return self.PREFERRED_INGREDIENTS_WEIGHT * match_ratio

    def _score_avoided_ingredients(self, product: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """Penalty for avoided ingredient presence"""
        avoided = set(i.lower() for i in profile.get('avoided_ingredients', []))
        product_ingredients = set(i.lower() for i in product.get('ingredients', []))

        if not avoided:
            return 0.0

        # Count unwanted ingredients present
        unwanted = avoided.intersection(product_ingredients)

        if not unwanted:
            return 0.0

        # Apply penalty proportional to number of avoided ingredients found
        penalty_ratio = len(unwanted) / len(avoided)
        return self.AVOIDED_INGREDIENTS_PENALTY * penalty_ratio

    def _score_rating(self, product: Dict[str, Any]) -> float:
        """Bonus for high ratings"""
        rating = product.get('rating', 0)

        if rating >= self.RATING_THRESHOLD:
            return self.RATING_BONUS

        return 0.0

    def generate_reason(self, product: Dict[str, Any], profile: Dict[str, Any], score: float) -> str:
        """
        Generate human-readable reason for recommendation

        Args:
            product: Product dictionary
            profile: User skin profile dictionary
            score: Calculated match score

        Returns:
            Reason string
        """
        reasons = []

        # Skin type
        user_skin_type = profile.get('skin_type', '').lower()
        product_skin_types = [st.lower() for st in product.get('skin_types', [])]
        if user_skin_type in product_skin_types:
            reasons.append(f"suitable for {user_skin_type} skin")

        # Concerns
        user_concerns = set(c.lower() for c in profile.get('concerns', []))
        product_tags = set(t.lower() for t in product.get('tags', []))
        matching_concerns = user_concerns.intersection(product_tags)
        if matching_concerns:
            concerns_str = ', '.join(matching_concerns)
            reasons.append(f"addresses {concerns_str}")

        # Preferred ingredients
        preferred = set(i.lower() for i in profile.get('preferred_ingredients', []))
        product_ingredients = set(i.lower() for i in product.get('ingredients', []))
        matching_ingredients = preferred.intersection(product_ingredients)
        if matching_ingredients:
            ingredients_str = ', '.join(list(matching_ingredients)[:2])  # Show max 2
            reasons.append(f"contains {ingredients_str}")

        # Avoided ingredients
        avoided = set(i.lower() for i in profile.get('avoided_ingredients', []))
        unwanted = avoided.intersection(product_ingredients)
        if not unwanted and avoided:
            reasons.append("free from ingredients you avoid")

        # Rating
        rating = product.get('rating', 0)
        if rating >= self.RATING_THRESHOLD:
            reasons.append(f"highly rated ({rating}/5)")

        if not reasons:
            return "Matches your general preferences"

        return "Great choice: " + ", ".join(reasons)