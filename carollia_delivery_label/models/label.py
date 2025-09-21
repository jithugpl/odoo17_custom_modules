from odoo import models, fields


class DeiveryLabel(models.Model):
    _inherit = 'product.product'

    manufacturing_date = fields.Date(string='Manufacturing Date')
    net_quantity = fields.Integer(string='Net Quantity', default=1)
    brand = fields.Char(string='Brand')
    # color = fields.Char(string='Color')
    # size = fields.Char(string='Size')
    # style_code = fields.Char(related='product_tmpl_id.style_code', string='Style Code', store=True)
    # default_code = fields.Char(related='product_tmpl_id.default_code', store=True)




class DeiveryLabels(models.Model):
    _inherit = 'product.template'

    manu_date = fields.Date(string='Manufacturing Date')

    manufacturing_date = fields.Date(
        related='product_variant_ids.manufacturing_date',
        store=True
    )


