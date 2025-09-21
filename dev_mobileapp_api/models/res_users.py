from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    api_token = fields.Char(string="API Token", readonly=True)





class ProductReview(models.Model):
    _name = 'product.review'
    _description = 'Product Review'

    product_id = fields.Many2one('product.template', required=True)
    name = fields.Char(string='Reviewer Name')
    rating = fields.Integer(string='Rating', required=True)
    description = fields.Text(string='Review')