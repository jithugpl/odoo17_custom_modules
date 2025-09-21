from odoo import models, fields

class ProductCustomisation(models.Model):
    _inherit = 'crm.lead'

    product_id = fields.Many2one('product.template', string="Product", required=False)
