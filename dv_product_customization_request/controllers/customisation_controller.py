import requests
from odoo import http
from odoo.http import request


class CustomisationController(http.Controller):

    @http.route('/product/customise/submit', type='http', auth="public", website=True, methods=['POST'])
    def submit_customisation(self, **post):
        product_id = int(post.get('product_id'))
        customisation_details = post.get('customisation_details')
        input_phone = post.get('contact_number')
        product = request.env['product.template'].sudo().browse(product_id)
        captcha_response = post.get('custom_captcha')

        # Validate CAPTCHA Checkbox
        if not captcha_response:
            return request.redirect('/shop')  # Redirect to shop or an error page


        if product.exists() and customisation_details:
            # Determine if the user is logged in
            user = request.env.user if request.env.user.id != http.request.website.user_id.id else None

            # Use logged-in user's phone number or the one provided in the form
            phone = user.phone if user and user.phone else input_phone

            # Create CRM opportunity
            request.env['crm.lead'].sudo().create({
                'name': f"Product Customisation Request: {product.name}",
                'type': 'opportunity',
                'description': customisation_details,
                'phone': phone,  # Save the determined phone number
                'product_id': product.id,
            })
            return request.render('dv_product_customization_request.success_page', {'product': product})

        return request.render('website.404')

