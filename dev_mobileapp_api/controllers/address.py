from odoo import http
from odoo.http import request, Response
import json
import logging


_logger = logging.getLogger(__name__)

class UserAddressController(http.Controller):

    # # code to update address in the main contact record
    @http.route('/user/address/update', type='json', auth='public', methods=['POST'], csrf=False)
    def update_user_address(self, **kwargs):
        try:
            # Extract token from Authorization header
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'error': 'Missing or invalid Authorization header'}

            token = auth_header.split(' ')[1]

            # Get the user based on token
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            if not user:
                return {'error': 'Invalid token'}

            # Get data
            data = json.loads(request.httprequest.data)
            street = data.get('street')
            street2 = data.get('street2')  # <-- Add this line
            city = data.get('city')
            # country_id = data.get('country_id')  # <-- India id:104
            country_name = data.get('country_id')  # accepting country name like 'India'
            country_id = None
            if country_name:
                country = request.env['res.country'].sudo().search([('name', '=', country_name)], limit=1)
                if country:
                    country_id = country.id
            # state_id = data.get('state_id')    # <-- kerala id:594
            state_name = data.get('state_id')  # accepting state name like 'Maharashtra'
            state_id = None
            if state_name and country_id:
                state = request.env['res.country.state'].sudo().search([
                    ('name', '=', state_name),
                    ('country_id', '=', country_id)
                ], limit=1)
                if state:
                    state_id = state.id
            zip_code = data.get('zip')
            mobile_no = data.get('mobile')
            phone_no = data.get('phone')
            email = data.get('email')
            tax_id = data.get('vat')
            website = data.get('website')
            title = data.get('title') # <-- Add id of titles
            # pan_no = data.get('l10n_in_pan')   # <-- value not adding in the field

            if not street or not city or not zip_code or not country_id:
                return {'error': 'Missing required fields'}

            # Update the main contact record (not child)
            user.partner_id.sudo().write({
                'street': street,
                'street2': street2,
                'city': city,
                'state_id': state_id,
                'zip': zip_code,
                'country_id': country_id,
                'mobile': mobile_no,
                'phone': phone_no,
                'email': email,
                'vat': tax_id,
                'website': website,
                'title': title,
                # 'l10n_in_pan': pan_no,   # <-- value not adding in the field
            })
            return {
                "status": True,
                "message": "Address added successfully",
                "data": {
                    'partner_id': user.partner_id.id,
                    "street": street,
                    "street2": street2,
                    "city": city,
                    "state_id": state_id,
                    "zip": zip_code,
                    "country_id": country_id,
                    "mobile": mobile_no,
                    "phone": phone_no,
                    "email": email,
                    "website": website,
                    'vat': tax_id,
                    'title': title,
                    # 'l10n_in_pan': pan_no, # <-- value not adding in the field(null)

                }
            }
            # return {
            #     'success': True,
            #     'message': 'Contact address updated successfully',
            #     'partner_id': user.partner_id.id
            # }

        except Exception as e:
            _logger.exception("Failed to update address")
            return {'error': str(e)}

        # code to create address in add address section(working code)(type:delivery in postman=delivery type address)
    @http.route('/user/address/add', type='json', auth='public', methods=['POST'], csrf=False)

    def add_user_address(self, **kwargs):
        try:
            # Extract Authorization Header
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'error': 'Missing or invalid Authorization header'}

            token = auth_header.split(' ')[1]

            # Find user with this token
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            if not user:
                return {'error': 'Invalid token'}

            # Get data
            data = json.loads(request.httprequest.data)
            name = data.get('name')
            street = data.get('street')
            street2 = data.get('street2')
            city = data.get('city')
            # country_id = data.get('country_id')  # <-- India id:104
            country_name = data.get('country_id')  # accepting country name like 'India'
            country_id = None
            if country_name:
                country = request.env['res.country'].sudo().search([('name', '=', country_name)], limit=1)
                if country:
                    country_id = country.id
            # state_id = data.get('state_id')    # <-- kerala id:594
            state_name = data.get('state_id')  # accepting state name like 'Maharashtra'
            state_id = None
            if state_name and country_id:
                state = request.env['res.country.state'].sudo().search([
                    ('name', '=', state_name),
                    ('country_id', '=', country_id)
                ], limit=1)
                if state:
                    state_id = state.id
            # state_id = data.get('state_id')
            zip_code = data.get('zip')
            # country_id = data.get('country_id')
            # address_type = data.get('type', 'contact') # <--contact type address
            # address_type = data.get('type', 'invoice') # <--invoice type address
            address_type = data.get('type', 'delivery') # <--delivery type address
            mobile_no = data.get('mobile')
            phone_no = data.get('phone')
            email = data.get('email')


            if not street or not city or not zip_code or not country_id:
                return {'error': 'Missing required fields'}

            # Create address
            address = request.env['res.partner'].sudo().create({
                'parent_id': user.partner_id.id,
                'type': address_type,
                'street': street,
                'street2': street2,
                'city': city,
                'state_id': state_id,
                'zip': zip_code,
                'country_id': country_id,
                'name': name,
                # 'name': user.name + "'s Address",
                'mobile': mobile_no,
                'phone': phone_no,
                'email': email
            })

            return {
                "status": True,
                "message": "Address added successfully",
                "data": {
                    "partner_id": user.partner_id.id,
                    "name" : name,
                    "street": street,
                    "street2": street2,
                    "city": city,
                    "state_id": state_id,
                    "zip": zip_code,
                    "country_id": country_id,
                    "mobile": mobile_no,
                    "phone": phone_no,
                    "email": email,
                    'address_id': address.id

            }
            }
            # return {
            #     'success': True,
            #     'message': 'Address added successfully',
            #     'address_id': address.id,
            # }

        except Exception as e:
            _logger.exception("Failed to add address")
            return {'error': str(e)}

    @http.route('/user/address/delete', type='json', auth='public', methods=['POST'], csrf=False)
    def delete_user_address(self, **kwargs):
        try:
            # Extract Authorization Header
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'error': 'Missing or invalid Authorization header'}

            token = auth_header.split(' ')[1]

            # Find user with token
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            if not user:
                return {'error': 'Invalid token'}

            # Get data
            data = json.loads(request.httprequest.data)
            address_id = data.get('address_id')

            if not address_id:
                return {'error': 'Missing address_id'}

            # Find the address under user's contact
            address = request.env['res.partner'].sudo().search([
                ('id', '=', address_id),
                ('parent_id', '=', user.partner_id.id)
            ], limit=1)

            if not address:
                return {'error': 'Address not found or unauthorized'}

            # Delete the address
            address.unlink()

            return {
                'status': True,
                'message': 'Address deleted successfully',
            }

        except Exception as e:
            _logger.exception("Failed to delete address")
            return {'error': str(e)}

    @http.route('/user/address/list', type='json', auth='public', methods=['GET'], csrf=False)
    def list_user_addresses(self, **kwargs):
        try:
            # Authorization
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'error': 'Missing or invalid Authorization header'}

            token = auth_header.split(' ')[1]
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            if not user:
                return {'error': 'Invalid token'}

            # Start with main address
            main_address = user.partner_id
            addresses = [main_address]

            # Add all child addresses
            child_addresses = request.env['res.partner'].sudo().search([
                ('parent_id', '=', main_address.id)
            ])
            addresses += child_addresses

            result = []
            for addr in addresses:
                result.append({
                    'address_id': addr.id,
                    'name': addr.name,
                    'type': addr.type or 'contact',  # Default to 'contact' if not set
                    'street': addr.street,
                    'street2': addr.street2,
                    'city': addr.city,
                    'state': addr.state_id.name if addr.state_id else '',
                    'zip': addr.zip,
                    'country': addr.country_id.name if addr.country_id else '',
                    'mobile': addr.mobile,
                    'phone': addr.phone,
                    'email': addr.email,
                    'is_main': addr.id == main_address.id  # Flag to identify main address
                })

            return {
                'status': True,
                'message': 'Address list retrieved successfully',
                'data': result
            }

        except Exception as e:
            _logger.exception("Failed to fetch addresses")
            return {'error': str(e)}

    # @http.route('/user/address/list', type='json', auth='public', methods=['GET'], csrf=False)
    # def list_user_addresses(self, **kwargs):
    #     try:
    #         # Extract Authorization Header
    #         auth_header = request.httprequest.headers.get('Authorization')
    #         if not auth_header or not auth_header.startswith('Bearer '):
    #             return {'error': 'Missing or invalid Authorization header'}
    #
    #         token = auth_header.split(' ')[1]
    #
    #         # Find user with token
    #         user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
    #         if not user:
    #             return {'error': 'Invalid token'}
    #
    #         # Fetch all child addresses of this user's partner
    #         addresses = request.env['res.partner'].sudo().search([
    #             ('parent_id', '=', user.partner_id.id)
    #         ])
    #
    #         result = []
    #         for addr in addresses:
    #             result.append({
    #                 'address_id': addr.id,
    #                 'name': addr.name,
    #                 'type': addr.type,
    #                 'street': addr.street,
    #                 'street2': addr.street2,
    #                 'city': addr.city,
    #                 'state': addr.state_id.name if addr.state_id else '',
    #                 'zip': addr.zip,
    #                 'country': addr.country_id.name if addr.country_id else '',
    #                 'mobile': addr.mobile,
    #                 'phone': addr.phone,
    #                 'email': addr.email,
    #             })
    #
    #         return {
    #             'status': True,
    #             'message': 'Address list retrieved successfully',
    #             'data': result
    #         }
    #
    #     except Exception as e:
    #         _logger.exception("Failed to fetch addresses")
    #         return {'error': str(e)}

    @http.route('/user/address/edit', type='json', auth='public', methods=['POST'], csrf=False)
    def edit_user_address(self, **kwargs):
        try:
            # Authorization
            auth_header = request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'error': 'Missing or invalid Authorization header'}

            token = auth_header.split(' ')[1]
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            if not user:
                return {'error': 'Invalid token'}

            # Get input data
            data = json.loads(request.httprequest.data)
            address_id = data.get('address_id')
            if not address_id:
                return {'error': 'Address ID is required'}

            address = request.env['res.partner'].sudo().browse(int(address_id))
            if not address.exists():
                return {'error': 'Address not found'}

            # Optional updated fields
            name = data.get('name')
            street = data.get('street')
            street2 = data.get('street2')
            city = data.get('city')
            zip_code = data.get('zip')
            mobile = data.get('mobile')
            phone = data.get('phone')
            email = data.get('email')
            address_type = data.get('type')

            # Handle country and state name (optional)
            country_name = data.get('country_id')
            country_id = None
            if country_name:
                country = request.env['res.country'].sudo().search([('name', '=', country_name)], limit=1)
                if country:
                    country_id = country.id

            state_name = data.get('state_id')
            state_id = None
            if state_name and country_id:
                state = request.env['res.country.state'].sudo().search([
                    ('name', '=', state_name),
                    ('country_id', '=', country_id)
                ], limit=1)
                if state:
                    state_id = state.id

            # Update fields
            address.write({
                'name': name or address.name,
                'street': street or address.street,
                'street2': street2 or address.street2,
                'city': city or address.city,
                'zip': zip_code or address.zip,
                'country_id': country_id or address.country_id.id,
                'state_id': state_id or address.state_id.id,
                'mobile': mobile or address.mobile,
                'phone': phone or address.phone,
                'email': email or address.email,
                'type': address_type or address.type,
            })

            return {
                'success': True,
                'message': 'Address updated successfully',
                'address_id': address.id
            }

        except Exception as e:
            _logger.exception("Failed to update address")
            return {'error': str(e)}

# class UserAddressController(http.Controller):

    # @http.route('/user/address/add', type='json', auth='public', methods=['POST'], csrf=False)
    # def add_user_address(self, **kwargs):
    #     try:
    #         user = request.env.user
    #
    #         # Expected fields from the POST body
    #         street = kwargs.get('street')
    #         city = kwargs.get('city')
    #         state_id = kwargs.get('state_id')  # Many2one to res.country.state
    #         zip_code = kwargs.get('zip')
    #         country_id = kwargs.get('country_id')  # Many2one to res.country
    #         address_type = kwargs.get('type', 'contact')  # default is 'contact'
    #         # mobile_no = kwargs.get('mobile')
    #
    #         if not street or not city or not zip_code or not country_id:
    #             return {'error': 'Missing required fields'}
    #
    #         # Create the address as a child contact of the current user
    #         address = request.env['res.partner'].sudo().create({
    #             'parent_id': user.partner_id.id,
    #             'type': address_type,
    #             'street': street,
    #             'city': city,
    #             'state_id': state_id,
    #             'zip': zip_code,
    #             'country_id': country_id,
    #             'name': user.name + "'s Address",
    #             # 'mobile': mobile_no
    #         })
    #
    #         return {
    #             'success': True,
    #             'message': 'Address added successfully',
    #             'address_id': address.id
    #         }
    #
    #     except Exception as e:
    #         return {'error': str(e)}

    # @http.route('/user/mobile/add', type='json', auth='public', methods=['POST'], csrf=False)
    # def add_mobile_number(self, **kwargs):
    #     try:
    #         user = request.env.user
    #         mobile = kwargs.get('mobile')
    #
    #         if not mobile:
    #             return {'error': 'Missing mobile number'}
    #
    #         # Update the user's partner record with new mobile number
    #         user.partner_id.sudo().write({'mobile': mobile})
    #
    #         return {
    #             'success': True,
    #             'message': 'Mobile number updated successfully',
    #             'mobile': mobile
    #         }
    #
    #     except Exception as e:
    #         return {'error': str(e)}