from odoo import http
from odoo.http import request

class OwlDemoController(http.Controller):

    @http.route('/owl_demo', type='http', auth="user", website=False)
    def owl_demo_page(self):
        return request.render("owl_demo.owl_demo_page")
