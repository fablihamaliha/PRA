#!/usr/bin/env python3
"""
Simple test script for GPT service integration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add pra directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pra'))

from services.gpt_service import GPTService


def test_gpt_service():
    """Test GPT service functionality"""
    print("Testing GPT Service Integration...")
    print("-" * 50)

    # Initialize service
    gpt_service = GPTService()

    # Check if service is available
    if not gpt_service.is_available():
        print("❌ GPT service not available. Please set OPENAI_API_KEY in .env file")
        print("\nTo get an API key:")
        print("1. Visit https://platform.openai.com/api-keys")
        print("2. Create a new API key")
        print("3. Add it to your .env file as: OPENAI_API_KEY=your-key-here")
        return

    print("✅ GPT service is available")
    print()

    # Test 1: Generate skincare advice
    print("Test 1: Generate Skincare Advice")
    print("-" * 50)
    test_profile = {
        'skin_type': 'oily',
        'concerns': ['acne', 'pores'],
        'preferred_ingredients': ['niacinamide', 'salicylic_acid'],
        'avoided_ingredients': ['fragrance', 'alcohol']
    }

    advice = gpt_service.generate_skincare_advice(test_profile)
    if advice:
        print("✅ Skincare advice generated successfully:")
        print(advice)
    else:
        print("❌ Failed to generate skincare advice")
    print()

    # Test 2: Explain product recommendation
    print("Test 2: Explain Product Recommendation")
    print("-" * 50)
    test_product = {
        'name': 'Hydrating Moisturizer',
        'brand': 'CeraVe',
        'score': 85
    }

    explanation = gpt_service.explain_product_recommendation(
        test_product,
        test_profile,
        85.0
    )
    if explanation:
        print("✅ Product explanation generated successfully:")
        print(explanation)
    else:
        print("❌ Failed to generate product explanation")
    print()

    # Test 3: Generate deal insights
    print("Test 3: Generate Deal Insights")
    print("-" * 50)
    test_deals = [
        {'price': 12.99, 'seller': 'Amazon'},
        {'price': 14.99, 'seller': 'Walmart'},
        {'price': 11.99, 'seller': 'Target'},
        {'price': 13.49, 'seller': 'CVS'}
    ]

    insights = gpt_service.generate_deal_insights('Moisturizer', test_deals)
    if insights:
        print("✅ Deal insights generated successfully:")
        print(insights)
    else:
        print("❌ Failed to generate deal insights")
    print()

    print("=" * 50)
    print("GPT Integration Test Complete!")


if __name__ == '__main__':
    test_gpt_service()
