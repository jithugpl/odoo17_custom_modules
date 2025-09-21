from odoo import models, fields


class MaterialRequestInherited(models.Model):
    _inherit = 'stock.picking'