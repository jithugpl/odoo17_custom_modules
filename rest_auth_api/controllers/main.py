from odoo import http,fields
from odoo.http import request
import json
import logging
from datetime import datetime
from werkzeug.exceptions import BadRequest, Unauthorized, Conflict, InternalServerError


_logger = logging.getLogger(__name__)

class AuthAPI(http.Controller):

    @http.route('/api/signup', type='json', auth='public', methods=['POST'], csrf=False)
    def signup(self, **kwargs):
        try:
          
            vals = kwargs 
            _logger.info(f"Received signup request: {vals}")
            required_fields = ['name', 'login', 'password']
            
            if not all(field in vals for field in required_fields):
                raise BadRequest("Missing required fields: name, login, password")

            if len(vals['password']) < 8:
                raise BadRequest("Password must be at least 8 characters")

            if request.env['res.users'].sudo().search([('login', '=', vals['login'])]):
                raise Conflict("User with this login already exists")

            user = request.env['res.users'].sudo().create({
                'name': vals['name'],
                'login': vals['login'],
                'password': vals['password'],
            })
            return {"status": "success", "user_id": user.id}
        except Exception as e:
            _logger.error("Signup error: %s", str(e))
            raise InternalServerError(str(e))
        
    @http.route('/api/login', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        try:
            vals = kwargs
            print(vals)
            if not vals:
                raise BadRequest("Request body must be in JSON format")

            login = vals.get('login')
            password = vals.get('password')

            if not login or not password:
                raise BadRequest("Login and password are required")
            user_agent_env = request.env(user=request.env.user)
            uid = request.env['res.users'].sudo()._login(request.db, login, password, user_agent_env)
            
            if not uid:
                raise Unauthorized("Invalid credentials")

            user = request.env['res.users'].sudo().browse(uid)

            # Generate dummy token (replace with secure logic)
            token = user._generate_token()

            return {
                "status": "success",
                "user_id": user.id,
                "token": token
            }

        except BadRequest as e:
            _logger.error("Login error: %s", str(e))
            raise
        except Unauthorized as e:
            _logger.error("Login failed: %s", str(e))
            raise
        except Exception as e:
            _logger.error("Login exception: %s", str(e))
            raise InternalServerError("Internal server error")
        
    @http.route('/api/profile', type='json', auth='public', methods=['POST'], csrf=False)
    def profile(self, **kwargs):
        try:
            # Extract Bearer token from Authorization header
            auth_header = request.httprequest.headers.get('Authorization')
            print(auth_header)
            if not auth_header or not auth_header.startswith('Bearer '):
                return {
                    "status": "error",
                    "message": "Invalid or missing Authorization header (use Bearer <token>)"
                }

            token = auth_header.replace('Bearer ', '').strip()

            # Find user with the given token
            user = request.env['res.users'].sudo().search([('auth_token', '=', token)], limit=1)

            if not user:
                return {"status": "error", "message": "Unauthorized: Invalid token"}

            print(user.auth_token_expiry)
            print(fields.Datetime.now())

            # Check token expiry
            if user.auth_token_expiry and user.auth_token_expiry < fields.Datetime.now():
                return {"status": "error", "message": "Token has expired"}

            # Respond with user profile
            return {
                "status": "success",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "login": user.login,
                }
            }

        except Exception as e:
            _logger.error("Profile error: %s", str(e))
            return {"status": "error", "message": "Internal server error"}
        
    @http.route('/api/fetch-all-products', type='json', auth='public', methods=['POST'], csrf=False)
    def fetch_all_products(self, **kwargs):
        try:
            # Extract Bearer token from header
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {
                    "status": "error",
                    "message": "Invalid or missing Authorization header (use Bearer <token>)"
                }

            token = auth_header.replace('Bearer ', '').strip()

            # Find user by token
            user = request.env['res.users'].sudo().search([('auth_token', '=', token)], limit=1)

            # Check token validity
            if not user:
                return {"status": "error", "message": "Unauthorized: Invalid token"}

            if user.auth_token_expiry and user.auth_token_expiry < fields.Datetime.now():
                return {"status": "error", "message": "Token has expired"}

            # Fetch products
            products = request.env['product.template'].sudo().search([], limit=10)

            return {
                "status": "success",
                "products": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "price": p.list_price
                    } for p in products
                ]
            }

        except Exception as e:
            _logger.error("Product fetch error: %s", str(e))
            return {"status": "error", "message": "Internal server error"}
        
    @http.route('/api/product-filter-price', type='json', auth='public', methods=['POST'], csrf=False)
    def product_filter_price(self, **kwargs):
        try:
            # Token validation
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {
                    "status": "error",
                    "message": "Invalid or missing Authorization header (use Bearer <token>)"
                }

            token = auth_header.replace('Bearer ', '').strip()
            user = request.env['res.users'].sudo().search([('auth_token', '=', token)], limit=1)

            if not user:
                return {"status": "error", "message": "Unauthorized: Invalid token"}

            if user.auth_token_expiry and user.auth_token_expiry < fields.Datetime.now():
                return {"status": "error", "message": "Token has expired"}

            # Get filter values from payload
            min_price = kwargs.get('min_price', 0)
            max_price = kwargs.get('max_price', float('inf'))

            # Search domain
            domain = [('list_price', '>=', min_price)]
            if max_price != float('inf'):
                domain.append(('list_price', '<=', max_price))

            # Query products
            products = request.env['product.template'].sudo().search(domain)

            return {
                "status": "success",
                "products": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "price": p.list_price
                    } for p in products
                ]
            }

        except Exception as e:
            _logger.error("Product price filter error: %s", str(e))
            return {"status": "error", "message": "Internal server error"}

    @http.route('/api/product-search-name', type='json', auth='public', methods=['POST'], csrf=False)
    def product_search_by_name(self, **kwargs):
        try:
            # Auth validation
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {
                    "status": "error",
                    "message": "Invalid or missing Authorization header (use Bearer <token>)"
                }

            token = auth_header.replace('Bearer ', '').strip()
            user = request.env['res.users'].sudo().search([('auth_token', '=', token)], limit=1)

            if not user:
                return {"status": "error", "message": "Unauthorized: Invalid token"}

            if user.auth_token_expiry and user.auth_token_expiry < fields.Datetime.now():
                return {"status": "error", "message": "Token has expired"}

            # Get search term
            search_term = kwargs.get('search', '').strip()

            if not search_term:
                return {"status": "error", "message": "Search term is required"}

            # Perform case-insensitive name search
            products = request.env['product.template'].sudo().search([
                ('name', 'ilike', search_term)
            ])

            return {
                "status": "success",
                "products": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "price": p.list_price
                    } for p in products
                ]
            }

        except Exception as e:
            _logger.error("Product name search error: %s", str(e))
            return {"status": "error", "message": "Internal server error"}

