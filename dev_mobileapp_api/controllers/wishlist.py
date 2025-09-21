from odoo import http, models, exceptions
from odoo.http import request
import json
from datetime import datetime


class WishlistAPIController(http.Controller):

    def _authenticate_user(self):
        """Authenticate user with token and validate profile."""
        token = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            token = request.params.get('token', '')

        if not token:
            return (None, {'message': 'Missing authentication token'}, 401)

        user = request.env['res.users'].sudo().search(
            [('api_token', '=', token)],
            limit=1
        )

        if not user:
            return (None, {'message': 'Invalid token'}, 404)

        if not user.partner_id:
            return (None, {'message': 'User profile incomplete'}, 400)

        return (user, None, None)

    # ====== GET Wishlist ======
    @http.route('/api/wishlist/get', type='http', auth='none', methods=['GET'], csrf=False)
    def get_wishlist(self, **kwargs):
        """Get user's wishlist items using the product.wishlist model."""
        user, error, status = self._authenticate_user()
        if error:
            return self._error_response(error['message'], status)

        website = request.env['website'].get_current_website()
        Wishlist = request.env['product.wishlist'].with_user(user)
        items = Wishlist.search([
            ('partner_id', '=', user.partner_id.id),
            ('website_id', '=', website.id),
        ])

        data = [{
            'wishlist_id': item.id,
            'product_id': item.product_id.id,
            'name': item.product_id.name,
            'sku': item.product_id.default_code,
            'price': item.price,
            'currency': item.currency_id.name,
            'added_date': item.create_date.isoformat(),
        } for item in items]

        return request.make_response(
            json.dumps({'status': True, 'data': data}),
            headers=[('Content-Type', 'application/json')],
            status=200
        )

    # ====== ADD to Wishlist ======
    @http.route('/api/wishlist/add', type='http', auth='none', methods=['POST'], csrf=False)
    def add_to_wishlist(self, **kwargs):
        """Add a product to the user's wishlist."""
        user, error, status = self._authenticate_user()
        if error:
            return self._error_response(error['message'], status)

        try:
            data = json.loads(request.httprequest.data)
        except json.JSONDecodeError:
            return self._error_response("Invalid JSON format", 400)

        product_id = data.get('product_id')
        if not product_id:
            return self._error_response("Missing product_id", 400)

        product = request.env['product.product'].with_user(user).browse(int(product_id))
        if not product.exists():
            return self._error_response("Product not found", 404)

        website = request.env['website'].with_user(user).get_current_website()
        pricelist = website.pricelist_id
        Wishlist = request.env['product.wishlist'].with_user(user)
        if Wishlist.search([('partner_id', '=', user.partner_id.id), ('product_id', '=', product.id), ('website_id', '=', website.id)], limit=1):
            return self._error_response("Product already in wishlist", 409)

        price = product.with_context(pricelist=pricelist.id)._get_combination_info_variant()['price']

        Wishlist._add_to_wishlist(
            pricelist_id=pricelist.id,
            currency_id=pricelist.currency_id.id,
            website_id=website.id,
            price=price,
            product_id=product.id,
            partner_id=user.partner_id.id
        )

        return request.make_response(
            json.dumps({'status': True, 'message': 'Product added to wishlist'}),
            headers=[('Content-Type', 'application/json')],
            status=201
        )


    # ====== REMOVE from Wishlist ======
    @http.route('/api/wishlist/delete/<int:wishlist_id>', type='http', auth='none', methods=['DELETE'], csrf=False)
    def remove_from_wishlist(self, wishlist_id, **kwargs):
        """Remove a product from the user's wishlist."""
        user, error, status = self._authenticate_user()
        if error:
            return self._error_response(error['message'], status)

        Wishlist = request.env['product.wishlist'].with_user(user)
        item = Wishlist.search([('id', '=', wishlist_id), ('partner_id', '=', user.partner_id.id)], limit=1)
        if not item:
            return self._error_response("Wishlist item not found", 404)

        try:
            item.unlink()
        except Exception as e:
            return self._error_response(f"Error removing item: {e}", 500)

        return request.make_response(
            json.dumps({'status': True, 'message': 'Product removed from wishlist'}),
            headers=[('Content-Type', 'application/json')],
            status=200
        )

    def _error_response(self, message, status_code):
        """Standard error response format"""
        return request.make_response(
            json.dumps({'status': False, 'message': message}),
            headers=[('Content-Type', 'application/json')],
            status=status_code
        )
