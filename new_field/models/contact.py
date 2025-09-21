from odoo import models,fields,api

class ContactNumber(models.Model):
    _inherit ='sale.order'

    contact = fields.Integer(string='contact')