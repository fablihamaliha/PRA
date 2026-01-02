from flask import Blueprint, request, jsonify, render_template
from services.deal_finder_service import DealFinderService
import logging

logger = logging.getLogger(__name__)

deals_bp = Blueprint('deals', __name__)
deal_service = DealFinderService()


@deals_bp.route('/')
def deals_page():
    """Render the deal finder page"""
    return render_template('deal_finder.html')


@deals_bp.route('/api/search', methods=['POST'])
def search_deals():
    """
    API endpoint to search for product deals

    Request body:
    {
        "product_name": "iPhone 15",
        "use_location": true
    }

    Response:
    {
        "success": true,
        "data": {
            "product_name": "iPhone 15",
            "location": {...},
            "total_deals": 10,
            "best_deal": {...},
            "all_deals": [...]
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'product_name' not in data:
            return jsonify({
                'success': False,
                'error': 'Product name is required'
            }), 400

        product_name = data['product_name'].strip()

        if not product_name:
            return jsonify({
                'success': False,
                'error': 'Product name cannot be empty'
            }), 400

        # Get user location if requested
        location = None
        if data.get('use_location', False):
            # Get client IP address
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if client_ip:
                # Extract first IP if multiple (X-Forwarded-For can have multiple IPs)
                client_ip = client_ip.split(',')[0].strip()
                location = deal_service.get_user_location(client_ip)

        # Search for deals
        max_results = data.get('max_results', 10)
        results = deal_service.search_deals(
            product_name=product_name,
            location=location,
            max_results=max_results
        )

        return jsonify({
            'success': True,
            'data': results
        }), 200

    except Exception as e:
        logger.error(f"Error searching deals: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred while searching for deals',
            'message': str(e)
        }), 500


@deals_bp.route('/api/location', methods=['GET'])
def get_location():
    """
    Get user location from IP address

    Response:
    {
        "success": true,
        "data": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York",
            "region": "New York",
            "country": "United States",
            "zip_code": "10001"
        }
    }
    """
    try:
        # Get client IP address
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
            location = deal_service.get_user_location(client_ip)

            if location:
                return jsonify({
                    'success': True,
                    'data': location
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Could not determine location'
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': 'Could not determine IP address'
            }), 400

    except Exception as e:
        logger.error(f"Error getting location: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred while getting location'
        }), 500


@deals_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for the deals API"""
    return jsonify({
        'success': True,
        'message': 'Deals API is running',
        'services': {
            'google_shopping': bool(deal_service.google_api_key),
            'walmart': bool(deal_service.walmart_api_key),
            'target': bool(deal_service.target_api_key),
            'best_buy': bool(deal_service.best_buy_api_key),
            'amazon': bool(deal_service.amazon_api_key)
        }
    }), 200
