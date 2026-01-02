#!/usr/bin/env python3
"""
Quick test script to verify RapidAPI integration
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pra'))

from dotenv import load_dotenv
load_dotenv()

from services.deal_finder_service import DealFinderService

def test_rapidapi():
    """Test RapidAPI product search"""
    print("Testing RapidAPI Product Search Integration")
    print("=" * 50)

    # Check API key is loaded
    api_key = os.environ.get('RAPIDAPI_KEY', '')
    if not api_key:
        print("❌ ERROR: RAPIDAPI_KEY not found in environment")
        return False

    print(f"✓ API Key loaded: {api_key[:20]}...")
    print()

    # Initialize service
    service = DealFinderService()
    print("✓ DealFinderService initialized")
    print()

    # Test search
    print("Searching for: laptop")
    print("Please wait...")
    print()

    try:
        results = service.search_deals(
            product_name="laptop",
            location=None,
            max_results=5
        )

        print("=" * 50)
        print("SEARCH RESULTS:")
        print("=" * 50)
        print(f"Product: {results['product_name']}")
        print(f"Total deals found: {results['total_deals']}")
        print()

        print("Sources checked:")
        for source in results['sources']:
            status_icon = {
                'success': '✓',
                'no_results': '○',
                'error': '✗'
            }.get(source['status'], '?')

            print(f"  {status_icon} {source['name']}: {source['count']} products ({source['status']})")

        print()

        if results['best_deal']:
            best = results['best_deal']
            print("BEST DEAL:")
            print(f"  Product: {best['product_name']}")
            print(f"  Seller: {best['seller']}")
            print(f"  Price: ${best['price']:.2f}")
            print(f"  Rating: {best['rating']} stars ({best['reviews']} reviews)")
            print(f"  URL: {best['url']}")
            print()

            print("✅ SUCCESS! RapidAPI integration is working!")
            return True
        else:
            print("⚠️  WARNING: No deals found")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rapidapi()
    sys.exit(0 if success else 1)
