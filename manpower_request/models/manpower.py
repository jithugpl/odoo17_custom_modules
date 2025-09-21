from odoo import models, fields, api, _

class ManpowerRequest(models.Model):
    _name = "manpower.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Manpower_Request"
    _rec_name = "reference_no"


    Request_Date = fields.Datetime(string="Request Date")
    reference_no = fields.Char(string='Reference', required=True,
                               readonly=True, default=lambda self: _('New'))
    Department = fields.Many2one('hr.department', string="Department")
    Job_Position = fields.Many2one('hr.job', string="Job Position")
    Number_of_employee = fields.Integer(string="No of Employee")
    # Education = fields.Many2many(string="Education")
    Experience = fields.Text(string="Experience")
    education_ids = fields.Many2many('hr.recruitment.degree', string='Education')
    # education_id = fields.Selection([
    #     ('bcom', 'BCOM'),
    #     ('btech', 'BTech'),
    #     ('bca', 'BCA'),
    #     ('mtech', 'MTech'),
    #     ('mcom', 'MCOM'),
    #     ('mba', 'MBA'),
    #     ('plus two', 'PLUS TWO')
    #
    # ], string='Education')
    employment_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary')
    ], string='Employment Type',widget='radio')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
    ], default='draft', string="Status", required=True, tracking=True)
    skills_ids = fields.One2many('manpower.skills', 'new_id', string='Skill Lines')

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_review(self):
        for rec in self:
            rec.state = 'review'
    def action_confirm(self):
        for rec in self:
            rec.state = 'approved'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    # @api.model
    # def create(self, vals):
    #     vals['ref']=self.env['ir.sequence'].next_by_code('manpower.request')
    #     return super(ManpowerRequest,self).create(vals)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'manpower.request') or _('New')
        res = super(ManpowerRequest, self).create(vals)
        return res


# one to man field in notebook


class ManpowerSkills(models.Model):
    _name = "manpower.skills"
    _description = "Manpower_Skills"

    # skills = fields.Many2one('hr.skill.type', required=True)
    skill_id = fields.Many2one('hr.skill',
                               domain="[('skill_type_id','=', skill_type_id)]", required=True, tracking=True
                               )
    skill_level_id = fields.Many2one('hr.skill.level',
                                     domain="[('skill_type_id', '=', skill_type_id)]",
                                     required=True)
    skill_type_id = fields.Many2one('hr.skill.type',

                                    required=True)
    new_id = fields.Many2one('manpower.request', string='Manpower Request')

