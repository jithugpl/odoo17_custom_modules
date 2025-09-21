from odoo import http
from odoo.http import request

class ProductCustomizationController(http.Controller):

    # @http.route('/customization/submit', type='http', auth='public', methods=['POST'], csrf=True, website=True)
    # def submit_customization(self, **kwargs):
    #     """Handle the submission of the customization form."""
    #     product_id = kwargs.get('product_id')
    #     customization_details = kwargs.get('customization_details')
    #
    #     if not product_id or not customization_details:
    #         return request.render('website.404')  # Render an error page if data is incomplete
    #
    #     try:
    #         # Create the customization request
    #         customization_request = request.env['product.customization.request'].sudo().create({
    #             'product_id': int(product_id),
    #             'customization_details': customization_details,
    #         })
    #
    #         # Trigger the opportunity creation
    #         customization_request.action_submit()
    #
    #         # Redirect to a success page
    #         return request.redirect('/thank-you')  # Replace with your actual success page
    #     except Exception as e:
    #         return request.render('website.500', {'error_message': str(e)})  # Render a generic error page



        @http.route('/customization/submit', type='http', auth="public", website=True, methods=['POST'], csrf=True)
        def submit_customization(self, **post):
            product_id = post.get('product_id')
            customisation_details = post.get('customization_details')

            # Ensure product_id and customization_details are provided
            if not product_id or not customisation_details:
                return request.render('website.http_error', {
                    'status_code': 400,
                    'message': "Product or customization details are missing!",
                })

            # Fetch product and validate it exists
            product = request.env['product.template'].sudo().search([('id', '=', int(product_id))], limit=1)
            if not product:
                return request.render('website.http_error', {
                    'status_code': 404,
                    'message': "Product not found!",
                })

            # Create CRM opportunity
            request.env['crm.lead'].sudo().create({
                'name': f"Customisation for {product.name}",
                'type': 'opportunity',
                'description': customisation_details,
            })

            # Redirect to a thank-you page or return success response
            return request.redirect('/thank-you')

