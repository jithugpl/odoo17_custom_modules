from odoo import models, fields, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'
    _order = 'id desc'

    monthly_expense_id = fields.Many2one('monthly.expense', string='monthly expense',  ondelete='set null')

    def button_cancel(self):
        for bill in self:
            deferred_expenses = self.env['deferred.expense.schedule'].search(
                [('vendor_bill_number', '=', bill.name), ('state', '!=', 'Cancel')])
            if deferred_expenses:
                raise ValidationError(
                    _("You cannot cancel this vendor bill because there are deferred expenses associated with it"))
        res = super(AccountMove, self).button_cancel()
        return res
