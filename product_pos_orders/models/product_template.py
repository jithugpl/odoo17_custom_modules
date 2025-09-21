from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pos_last_orders = fields.One2many(
        'pos.order',
        compute='_compute_pos_last_orders',
        string="Last 5 POS Orders"
    )

    @api.depends('id')
    def _compute_pos_last_orders(self):
        for product in self:
            pos_orders = self.env['pos.order'].search([
                ('lines.product_id', '=', product.id),
                ('state', '=', 'paid')  # or 'done' depending on your setup
            ], order='date_order desc', limit=5)
            product.pos_last_orders = pos_orders
