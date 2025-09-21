from odoo import models, fields

class CarWashType(models.Model):
    _name = 'car.wash.type'
    _description = 'Car Wash Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Wash Type', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    duration = fields.Integer(string='Duration (Minutes)')