from odoo import models, fields, api

class OfficeAssetRequest(models.Model):
    _name = 'office.asset.request'
    _description = 'Office Asset Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Request Reference", required=True, copy=False, readonly=True,
                       default=lambda self: ('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,
                                  default=lambda self: self.env.user.employee_id)
    request_date = fields.Date(string="Request Date", default=fields.Date.today,tracking=True)
    asset_name = fields.Char(string="Asset Name", required=True,tracking=True)
    quantity = fields.Integer(string="Quantity", default=1 ,tracking=True)
    reason = fields.Text(string="Reason")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string="Status", default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('office.asset.request') or 'New'
        return super().create(vals)

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
