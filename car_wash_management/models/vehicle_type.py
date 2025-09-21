from odoo import models, fields

class VehicleType(models.Model):
    _name = 'vehicle.type'
    _description = 'Vehicle Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Vehicle Type Name', required=True)
    description = fields.Text(string='Description')
    rate = fields.Float(string='Rate', required=True)
