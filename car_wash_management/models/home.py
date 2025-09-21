from odoo import models, fields

class HomePage(models.Model):
    _name = 'home.page'
    _description = 'Home Page'
    _inherit = ['mail.thread', 'mail.activity.mixin']

