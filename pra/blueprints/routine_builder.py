"""
Routine Builder Blueprint
Handles routine generation, deals, and shopping lists
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import current_user, login_required
import logging
import uuid

from pra.models.db import db
from pra.models.routine import Routine, RoutineProduct, ShoppingList, ShoppingListItem, SavedRoutine
from pra.models.product import Product
from pra.services.routine_builder_service import RoutineBuilderService
from pra.services.product_scraper_service import ProductScraperService
from pra.services.deal_finder_service import DealFinderService
import json

logger = logging.getLogger(__name__)

# Create blueprint
routine_builder_bp = Blueprint('routine_builder', __name__)

# Initialize services
routine_service = RoutineBuilderService()
scraper_service = ProductScraperService()
deal_finder_service = DealFinderService()

def _get_step_by_order(routine, time_of_day, step_order):
    steps = routine.get(time_of_day.upper(), [])
    for step in steps:
        if step.get('order') == step_order:
            return step
    if 1 <= step_order <= len(steps):
        return steps[step_order - 1]
    return None


def _fetch_step_deals(step, routine_data):
    base_keywords = step.get('search_keywords') or [step.get('step_name', '')]
    skin_type = routine_data.get('skin_type', '')
    concerns = routine_data.get('concerns', [])
    search_keywords = base_keywords + [skin_type] + concerns
    search_keywords = [kw for kw in search_keywords if kw]
    query = " ".join(search_keywords)
    deals_payload = deal_finder_service.search_deals(query, location=None, max_results=30)
    all_deals = deals_payload.get('all_deals', [])

    def normalize_deal(deal):
        return {
            'name': deal.get('product_name') or deal.get('name'),
            'brand': deal.get('seller') or 'Unknown',
            'price': deal.get('price') or 0,
            'rating': deal.get('rating') or 0,
            'num_reviews': deal.get('reviews') or 0,
            'url': deal.get('url'),
            'image_url': deal.get('image_url'),
            'source': deal.get('source', 'rapidapi'),
            'ingredients': deal.get('ingredients', [])
        }

    affordable = [
        normalize_deal(d) for d in all_deals
        if 0 < (d.get('price') or 0) <= 30
    ]
    luxury = [
        normalize_deal(d) for d in all_deals
        if (d.get('price') or 0) >= 50
    ]

    affordable = sorted(
        affordable,
        key=lambda p: (p.get('price') or float('inf'), -(p.get('rating') or 0))
    )[:8]
    luxury = sorted(
        luxury,
        key=lambda p: (-(p.get('rating') or 0), -(p.get('price') or 0))
    )[:8]

    return {
        'affordable': affordable,
        'luxury': luxury
    }


@routine_builder_bp.route('/build-routine')
def build_routine():
    """
    Show the routine builder form page.
    If user is logged in and has an existing routine, redirect to results.
    """
    # Check if user is authenticated and has existing routine
    if current_user.is_authenticated:
        existing_routine = SavedRoutine.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(SavedRoutine.updated_at.desc()).first()

        # If has routine and not in update mode, redirect to results
        if existing_routine and request.args.get('update') != 'true':
            # Get or create session for this routine
            session_id = existing_routine.session_id

            # Store routine in session if not already there
            if not session.get(f'routine_{session_id}'):
                routine_data = json.loads(existing_routine.routine_data)
                session[f'routine_{session_id}'] = {
                    'skin_type': existing_routine.skin_type,
                    'concerns': json.loads(existing_routine.concerns),
                    'budget': existing_routine.budget,
                    'lifestyle': json.loads(existing_routine.lifestyle),
                    'preferred_ingredients': json.loads(existing_routine.preferred_ingredients or '[]'),
                    'avoided_ingredients': json.loads(existing_routine.avoided_ingredients or '[]'),
                    'routine': routine_data
                }

            return redirect(url_for('routine_builder.routine_results', session_id=session_id))

        # If in update mode, pass existing routine data to pre-fill form
        if request.args.get('update') == 'true' and existing_routine:
            return render_template('build_routine.html',
                                   update_mode=True,
                                   routine_data={
                                       'skin_type': existing_routine.skin_type,
                                       'concerns': json.loads(existing_routine.concerns),
                                       'budget': existing_routine.budget,
                                       'lifestyle': json.loads(existing_routine.lifestyle),
                                       'preferred_ingredients': json.loads(existing_routine.preferred_ingredients or '[]'),
                                       'avoided_ingredients': json.loads(existing_routine.avoided_ingredients or '[]')
                                   })

    # No routine or not logged in - show form
    return render_template('build_routine.html', update_mode=False)


@routine_builder_bp.route('/api/generate-routine', methods=['POST'])
def generate_routine():
    """
    Generate a personalized routine based on user preferences.
    Accessible without login - stores in session.
    """
    try:
        data = request.get_json()

        # Extract form data
        skin_type = data.get('skin_type', 'normal')
        concerns = data.get('concerns', [])
        budget = data.get('budget', 'mixed')
        lifestyle = data.get('lifestyle', [])
        preferred_ingredients = data.get('preferred_ingredients', [])
        avoided_ingredients = data.get('avoided_ingredients', [])

        logger.info(f"Generating routine for {skin_type} skin with concerns: {concerns}, budget: {budget}")

        # Step 1: Generate routine structure with GPT (returns STEP NAMES only, no products)
        routine_structure = routine_service.generate_routine_structure(
            skin_type=skin_type,
            concerns=concerns,
            budget=budget,
            lifestyle=lifestyle,
            preferred_ingredients=preferred_ingredients,
            avoided_ingredients=avoided_ingredients
        )

        # Step 2: Store routine structure (no product search yet - happens when user clicks "View Products")
        session_id = str(uuid.uuid4())
        session[f'routine_{session_id}'] = {
            'skin_type': skin_type,
            'concerns': concerns,
            'budget': budget,
            'lifestyle': lifestyle,
            'preferred_ingredients': preferred_ingredients,
            'avoided_ingredients': avoided_ingredients,
            'routine': routine_structure  # Just the steps, not products
        }

        # Step 4: Auto-save for logged-in users
        if current_user.is_authenticated:
            try:
                # Check if user has existing routine
                existing_routine = SavedRoutine.query.filter_by(
                    user_id=current_user.id,
                    is_active=True
                ).order_by(SavedRoutine.updated_at.desc()).first()

                if existing_routine:
                    # Update existing routine
                    existing_routine.session_id = session_id
                    existing_routine.skin_type = skin_type
                    existing_routine.concerns = json.dumps(concerns)
                    existing_routine.budget = budget
                    existing_routine.lifestyle = json.dumps(lifestyle)
                    existing_routine.preferred_ingredients = json.dumps(preferred_ingredients)
                    existing_routine.avoided_ingredients = json.dumps(avoided_ingredients)
                    existing_routine.routine_data = json.dumps(routine_structure)
                    logger.info(f"Updated routine for user {current_user.id}")
                else:
                    # Create new saved routine
                    existing_routine = SavedRoutine(
                        user_id=current_user.id,
                        session_id=session_id,
                        skin_type=skin_type,
                        concerns=json.dumps(concerns),
                        budget=budget,
                        lifestyle=json.dumps(lifestyle),
                        preferred_ingredients=json.dumps(preferred_ingredients),
                        avoided_ingredients=json.dumps(avoided_ingredients),
                        routine_data=json.dumps(routine_structure),
                        is_active=True
                    )
                    db.session.add(existing_routine)
                    logger.info(f"Created new routine for user {current_user.id}")

                db.session.commit()
            except Exception as e:
                logger.error(f"Error auto-saving routine: {str(e)}")
                db.session.rollback()
                # Don't fail the request if save fails - routine still in session

        return jsonify({
            'success': True,
            'session_id': session_id,
            'routine': routine_structure
        }), 200

    except Exception as e:
        logger.error(f"Error generating routine: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate routine'
        }), 500


@routine_builder_bp.route('/routine-results/<session_id>')
def routine_results(session_id):
    """Show the generated routine results"""
    routine_data = session.get(f'routine_{session_id}')

    if not routine_data:
        return redirect(url_for('routine_builder.build_routine'))

    return render_template(
        'routine_results.html',
        session_id=session_id,
        routine=routine_data['routine'],
        skin_type=routine_data['skin_type'],
        concerns=routine_data['concerns']
    )


@routine_builder_bp.route('/routine-step-deals/<session_id>/<time_of_day>/<int:step_order>')
def routine_step_deals(session_id, time_of_day, step_order):
    """Show deals comparison for a specific routine step"""
    routine_data = session.get(f'routine_{session_id}')

    if not routine_data:
        return redirect(url_for('routine_builder.build_routine'))

    routine = routine_data['routine']
    step = _get_step_by_order(routine, time_of_day, step_order)

    if not step:
        return redirect(url_for('routine_builder.routine_results', session_id=session_id))

    deals = _fetch_step_deals(step, routine_data)

    return render_template(
        'routine_step_deals.html',
        session_id=session_id,
        time_of_day=time_of_day.upper(),
        step=step,
        deals=deals,
        skin_type=routine_data['skin_type'],
        concerns=routine_data['concerns']
    )


@routine_builder_bp.route('/api/routine-step-deals', methods=['POST'])
def routine_step_deals_api():
    """Fetch deals for a specific routine step"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        time_of_day = data.get('time_of_day')
        step_order = data.get('step_order')

        routine_data = session.get(f'routine_{session_id}')
        if not routine_data or not time_of_day or not step_order:
            return jsonify({
                'success': False,
                'error': 'Invalid routine step request'
            }), 400

        step = _get_step_by_order(routine_data['routine'], time_of_day, int(step_order))
        if not step:
            return jsonify({
                'success': False,
                'error': 'Step not found'
            }), 404

        deals = _fetch_step_deals(step, routine_data)

        return jsonify({
            'success': True,
            'step': step,
            'deals': deals
        }), 200

    except Exception as e:
        logger.error(f"Error fetching step deals: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch deals'
        }), 500


@routine_builder_bp.route('/api/find-deals', methods=['POST'])
def find_deals():
    """
    Find affordable and luxury alternatives for routine steps.
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        routine_data = session.get(f'routine_{session_id}')
        if not routine_data:
            return jsonify({
                'success': False,
                'error': 'Routine not found'
            }), 404

        routine = routine_data['routine']
        all_steps = routine.get('AM', []) + routine.get('PM', [])

        deals = {
            'affordable': [],
            'luxury': []
        }

        # Find alternatives for each step
        for step in all_steps:
            step_deals = _fetch_step_deals(step, routine_data)
            deals['affordable'].extend(step_deals['affordable'][:2])
            deals['luxury'].extend(step_deals['luxury'][:2])

        # Store deals in session
        session[f'deals_{session_id}'] = deals

        return jsonify({
            'success': True,
            'deals': deals
        }), 200

    except Exception as e:
        logger.error(f"Error finding deals: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to find deals'
        }), 500


@routine_builder_bp.route('/deals/<session_id>')
def deals_comparison(session_id):
    """Show affordable vs luxury deals comparison"""
    deals = session.get(f'deals_{session_id}')
    routine_data = session.get(f'routine_{session_id}')

    if not deals or not routine_data:
        return redirect(url_for('routine_builder.build_routine'))

    return render_template(
        'deals_comparison.html',
        session_id=session_id,
        deals=deals,
        routine=routine_data['routine']
    )


@routine_builder_bp.route('/api/check-existing-routine', methods=['POST'])
def check_existing_routine():
    """
    Check if user has existing routines with same or different parameters.
    Called before generating routine if user is logged in.
    """
    try:
        if not current_user.is_authenticated:
            return jsonify({'authenticated': False}), 200

        data = request.get_json()
        skin_type = data.get('skin_type', 'normal')
        concerns = sorted(data.get('concerns', []))
        budget = data.get('budget', 'mixed')
        lifestyle = sorted(data.get('lifestyle', []))

        # Get user's most recent routine
        existing_routine = SavedRoutine.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(SavedRoutine.updated_at.desc()).first()

        if not existing_routine:
            return jsonify({
                'authenticated': True,
                'has_existing': False
            }), 200

        # Compare parameters
        existing_concerns = sorted(existing_routine.get_concerns_list())
        existing_lifestyle = sorted(existing_routine.get_lifestyle_list())

        is_identical = (
            existing_routine.skin_type == skin_type and
            existing_concerns == concerns and
            existing_routine.budget == budget and
            existing_lifestyle == lifestyle
        )

        return jsonify({
            'authenticated': True,
            'has_existing': True,
            'is_identical': is_identical,
            'existing_routine': existing_routine.to_dict() if not is_identical else None
        }), 200

    except Exception as e:
        logger.error(f"Error checking existing routine: {str(e)}")
        return jsonify({'error': str(e)}), 500


@routine_builder_bp.route('/api/save-routine', methods=['POST'])
def save_routine():
    """
    Save routine to database.
    If user not authenticated, return 401 with redirect URL.
    If authenticated, save routine using SavedRoutine model.
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        routine_data = session.get(f'routine_{session_id}')
        if not routine_data:
            return jsonify({
                'success': False,
                'error': 'Routine not found'
            }), 404

        # Check if user is authenticated
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'redirect': f'/auth?next=/routine-results/{session_id}&action=save'
            }), 401

        # Check if updating existing routine or creating new
        update_existing = data.get('update_existing', False)
        existing_routine_id = data.get('existing_routine_id')

        if update_existing and existing_routine_id:
            # Update existing routine
            saved_routine = SavedRoutine.query.filter_by(
                id=existing_routine_id,
                user_id=current_user.id
            ).first()

            if not saved_routine:
                return jsonify({
                    'success': False,
                    'error': 'Routine not found'
                }), 404

            saved_routine.skin_type = routine_data['skin_type']
            saved_routine.concerns = json.dumps(routine_data['concerns'])
            saved_routine.budget = routine_data['budget']
            saved_routine.lifestyle = json.dumps(routine_data['lifestyle'])
            saved_routine.preferred_ingredients = json.dumps(routine_data.get('preferred_ingredients', []))
            saved_routine.avoided_ingredients = json.dumps(routine_data.get('avoided_ingredients', []))
            saved_routine.routine_data = json.dumps(routine_data['routine'])
        else:
            # Create new saved routine
            saved_routine = SavedRoutine(
                user_id=current_user.id,
                session_id=session_id,
                skin_type=routine_data['skin_type'],
                concerns=json.dumps(routine_data['concerns']),
                budget=routine_data['budget'],
                lifestyle=json.dumps(routine_data['lifestyle']),
                preferred_ingredients=json.dumps(routine_data.get('preferred_ingredients', [])),
                avoided_ingredients=json.dumps(routine_data.get('avoided_ingredients', [])),
                routine_data=json.dumps(routine_data['routine']),
                is_active=True
            )
            db.session.add(saved_routine)

        db.session.commit()
        logger.info(f"Saved routine for user {current_user.id}")

        return jsonify({
            'success': True,
            'routine_id': saved_routine.id,
            'message': 'Routine updated successfully!' if update_existing else 'Routine saved successfully!'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving routine: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to save routine'
        }), 500


@routine_builder_bp.route('/api/user/routines', methods=['GET'])
@login_required
def get_user_routines():
    """Get all saved routines for current user"""
    try:
        routines = SavedRoutine.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(SavedRoutine.updated_at.desc()).all()

        return jsonify({
            'success': True,
            'routines': [r.to_dict() for r in routines]
        }), 200

    except Exception as e:
        logger.error(f"Error fetching user routines: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch routines'
        }), 500


@routine_builder_bp.route('/api/create-shopping-list', methods=['POST'])
@login_required
def create_shopping_list():
    """
    Create shopping list from selected products.
    """
    try:
        data = request.get_json()
        selected_products = data.get('products', [])  # List of {product_id, is_affordable}
        list_name = data.get('name', 'My Shopping List')
        routine_id = data.get('routine_id')

        # Create shopping list
        shopping_list = ShoppingList(
            user_id=current_user.id,
            routine_id=routine_id,
            name=list_name
        )
        db.session.add(shopping_list)
        db.session.flush()

        # Add items to shopping list
        for item_data in selected_products:
            product_id = item_data.get('product_id')
            is_affordable = item_data.get('is_affordable', True)

            shopping_item = ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=product_id,
                is_affordable_option=is_affordable
            )
            db.session.add(shopping_item)

        db.session.commit()

        return jsonify({
            'success': True,
            'shopping_list_id': shopping_list.id
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating shopping list: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create shopping list'
        }), 500


@routine_builder_bp.route('/shopping-list/<int:list_id>')
@login_required
def view_shopping_list(list_id):
    """View shopping list"""
    shopping_list = ShoppingList.query.filter_by(
        id=list_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        'shopping_list.html',
        shopping_list=shopping_list
    )


@routine_builder_bp.route('/api/toggle-purchased/<int:item_id>', methods=['POST'])
@login_required
def toggle_purchased(item_id):
    """Toggle purchased status of a shopping list item"""
    try:
        item = ShoppingListItem.query.join(ShoppingList).filter(
            ShoppingListItem.id == item_id,
            ShoppingList.user_id == current_user.id
        ).first_or_404()

        item.is_purchased = not item.is_purchased
        db.session.commit()

        return jsonify({
            'success': True,
            'is_purchased': item.is_purchased
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling purchased status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update item'
        }), 500
