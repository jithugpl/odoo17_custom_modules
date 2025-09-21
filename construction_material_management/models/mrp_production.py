from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking')
