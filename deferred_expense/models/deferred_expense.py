from odoo import models, fields, api, _
from calendar import monthrange
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class DeferredExpenseSchedule(models.Model):
    _name = 'deferred.expense.schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Deferred Expense Schedule'
    _rec_name = 'reference'

    reference = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    debit_account = fields.Many2one('account.account', string='Debit Account', required=True, tracking=True)
    credit_account = fields.Many2one('account.account', string='Credit Account', required=True, tracking=True)
    amount = fields.Float(string='Total Amount', required=True, tracking=True)
    number_of_month = fields.Integer(string='Number of Months', compute='compute_number_of_month', store=True)
    date = fields.Date(string='Start Date', help='Select start date here', required=True, tracking=True)
    end_date = fields.Date(string='End Date', help='select end date here', required=True, tracking=True)

    generated_data_ids = fields.One2many('deferred.expense.data', 'schedule_id', string='Generated Data',
                                         ondelete='cascade')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('Cancel', 'Cancel')

    ], default='draft', string='status', required=True, tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    vendor_bill_number = fields.Char(string='Vendor Bill Number', readonly=True)

    @api.constrains('debit_account', 'credit_account', 'amount')
    def account_selection(self):
        for rec in self:
            if rec.debit_account == rec.credit_account:
                raise ValidationError('You cannot choose same account for credit and debit')
            if rec.amount <= 0:
                raise ValidationError('Amount must be greater than zero')

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('deferred.expense') or _('New')
        res = super(DeferredExpenseSchedule, self).create(vals)
        return res

    @api.depends('date', 'end_date')
    def compute_number_of_month(self):
        for rec in self:
            if rec.date and rec.end_date:
                start_date = fields.Date.from_string(rec.date)
                end_date = fields.Date.from_string(rec.end_date)
                rec.number_of_month = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
            else:
                rec.number_of_month = 0

    def action_schedule(self):
        for rec in self:
            for l in rec.generated_data_ids:
                if l.status == True:
                    raise ValidationError("you cannot generate again")
            if rec.date > rec.end_date:
                raise UserError(_('The End Date cannot be earlier than the Start Date.'))

            if rec.number_of_month <= 0:
                raise UserError(_('The number of months must be greater than zero.'))

            rec.generated_data_ids.unlink()
            data = []
            start_date = fields.Date.from_string(rec.date)
            end_date = fields.Date.from_string(rec.end_date)
            total_amount = rec.amount
            total_days = (end_date - start_date).days + 1
            per_day_amount = total_amount / total_days

            for i in range(rec.number_of_month + 1):
                month_date = start_date + relativedelta(months=i)
                if i == 0:
                    start_day = start_date.day
                    days_in_month = monthrange(month_date.year, month_date.month)[1] - start_day + 1
                    expense = days_in_month * per_day_amount
                elif i == rec.number_of_month:
                    end_date = rec.end_date
                    end_day = end_date.day
                    expense = end_day * per_day_amount
                    month_date = end_date
                else:
                    month_date = start_date + relativedelta(months=i)
                    days_in_month = monthrange(month_date.year, month_date.month)[1]
                    expense = days_in_month * per_day_amount
                data.append({
                    'date': month_date,
                    'amount': expense,
                    'schedule_id': rec.id,
                    'debit_account': rec.debit_account.id,
                    'credit_account': rec.credit_account.id,
                    'debit_amount': expense,
                    'credit_amount': expense,
                    'status': False,
                    'reference': rec.reference
                })

            self.env['deferred.expense.data'].create(data)

        return True

    def action_cancel(self):
        for record in self:
            for g in record.generated_data_ids:
                if g.status == True:
                    raise ValidationError(
                        'you cannot cancel this record as there are posted journal entries associated with this')
                record.state = 'Cancel'

    def action_approve(self):
        for record in self:
            record.state = 'approved'


class DeferredExpenseData(models.Model):
    _name = 'deferred.expense.data'
    _description = 'Deferred Expense Data'

    date = fields.Date(string='Date', required=True)
    amount = fields.Float(string='Amount', required=True)
    schedule_id = fields.Many2one('deferred.expense.schedule', string='Schedule', required=True, ondelete='cascade')
    status = fields.Boolean(string="Posted", store=True)
    debit_account = fields.Many2one('account.account', string='Debit Account', required=True)
    credit_account = fields.Many2one('account.account', string='Credit Account', required=True)
    debit_amount = fields.Float(string='Debit Amount', required=True)
    credit_amount = fields.Float(string='Credit Amount', required=True)
    reference = fields.Char(string='reference')
    journal_entry = fields.Char(string='journal entry')
