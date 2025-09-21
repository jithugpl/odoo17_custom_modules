import secrets
import logging
import requests
from random import choice
import string
import pytz
from datetime import datetime, timedelta
from odoo import http
from odoo.http import request
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError
import  json

_logger = logging.getLogger(__name__)

class MobAuthController(http.Controller):

    @http.route('/auth/signup', type='json', auth='public', methods=['POST'], csrf=False)
    def customer_signup(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            print("data : ", data)
            print("kwargs", kwargs)
            name = data.get('name')
            print("Name:", name)
            login = data.get('login')
            print("Login:", login)
            phone = data.get('phone')
            print("Phone:", phone)
            password = data.get('password')
            print("Password:", password)
            _logger.info(f"[SIGNUP] Received request: {kwargs}")

            if not all([name, login, password]):
                raise BadRequest("Missing required fields: name, login, password")

            if request.env['res.users'].sudo().search([('login', '=', login)]):
                raise Conflict("User with this login already exists")

            # Generate API token
            token = secrets.token_urlsafe(32)

            # creating portal user
            user_id = request.env['res.users'].sudo().create({
                'name': name,
                'login': login,
                'email': login,
                'password': password,
                'api_token': token,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
            })

            # creating partner
            if not  user_id.partner_id:
                request.env['res.partner'].sudo().create({
                    'name': name,
                    'email': login,
                    'phone': phone,
                    'user_id': user_id.id,
                })
            # if user_id:
            #     request.env['res.partner'].sudo().create({
            #         'name': name,
            #         'email': login,
            #         'phone': phone,
            #         'user_id': user_id.id,
            #     })

            return {
                "status": "success",
                "message": "User registered successfully",
                "user_id": user_id.id,
                "token": token,
            }

        except BadRequest as e:
            _logger.warning(f"[SIGNUP] Bad Request: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

        except Conflict as e:
            _logger.warning(f"[SIGNUP] Conflict: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

        except Exception as e:
            _logger.exception("[SIGNUP] Internal Server Error")
            return {
                "status": "error",
                "message": "Something went wrong on our end. Please try again later."
            }

    @http.route('/auth/login', type='json', auth='public', methods=['POST'], csrf=False)
    def customer_login(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            print(data)
            email = data.get('login')
            password = data.get('password')
            print(email)
            print(password)

            if not all([email,password]):
                return {
                    "status": False,
                    "message": "Email and password are required"
                }

            session_user = request.env(user=request.env.user)
            user_id = request.env['res.users'].sudo()._login(request.db, email, password, session_user)
            if not user_id:
                _logger.exception("Invalid credentials")
                return {
                    "status": False,
                    "message": "Invalid credentials"
                }
            uid = request.env['res.users'].sudo().browse(user_id)

            if not uid.api_token:
                token = secrets.token_urlsafe(32)
                uid.sudo().write({'api_token': token})
            return {
                "status": True,
                "message": "Login successful",
                "token": uid.api_token,
            }

        except Exception as e:
            _logger.exception("Login API failed")
            return {
                "status": False,
                "message": "Something went wrong on our end. Please try again later."
            }


    @http.route('/auth/forgot-password/request-otp', type='json', auth='public', methods=['POST'], csrf=False)
    def request_otp(self, **kwargs):
        try:
            phone = kwargs.get('phone')
            if not phone:
                return {
                    "status": False,
                    "message": "Phone number is required"
                }

            user = request.env['res.users'].sudo().search([('phone', '=', phone)], limit=1)

            if not user:
                return {
                    "status": False,
                    "message": "Phone number not registered"
                }
            OTP = self.generate_otp(4)
            vals = {
                'otp': OTP,
                'email': user.login,
                'phone': phone,
            }

            send_sms = self.send_sms_otp(phone,OTP)
            if send_sms:
                res = request.env['otp.verification'].sudo().create(vals)
                _logger.info(f"OTP for phone {phone}: {OTP}")  # For testing

                return {
                    "status": True,
                    "message": "OTP sent to the registered phone number"
                }
            else:
                _logger.exception("send_sms is False")
                return {
                    "status": False,
                    "message": "Something went wrong on our end. Please try again later."
                }
        except Exception as e:
            _logger.exception("Failed to send OTP")
            return {
                "status": False,
                "message": "Something went wrong on our end. Please try again later."
            }

    @http.route('/auth/forgot-password/verify-otp', type='json', auth='public', methods=['POST'], csrf=False)
    def verify_otp(self, **kwargs):
        try:
            phone = kwargs.get('phone')
            otp = kwargs.get('otp')
            otp_id = request.env['otp.verification'].sudo().search([('phone', '=', phone),('otp','=',otp)], limit=1)
            if otp_id:
                expiration_time = datetime.utcnow() - timedelta(minutes=1)

                if otp_id.create_date < expiration_time:
                    otp_id.sudo().unlink()
                    return {
                        'status': False,
                        'message': 'OTP expired. Please request a new one.'
                    }
                else:
                    otp_id.sudo().write({'state': 'verified'})
                    return {
                        'status': True,
                        'message': 'OTP verified successfully.'
                    }
            return {
                'status': False,
                'message': 'Invalid OTP or phone number.'
            }

        except Exception as e:
            _logger.exception("Failed to Verify OTP")
            return {
                "status": False,
                "message": "Something went wrong on our end. Please try again later."
            }

    @http.route('/auth/forgot-password/reset', type='json', auth='public', methods=['POST'], csrf=False)
    def reset_password(self, **kwargs):
        try:
            phone = kwargs.get('phone')
            new_password = kwargs.get('new_password')
            confirm_password = kwargs.get('confirm_password')

            if not all([phone, new_password, confirm_password]):
                return {
                    "status": False,
                    "message": "Phone, OTP, new password, and confirm password are required."
                }

            otp_id = request.env['otp.verification'].sudo().search([
                ('phone', '=', phone),
                ('state', '=', 'verified')
            ], limit=1)

            if not otp_id:
                return {
                    "status": False,
                    "message": "OTP verification required"
                }

            if new_password != confirm_password:
                return {
                    "status": False,
                    "message": "Passwords do not match"
                }

            user = request.env['res.users'].sudo().search([
                ('partner_id.phone', '=', phone)
            ], limit=1)

            if not user:
                return {
                    "status": False,
                    "message": "Phone number not registered"
                }

            user.sudo().write({'password': new_password})
            otp_id.sudo().unlink()

            return {
                "status": True,
                "message": "Password reset successfully"
            }

        except Exception as e:
            _logger.exception("Error in reset-password")
            return {
                "status": False,
                "message": "Something went wrong on our end. Please try again later."
            }

    @http.route('/auth/logout', type='json', auth='public', methods=['POST'], csrf=False)
    def logout(self, **kwargs):
        try:
            token = kwargs.get('token')

            if not token:
                return {
                    "status": False,
                    "message": "Invalid or missing authentication token"
                }

            user = request.env['res.users'].sudo().search([
                ('api_token', '=', token)
            ], limit=1)

            if not user:
                return {
                    "status": False,
                    "message": "Invalid or missing authentication token"
                }

            user.sudo().write({'api_token': False})

            return {
                "status": True,
                "message": "Logged out successfully"
            }

        except Exception as e:
            _logger.exception("Logout API failed")
            return {
                "status": False,
                "message": "Something went wrong on our end. Please try again later."
            }


    # OTP Creation
    def generate_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp

    # sending sms
    def send_sms_otp(self,phone,OTP):
        try:
            sms_url = "https://prutech.org/SMS/api/broadcast"
            auth_url = "https://prutech.org/SMS/api/token"
            auth_payload = {
                "username": "rajesh@datavalley.in",
                "password": "wWPe%VOO*V^?*Zh"
            }

            auth_response = requests.post(auth_url, json=auth_payload)

            if auth_response.status_code == 200:
                token = auth_response.json().get("token")

                sms_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }

                sms_payload = {
                    "pingBackType": "0",
                    "pingBackId": "0",
                    "jsonData": {
                        "senderId": "CARLIA",
                        "templateId": "1107173563435236694",
                        "templateName": "carollia user registration (www.carollia.com)",
                        "unicodeStatus": 0,
                        "messages": [
                            {
                                "msisdn": phone,  # Mobile number to send SMS
                                "message": f"Your OTP for Carollia registration is {OTP}. It is valid for 10 minutes. Do not share it with anyone",
                            }
                        ]
                    }
                }

                sms_response = requests.post(sms_url, headers=sms_headers, json=sms_payload)

                if sms_response.status_code == 200:
                    sms_result = sms_response.json()
                    _logger.info("SMS Response -> %s", sms_result)
                    _logger.info("OTP sent successfully to %s", phone)
                    return True

                else:
                    _logger.error("Failed to send OTP to %s: %s", phone, sms_response.text)
                    return False
            else:
                _logger.error("Failed to authenticate with SMS gateway: %s", auth_response.text)
                return False
        except Exception as e:
            _logger.error("Error while sending OTP via SMS: %s", str(e))
            return False




class ProductTemplateController(http.Controller):
    @http.route('/products', type='http', auth='public', methods=['GET'], cors='*')
    def get_products(self):
        try:
            products = request.env['product.template'].sudo().search([('active', '=', True)])
            for product in products:
                fields = product.fields_get()
                for field_name in fields:
                    value = getattr(product, field_name, None)
                    print(f"{field_name}: {value}")
                print("-----")
            # product_list = [{'id': p.id, 'name': p.name or '', 'description':p.description,'weight':p.weight,} for p in products]
            product_list = [{
                'id': p.id,   #Unique product identifier
                'name': p.name or '',
                'description': p.description or '',
                'description_sale': p.description_sale or '', #Long description shown to users
                'ecommerce description': p.description_ecommerce or '',
                'weight': p.weight or 0.0,
                'volume': p.volume or 0.0,
                'compare to price': p.compare_list_price or 0.0,
                'list_price': p.list_price or 0.0,
                'default_code': p.default_code or '',

                'tags': [tag.name for tag in p.product_tag_ids] if p.product_tag_ids else [],  # 👈 Here you get tags
                'public_categories': [{'id': cat.id, 'name': cat.name} for cat in
                                      p.public_categ_ids] if p.public_categ_ids else [],
                'type': p.type or '',
                'uom_id': p.uom_id.name if p.uom_id else '',
                'categ_id': p.categ_id.name if p.categ_id else '', #Product category
                'active': p.active,
                # 'care_guide_id':p.care_guide_id, #Care guide
                 'material_id': p.material_id.name if p.material_id else '', #Material
                'out_of_stock_message': p.out_of_stock_message or '',#
                'on_hand_qty': p.qty_available or 0.0,
                'show_availability':p.show_availability, #Whether to show availability
                'is_published': p.is_published, #Whether product is published on website
                'variant_available': len(p.product_variant_ids) or '0',
                'variants': [{
                    'id': variant.id,
                    'name': variant.name,
                    'price': variant.list_price,
                    'internal reference': variant.default_code,
                    'attribute_values': [{
                        'attribute': attr_value.attribute_id.name,
                        'value': attr_value.name
                    } for attr_value in variant.product_template_variant_value_ids]
                } for variant in p.product_variant_ids],

                'attributes': [
                    {
                        'attribute_name': value.attribute_id.name,
                        'value_name': value.name
                    }
                    for variant in p.product_variant_ids
                    for value in variant.product_template_attribute_value_ids
                ],





            } for p in products]

            return request.make_response(
                json.dumps({
                    'status': True,
                    'message': 'Product list fetched successfully',
                    'data': product_list
                }),
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            _logger.error("Error fetching products: %s", str(e))
            return request.make_response(
                json.dumps({
                    'status': False,
                    'message': 'Unable to fetch products at the moment. Please try again later.'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )