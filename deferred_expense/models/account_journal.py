from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    deferred_expense = fields.Boolean(string='Deferred Expense', copy=False)
