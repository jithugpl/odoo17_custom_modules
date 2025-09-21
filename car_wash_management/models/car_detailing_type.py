from odoo import models, fields

class CarDetailingType(models.Model):
    _name = 'car.detailing.type'
    _description = 'Car Detailing Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Detailing Type', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    duration = fields.Integer(string='Duration (Minutes)')