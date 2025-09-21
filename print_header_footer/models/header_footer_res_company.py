from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    company_header = fields.Image(string="Company Header")
    company_footer = fields.Image(string="Company Footer")