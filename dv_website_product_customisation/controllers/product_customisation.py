# from odoo import http
# from odoo.http import request
#
# class ProductCustomization(http.Controller):
#
#     @http.route('/customization/submit', type='http', auth='public', methods=['POST'], csrf=True, website=True)
#     def submit_customization(self, **kwargs):
#         product_id = kwargs.get('product_id')
#         customization_details = kwargs.get('customization_details')
#         print("product custom data...........",product_id,customization_details)
#         previous_url = request.httprequest.referrer or '/'
#
#         return request.redirect(previous_url)