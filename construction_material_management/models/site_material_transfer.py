from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError


class SiteMaterialTransfer(models.Model):
    _name = 'site.material.transfer'
    _description = 'Site To Site Material Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), tracking=True)
    date = fields.Date(string="Date", copy=False, default=fields.Date.context_today)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,
                                 copy=False, readonly=True)
    from_project_id = fields.Many2one('project.project', string='From Project')
    to_project_id = fields.Many2one('project.project', string='To Project')
    site_material_line_ids = fields.One2many('site.material.transfer.line', 'site_material_transfer_id')
    state = fields.Selection(
        [('draft', 'Draft'), ('review', 'Reviewed'), ('issued', 'Issued'), ('receive', 'Received')], default='draft',
        required=True,
        readonly=True, index=True, string='State', tracking=True, store=True)
    move_id = fields.Many2one('account.move', string='Entry')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, store=True)

    def action_review(self):
        self.state = 'review'
        if self.name == 'New':
            self.name = self.env['ir.sequence'].next_by_code('site.material.transfer.seq') or _('New')

    def action_approve(self):
        self.state = 'issued'
        journal_id = self.env.company.site_material_transfer_journal_id
        credit_id = self.env.company.site_material_transfer_credit_account_id
        debit_id = self.env.company.site_material_transfer_debit_account_id
        total = sum(self.site_material_line_ids.mapped('amount_total'))
        if not journal_id or not credit_id or not debit_id:
            raise ValidationError(
                _('You need to add Journal, Credit Account and Debit Account in Company Form'))

        move = self.env['account.move'].create({
            'move_type': 'entry',
            # 'partner_id': self.from_project_id.partner_id.id,
            'journal_id': journal_id.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': debit_id.id,
                    'currency_id': self.currency_id.id,
                    'debit': total,
                    'partner_id': self.to_project_id.partner_id.id,
                    'credit': 0.0,
                    'analytic_distribution': {
                        str(self.to_project_id.analytic_account_id.id): 100} if self.to_project_id.analytic_account_id.id else None
                }),
                (0, 0, {
                    'account_id': credit_id.id,
                    'partner_id': self.from_project_id.partner_id.id,
                    'currency_id': self.currency_id.id,
                    'debit': 0.0,
                    'credit': total,
                    'analytic_distribution': {
                        str(self.from_project_id.analytic_account_id.id): 100} if self.from_project_id.analytic_account_id.id else None

                }),
            ],
        })
        move.action_post()
        self.move_id = move.id

    def action_receive(self):
        self.state = 'receive'

    def action_draft(self):
        self.state = 'draft'


class SiteMaterialTransferLine(models.Model):
    _name = 'site.material.transfer.line'
    _description = 'Site Material Transfer Line'

    site_material_transfer_id = fields.Many2one('site.material.transfer', string='Site Material Transfer')
    product_id = fields.Many2one('product.product', string='Products', required=True)
    quantity = fields.Float(string='Quantity', default=1)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,
                                 copy=False, readonly=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, store=True)
    amount_total = fields.Monetary(
        string='Amount',
        compute='_compute_amount', store=True, readonly=True,
        currency_field='currency_id',
    )
    price_unit = fields.Float(
        string="Rate",
        compute='_compute_price_unit', precompute=True, store=True, required=True, readonly=True,
        copy=True,
        digits='Product Price',
    )

    @api.depends('product_id')
    def _compute_price_unit(self):
        for line in self:
            line.price_unit = line.product_id.list_price

    @api.depends('product_id', 'quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            if line.product_id and line.quantity and line.price_unit:
                line.amount_total = line.price_unit * line.quantity
            else:
                line.amount_total = 0
