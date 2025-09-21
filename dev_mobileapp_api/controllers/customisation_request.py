from odoo import http
from odoo.http import request, Response
import json


class CustomisationRequestAPI(http.Controller):
# get customisation request api
    @http.route('/api/customisation_requests', auth='public', type='json', methods=['GET'], csrf=False)
    def get_customisation_requests(self, **kwargs):
        """Fetch all product customisation requests"""
        leads = request.env['crm.lead'].sudo().search([('product_id', '!=', False)])
        result = []
        for lead in leads:
            result.append({
                'id': lead.id,
                'product_name': lead.product_id.name,
                'product_id': lead.product_id.id,
                'customisation_details': lead.description,
                'phone': lead.phone,
                'created_by': lead.create_uid.name,
                'create_date': lead.create_date.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return {'status': 200, 'data': result}


# post customisation request api
    @http.route('/api/customisation/request', auth='public', type='json', methods=['POST'], csrf=False)
    def create_customisation_request(self):
        """Create a new product customisation request"""
        try:

            data = request.httprequest.get_json(force=True)  # 💡 works reliably for JSON
            product_id = int(data.get('product_id', 0))
            description = data.get('customisation_details', '')
            phone = data.get('contact_number', '')

            if not product_id or not description:
                return {'status': 400, 'message': 'Missing product_id or customisation_details'}

            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return {'status': 404, 'message': 'Product not found'}

            # Get the current user
            # current_user = request.env.user

            lead = request.env['crm.lead'].sudo().create({
                'name': f"Product Customisation Request: {product.name}",
                'type': 'opportunity',
                'description': description,
                'phone': phone,
                'product_id': product.id,
                # 'user_id': current_user.id,  # 👈 Set current user as the Salesperson
            })

            return {
                'status': 201,
                'message': 'Customisation request created successfully',
                'data': {
                    'id': lead.id,
                    'product_name': product.name,
                    'description': description,
                    'phone': phone,
                    # 'salesperson': current_user.name

                    }
            }

        except Exception as e:
            return {'status': 500, 'message': 'Internal server error', 'error': str(e)}


