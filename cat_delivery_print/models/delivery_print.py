from odoo import fields,models,api


class Saleordername(models.Model):
    _inherit = 'sale.order.line'
