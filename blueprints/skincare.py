from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

skincare_bp = Blueprint('skincare', __name__)


@skincare_bp.route('/quiz', methods=['POST'])
def quiz():
    """
    Create or update skin profile for a user
    """
    # Import here to avoid circular imports
    from models.db import db
    from models.user import User
    from models.skin_profile import SkinProfile
    from utils.validators import validate_quiz_input

    try:
        data = request.get_json()

        # Validate input
        is_valid, errors = validate_quiz_input(data)
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400

        user_id = data.get('user_id')

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check if profile exists
        profile = SkinProfile.query.filter_by(user_id=user_id).first()

        # In the quiz() function, update profile creation/update:

        if profile:
            # Update existing profile
            profile.skin_type = data.get('skin_type')
            profile.concerns_list = data.get('concerns', [])  # Use property setter
            profile.budget_min = data.get('budget_min')
            profile.budget_max = data.get('budget_max')
            profile.preferred_ingredients_list = data.get('preferred_ingredients', [])  # Use property setter
            profile.avoided_ingredients_list = data.get('avoided_ingredients', [])  # Use property setter
        else:
            # Create new profile
            profile = SkinProfile(
                user_id=user_id,
                skin_type=data.get('skin_type'),
                budget_min=data.get('budget_min'),
                budget_max=data.get('budget_max')
            )
            profile.concerns_list = data.get('concerns', [])
            profile.preferred_ingredients_list = data.get('preferred_ingredients', [])
            profile.avoided_ingredients_list = data.get('avoided_ingredients', [])
            db.session.add(profile)

        db.session.commit()

        logger.info(f"Skin profile saved for user {user_id}")

        return jsonify({
            'message': 'Skin profile saved successfully',
            'profile_id': profile.id
        }), 200

    except Exception as e:
        logger.error(f"Error in quiz endpoint: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@skincare_bp.route('/auto-cart', methods=['POST'])
def auto_add_to_cart():
    """
    Automatically login to Sephora and add recommendations to cart
    """
    from services.sephora_automation import SephoraCartService

    try:
        data = request.get_json()

        # Required fields
        user_id = data.get('user_id')
        sephora_email = data.get('sephora_email')
        sephora_password = data.get('sephora_password')

        if not all([user_id, sephora_email, sephora_password]):
            return jsonify({
                'error': 'Missing required fields: user_id, sephora_email, sephora_password'
            }), 400

        # Get recommendations
        from models.user import User
        from models.skin_profile import SkinProfile
        from services.recommender import RecommenderService

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        profile = SkinProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'error': 'Skin profile not found'}), 404

        # Generate recommendations
        recommender = RecommenderService()
        recommendations = recommender.get_recommendations(profile.to_dict())

        # Auto-add to cart
        cart_service = SephoraCartService()
        result = cart_service.auto_add_recommendations(
            sephora_email,
            sephora_password,
            recommendations
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Auto-cart error: {str(e)}")
        return jsonify({'error': str(e)}), 500
@skincare_bp.route('/recommend', methods=['POST'])
def recommend():
    """
    Generate product recommendations based on skin profile
    """
    # Import here to avoid circular imports
    from models.db import db
    from models.user import User
    from models.skin_profile import SkinProfile
    from models.recommendation import RecommendationSession, RecommendationItem
    from services.recommender import RecommenderService
    from utils.validators import validate_recommend_input

    try:
        data = request.get_json()

        # Validate input
        is_valid, errors = validate_recommend_input(data)
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400

        # Get skin profile
        if 'user_id' in data:
            # Load from database
            user_id = data['user_id']
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            profile = SkinProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return jsonify({'error': 'Skin profile not found. Please complete the quiz first.'}), 404

            profile_dict = profile.to_dict()
        else:
            # Use provided data
            user_id = None
            profile_dict = {
                'skin_type': data.get('skin_type'),
                'concerns': data.get('concerns', []),
                'budget_min': data.get('budget_min'),
                'budget_max': data.get('budget_max'),
                'preferred_ingredients': data.get('preferred_ingredients', []),
                'avoided_ingredients': data.get('avoided_ingredients', [])
            }

        # Generate recommendations
        recommender = RecommenderService()
        recommendations = recommender.get_recommendations(profile_dict)

        # Save recommendation session if user exists
        session_id = None
        if user_id:
            session = RecommendationSession(
                user_id=user_id,
                skin_profile_id=profile.id if 'profile' in locals() else None
            )
            db.session.add(session)
            db.session.flush()

            # Save recommendation items
            for idx, rec in enumerate(recommendations):
                item = RecommendationItem(
                    session_id=session.id,
                    product_id=rec.get('product_id'),
                    rank=idx + 1,
                    match_score=rec.get('score'),
                    reason=rec.get('reason')
                )
                db.session.add(item)

            db.session.commit()
            session_id = session.id
            logger.info(f"Recommendation session {session_id} created for user {user_id}")

        return jsonify({
            'session_id': session_id,
            'recommendations': recommendations
        }), 200

    except Exception as e:
        logger.error(f"Error in recommend endpoint: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@skincare_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """
    Get user's skin profile
    """
    from models.skin_profile import SkinProfile

    try:
        profile = SkinProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        return jsonify(profile.to_dict()), 200

    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@skincare_bp.route('/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    """
    Get user's recommendation history
    """
    from models.recommendation import RecommendationSession, RecommendationItem

    try:
        sessions = RecommendationSession.query.filter_by(user_id=user_id) \
            .order_by(RecommendationSession.created_at.desc()) \
            .limit(10).all()

        history = []
        for session in sessions:
            items = RecommendationItem.query.filter_by(session_id=session.id) \
                .order_by(RecommendationItem.rank).all()

            history.append({
                'session_id': session.id,
                'created_at': session.created_at.isoformat(),
                'recommendations': [item.to_dict() for item in items]
            })

        return jsonify({'history': history}), 200

    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500