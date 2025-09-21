from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    petty_cash_limit = fields.Float(string='Amount')
    petty_cash_site_limit = fields.Boolean(string='Petty cash', default=False)
