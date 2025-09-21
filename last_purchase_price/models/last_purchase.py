from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AdditionalItemsLines(models.Model):
    _inherit = 'purchase.order.line'


    # last_purchase_price = fields.Boolean(string='Last Purchase Price', default=False , readonly=True )
    last_purchase_price = fields.Float(
        string="last_purchase_price",
        related='product_id.product_tmpl_id.standard_price',
        readonly=True,
        store=True
    )