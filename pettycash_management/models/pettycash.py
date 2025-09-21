from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _


class pettyCashManagement(models.Model):
    _name = 'petty.cash.management'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'petty cash management'
    _order = 'id desc'

    def _get_default_account(self):
        cash_account = self.env['account.account'].search([('cash_account_selection', '=', True)], limit=1)
        return cash_account.id

    def _get_default_journal_id(self):
        cash_journal = self.env['account.journal'].search([('petty_cash_site_limit', '=', True)], limit=1)
        return cash_journal.id

    name = fields.Char(string='Sl No', required=True, default=lambda self: _('New'), copy=False, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company.id, readonly=True)

    account_id = fields.Many2one('account.account', string='Account', required=True, default=_get_default_account)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirm'),
         ('review', 'Review'),
         ('verified', 'Verified'),
         ('post', 'posted'),
         ('cancel', 'cancelled')
         ], default='draft', string='status', tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self:
    self.env.user.company_id.currency_id.id, required=True, readonly=True)
    total = fields.Float(string='Total', compute='compute_total', store=True, Tracking=True)
    date = fields.Date(string='Date', help='Select date here', default=fields.Date.context_today)
    project = fields.Many2one('project.project')
    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
                                 domain="[('company_id', '=', company_id)]", default=_get_default_journal_id)
    petty_cash_lines_ids = fields.One2many('petty.cash.management.lines', 'ref_id')
    remarks = fields.Text(string='Remarks')
    move_id = fields.Many2one('account.move', string='Entry', copy=False)

    @api.onchange('account_id')
    def onchange_payment_type(self):
        if self.account_id.journal_id:
            self.journal_id = self.account_id.journal_id.id

    @api.depends('petty_cash_lines_ids.amount')
    def compute_total(self):
        for ln in self:
            ln.total = 0
            for line in ln.petty_cash_lines_ids:
                if line.amount:
                    ln.total += line.amount

    @api.model
    def default_get(self, fields):
        res = super(pettyCashManagement, self).default_get(fields)
        x = self.env.company.id
        res.update({
            'company_id': x,
        })
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'petty.cash.management.Sequence') or _('New')
        res = super(pettyCashManagement, self).create(vals)
        return res

    def action_confirm(self):
        if not self.petty_cash_lines_ids:
            raise UserError(_("You need to add a line before Confirm."))

        self.state = 'confirm'

    def action_review(self):
        self.state = 'review'

    def action_verify(self):
        self.state = 'verified'

    def action_post(self):
        pt_cash = self.env['account.move'].search([('petty_cash_id', '=', self.id)])
        if any(move.state == 'post'for move in pt_cash):
            raise ValidationError('Already Posted')

        line_ids = []
        move_dict = {
            'move_type': 'entry',
            'narration': self.name,
            'petty_cash_id': self.id,
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'date': self.date,

        }

        total = sum(self.petty_cash_lines_ids.mapped('amount'))
        nar_list = [str(nar) for nar in self.petty_cash_lines_ids.mapped('narration') if nar]
        nar = ', '.join(nar_list)
        if not self.project:
            raise ValidationError("Invalid value for project")

        total_credit_line = (0, 0, {
            'name': nar,
            'account_id': self.account_id.id,
            'journal_id': self.journal_id.id,
            'product_id': self.petty_cash_lines_ids.mapped('product.id')[0] if self.petty_cash_lines_ids else False,
            'analytic_distribution': {self.project.analytic_account_id.id: 100.0},
            'date': self.date,
            'debit': 0.0,
            'credit': total,

        })
        line_ids.append(total_credit_line)

        for line in self.petty_cash_lines_ids:
            debit_line = (0, 0, {
                'name': line.narration,
                'account_id': line.account_id.id,
                'product_id': line.product.id,
                'date': self.date,
                'analytic_distribution': {line.project_id.id: 100.0} if line.project_id else {},
                'debit': line.amount,
                'credit': 0.0,
            })
            line_ids.append(debit_line)

        move_dict['line_ids'] = line_ids
        
        move = self.env['account.move'].create(move_dict)
        move.action_post()
        self.write({'move_id': move.id})
        self.state = 'post'

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        if self.move_id and self.move_id.petty_cash_id.state == 'post':
            self.move_id.button_cancel()
        self.state = 'draft'

    def unlink(self):
        raise ValidationError('Cannot Delete this record.')

    def action_journal_entries(self):
        self.ensure_one()
        return {
            'name': 'journal entries',
            'res_model': 'account.move',
            'view_mode': 'form',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.move_id.id,
            'target': 'current',

        }

    @api.constrains('total')
    def _check_amount_limit(self):
        for record in self:
            if record.journal_id.petty_cash_site_limit and record.total > record.journal_id.petty_cash_limit:
                raise ValidationError("Limit exceeded")


class PettyCashManagementLines(models.Model):
    _name = 'petty.cash.management.lines'

    account_id = fields.Many2one('account.account', string='Account',required=True)
    amount = fields.Float(string='Amount')
    narration = fields.Char(string='Narration',required=True)
    ref_id = fields.Many2one('petty.cash.management')
    project_id = fields.Many2one('account.analytic.account', related='ref_id.project.analytic_account_id',
                                 string='Analytic Account')

    product = fields.Many2one('product.product', string="product")

    @api.onchange('product')
    def _onchange_product_id(self):
        if self.product:
            self.account_id = self.product.property_account_expense_id

        else:
            self.account_id = False
