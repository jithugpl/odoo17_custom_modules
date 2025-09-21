from odoo import models, fields, api, _


class CleaningForm(models.Model):
    _name = "cleaning.form"
    _description = "Cleaning Form"
    _inherit = 'mail.thread', 'mail.activity.mixin'
    _rec_name = "date"

    cleaning_no = fields.Char(string='Cleaning Number', required=True, readonly=True, default=lambda self: _('New'))
    number = fields.Char(string='Form', default="MM/PDN/FMT-03", readonly=True)
    date = fields.Date(string='Date', default=lambda self: fields.Date.today(), readonly=True)
    strength_of_solution = fields.Char(string='Strength Of Solution', required=True)
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)
    cleaned_by = fields.Many2one('hr.employee', string="Cleaned By", required=True)
    checked_by = fields.Many2one('res.users', string="Checked By", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.company)


    def action_approved(self):
        for record in self:
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if employee:
                record.checked_by = employee.id

    # below function to create sequence, xml code for sequence in data folder

    @api.model
    def create(self, vals):
        if vals.get('cleaning_no', _('New')) == _('New'):
            vals['cleaning_no'] = self.env['ir.sequence'].next_by_code('cleaning.code') or _('New')
        if not vals.get('user_id'):
            vals['user_id'] = self.env.user.id
        return super(CleaningForm, self).create(vals)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled'),
    ], default='draft', string="Status", required=True, tracking=True)

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.checked_by = False  # Clear the checked_by field


    # def action_approve(self):
    #     for rec in self:
    #         rec.state = 'approve'
    #     for record in self:
    #         employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #         if employee:
    #             record.checked_by = employee.id
    def action_approve(self):
        for rec in self:
            rec.state = 'approve'
            rec.checked_by = self.env.user

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

