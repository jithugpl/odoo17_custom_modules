from odoo import models, fields, api, _


class NewTrial(models.Model):
    _name = "trial.form"
    _description = "Trial Form"


    trial_no = fields.Char(string='Trial Number', required=True, readonly=True, default=lambda self: _('New'))
    trial_date = fields.Date(string='Trial Date')
    project_name = fields.Many2one(comodel_name='project.project', string='Project Name')
    customer_name = fields.Many2one(comodel_name='res.partner', string='Customer Name')
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)#to show created person
    employee_name = fields.Many2one('hr.employee', string="Employee")
    checked_by = fields.Many2one('hr.employee', string="Checked By", readonly=True)

    def action_dispatched(self):
        for record in self:
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if employee:
                record.checked_by = employee.id

    #below function to create sequence, xml code for sequence in data folder
    @api.model
    def create(self, vals):
        if vals.get('trial_no', _('New')) == _('New'):
            vals['trial_no'] = self.env['ir.sequence'].next_by_code('trial.slip') or _('New')
        if not vals.get('user_id'):
            vals['user_id'] = self.env.user.id
        return super(NewTrial, self).create(vals)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('dispatch', 'Dispatched'),
        ('cancel', 'Cancelled'),
    ], default='draft', string="Status", required=True, tracking=True)

    #below are actions for buttons

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'


    def action_review(self):
        for rec in self:
            rec.state = 'review'

    def action_dispatch(self):
        for rec in self:
            rec.state = 'dispatch'
        for record in self:
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if employee:
                record.checked_by = employee.id

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


#function to auto select customer on selecting project
    @api.onchange('project_name')
    def _onchange_project_name(self):
        if self.project_name:
            self.customer_name = self.project_name.partner_id
        else:
            self.customer_name = False
