from odoo import models,fields,_,api

class AddPettyCash(models.Model):
    _inherit='account.account'

    # petty_cash_selection=fields.Boolean(string='Add Petty Cash',default=False)
    cash_account_selection=fields.Boolean(string='Cash Account',default=False)
    journal_id=fields.Many2one('account.journal',string='Journals')







