from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class ProductReviewController(http.Controller):

    @http.route('/product/reviews', auth='public', type='json', methods=['GET'], csrf=False)
    def get_product_reviews(self, **kwargs):
        """Fetch all customer product reviews"""
        reviews = request.env['rating.rating'].sudo().search([
            ('res_model', '=', 'product.template'),
            ('rating', '!=', 0)
        ])
        result = []
        for review in reviews:
            result.append({
                'id': review.id,
                'product_id': review.res_id,
                'product_name': review.res_id and request.env['product.template'].browse(review.res_id).name or '',
                'name': review.partner_id.name if review.partner_id else '',
                'rating': review.rating or 0.0,
                'review': review.feedback or '',
                'publisher_comment': review.publisher_comment or '',
                'date': review.create_date.strftime('%Y-%m-%d') if review.create_date else '',
            })
        return {'status': 200, 'data': result}

    @http.route('/product/review', auth='public', type='json', methods=['POST'], csrf=False)
    def post_product_review(self, **kwargs):
        """
        Post a new customer product review.
        Required fields: product_id, rating, review
        """
        product_id = kwargs.get('product_id')
        rating = kwargs.get('rating')
        review = kwargs.get('review')
        partner_id = request.env.user.partner_id.id
        product = request.env['product.template'].sudo().browse(product_id)

        print("Product ID:", product_id)
        # Validation
        if not product_id or not rating or not review:
            return {'status': 400, 'message': 'Missing product_id, rating, or review.'}

        # Create review
        try:
            print('Creating rating.rating with:', {
                'res_model': 'product.template',
                'res_id': product_id,
                'rating': rating,
                'feedback': review,
                'partner_id': partner_id,
                'product_name': product.name,

            })
            review_record = request.env['rating.rating'].sudo().create({
                'res_model': 'product.template',
                'res_id': product_id,
                'rating': rating,
                'feedback': review,
                'partner_id': partner_id,
            })
            return {
                'status': 200,
                'message': 'Review submitted successfully.',
                'review_id': review_record.id
            }
        except Exception as e:
            return {
                'status': 500,
                'message': f'Error submitting review: {str(e)}'
            }
