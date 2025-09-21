from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MonthlyExpense(models.Model):
    _name = "monthly.expense"
    _description = "Monthly Expense"

    debit_account = fields.Many2one('account.account', string='Debit Account')
    debit_amount = fields.Float(string='Debit Amount')
    credit_account = fields.Many2one('account.account', string='Credit Account')
    credit_amount = fields.Float(string='Credit Amount')
    date = fields.Date(string='Date')
    filter_id = fields.Many2one('deferred.expense.filter', string='Filter', ondelete='cascade')
    move_id = fields.Many2one('account.move', string='move', ondelete='cascade')
    reference = fields.Char(string='reference')
    journal_entry = fields.Char(string='Journal Entry Name')
    expense_id = fields.Many2one('deferred.expense.data',ondelete='cascade')
    journal_id = fields.Many2one('account.journal', string='journal', related='filter_id.journal_id')


class DeferredExpenseFilter(models.Model):
    _name = 'deferred.expense.filter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Deferred Expense Filter'
    _rec_name = 'reference'

    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    monthly_expense_ids = fields.One2many('monthly.expense', 'filter_id', string='Monthly Expenses', ondelete='cascade')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('post', 'Posted'),
        ('cancel', 'Cancel')
    ], default='draft', string='Status', required=True, tracking=True)
    journal_id = fields.Many2one('account.journal', string='journal', required=True, tracking=True)
    accounting_date = fields.Date(string='Accounting Date', default=lambda self: fields.Date.today(), tracking=True)
    is_generated = fields.Boolean(string='Data Generated', compute='_compute_is_generated', store=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    journal_entry = fields.Char(string='Journal Entry Name')

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('monthly.expense') or _('New')
        res = super(DeferredExpenseFilter, self).create(vals)
        return res

    def action_reset_to_draft(self):
        move_obj = self.env['account.move'].search([('monthly_expense_id', 'in', self.monthly_expense_ids.ids)])
        for move in move_obj:
            move.button_cancel()

        self.state = 'draft'
        for expense in self.monthly_expense_ids:
            expense.expense_id.status = False
            expense.journal_entry = ''
            expense.expense_id.journal_entry = ''

    def action_open_journal_entries(self):
            return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entries',
            'view_mode': 'tree,form',
            'res_model': 'account.move',


        }

    def action_cancel(self):
        self.state = 'cancel'

    def action_apply_filter(self):


        start_date = self.start_date
        end_date = self.end_date
        previous_records = self.env['monthly.expense'].search([
            ('filter_id', '=', self.id)
        ])
        previous_records.unlink()

        expense_data = self.env['deferred.expense.data'].search([
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('schedule_id.state', '!=', 'Cancel'),
            ('status', '=', False)

        ])
        report_data = []
        for record in expense_data:

            if record.debit_account.id and record.credit_account.id and record.debit_amount and record.credit_amount:
                report_data.append({
                    'debit_account': record.debit_account.id,
                    'debit_amount': record.debit_amount,
                    'credit_account': record.credit_account.id,
                    'credit_amount': record.credit_amount,
                    'date': self.accounting_date,
                    'filter_id': self.id,
                    'reference': record.reference,
                    'expense_id': record.id,

                })
        self.env['monthly.expense'].create(report_data)
        self.is_generated = True
        return True

    def unlink(self):
        raise ValidationError("You cannot delete the record")

    def action_post(self):
        for record in self:
            if not record.monthly_expense_ids:
                raise ValidationError("Cannot post without any expense")
        for expense in self.monthly_expense_ids:
            move_obj = self.env['account.move']
            move_vals = {
                'journal_id': self.journal_id.id,
                'date': expense.date,
                'ref': self.reference,
                'monthly_expense_id': expense.id,
                'move_type': 'entry',
                'line_ids': [
                    (0, 0, {'account_id': expense.debit_account.id,
                            'debit': expense.debit_amount,
                            'credit': 0.0, }),
                    (0, 0, {'account_id': expense.credit_account.id,
                            'debit': 0.0,
                            'credit': expense.credit_amount, }),
                ]
            }
            move = move_obj.create(move_vals)
            move.action_post()
            expense.write({'journal_entry': move.name})
            expense.expense_id.status = True
            expense.expense_id.journal_entry = move.name

        self.state = 'post'
