from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    date_order = fields.Datetime(related='order_id.date_order', store=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    last_5_pos_order_lines = fields.One2many(
        'pos.order.line', compute='_compute_last_5_pos_orders',
        string="Last 5 POS Orders", store=False
    )

    @api.depends('product_variant_ids')
    def _compute_last_5_pos_orders(self):
        for product in self:
            product.last_5_pos_order_lines = self.env['pos.order.line'].search([
                ('product_id', 'in', product.product_variant_ids.ids),
                ('order_id.state', '=', 'done')
            ], order='date_order desc', limit=5)
