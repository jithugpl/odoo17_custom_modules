# models/account_move.py

from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_new_field = fields.Char(string='New Field')
