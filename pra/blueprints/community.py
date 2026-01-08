"""
Community Blueprint
Social features including product comments and reviews
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from pra.models.db import db
from pra.models.community import ProductComment, CommentHelpfulVote
from pra.models.product import Product
import logging

logger = logging.getLogger(__name__)

community_bp = Blueprint('community', __name__)


@community_bp.route('/')
def community_page():
    """Display community page with recent product comments"""
    # Get recent comments with products
    recent_comments = ProductComment.query\
        .order_by(ProductComment.created_at.desc())\
        .limit(50)\
        .all()

    return render_template('community.html', comments=recent_comments)


@community_bp.route('/product/<int:product_id>')
def product_discussion(product_id):
    """Display discussion page for a specific product"""
    product = Product.query.get_or_404(product_id)

    # Get comments for this product
    comments = ProductComment.query\
        .filter_by(product_id=product_id)\
        .order_by(ProductComment.created_at.desc())\
        .all()

    return render_template('product_discussion.html', product=product, comments=comments)


@community_bp.route('/api/comment', methods=['POST'])
@login_required
def add_comment():
    """Add a new comment to a product"""
    try:
        data = request.get_json()

        product_id = data.get('product_id')
        comment_text = data.get('comment_text', '').strip()
        rating = data.get('rating')

        if not product_id:
            return jsonify({'success': False, 'error': 'Product ID is required'}), 400

        if not comment_text:
            return jsonify({'success': False, 'error': 'Comment text is required'}), 400

        # Validate rating if provided
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Invalid rating value'}), 400

        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404

        # Create comment
        comment = ProductComment(
            user_id=current_user.id,
            product_id=product_id,
            comment_text=comment_text,
            rating=rating
        )

        db.session.add(comment)
        db.session.commit()

        return jsonify({
            'success': True,
            'comment': comment.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to add comment'}), 500


@community_bp.route('/api/comment/<int:comment_id>', methods=['PUT'])
@login_required
def edit_comment(comment_id):
    """Edit an existing comment"""
    try:
        comment = ProductComment.query.get_or_404(comment_id)

        # Check if user owns this comment
        if comment.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        data = request.get_json()
        comment_text = data.get('comment_text', '').strip()

        if not comment_text:
            return jsonify({'success': False, 'error': 'Comment text is required'}), 400

        comment.comment_text = comment_text
        comment.is_edited = True

        # Update rating if provided
        if 'rating' in data:
            rating = data['rating']
            if rating is not None:
                try:
                    rating = int(rating)
                    if rating < 1 or rating > 5:
                        return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400
                    comment.rating = rating
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'error': 'Invalid rating value'}), 400

        db.session.commit()

        return jsonify({
            'success': True,
            'comment': comment.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error editing comment: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to edit comment'}), 500


@community_bp.route('/api/comment/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        comment = ProductComment.query.get_or_404(comment_id)

        # Check if user owns this comment
        if comment.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        db.session.delete(comment)
        db.session.commit()

        return jsonify({'success': True}), 200

    except Exception as e:
        logger.error(f"Error deleting comment: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to delete comment'}), 500


@community_bp.route('/api/comment/<int:comment_id>/helpful', methods=['POST'])
@login_required
def mark_helpful(comment_id):
    """Mark a comment as helpful"""
    try:
        comment = ProductComment.query.get_or_404(comment_id)

        # Check if user already voted
        existing_vote = CommentHelpfulVote.query.filter_by(
            user_id=current_user.id,
            comment_id=comment_id
        ).first()

        if existing_vote:
            # Remove vote (toggle)
            db.session.delete(existing_vote)
            comment.helpful_count = max(0, comment.helpful_count - 1)
            action = 'removed'
        else:
            # Add vote
            vote = CommentHelpfulVote(
                user_id=current_user.id,
                comment_id=comment_id
            )
            db.session.add(vote)
            comment.helpful_count += 1
            action = 'added'

        db.session.commit()

        return jsonify({
            'success': True,
            'action': action,
            'helpful_count': comment.helpful_count
        }), 200

    except Exception as e:
        logger.error(f"Error marking comment helpful: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to mark comment as helpful'}), 500


@community_bp.route('/api/search-products', methods=['GET'])
def search_products():
    """Search for products by name or brand"""
    try:
        query = request.args.get('q', '').strip()

        if not query:
            return jsonify({'success': False, 'error': 'Search query is required'}), 400

        # Search products by name or brand
        products = Product.query.filter(
            db.or_(
                Product.name.ilike(f'%{query}%'),
                Product.brand.ilike(f'%{query}%')
            )
        ).limit(20).all()

        return jsonify({
            'success': True,
            'products': [p.to_dict() for p in products]
        }), 200

    except Exception as e:
        logger.error(f"Error searching products: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to search products'}), 500
