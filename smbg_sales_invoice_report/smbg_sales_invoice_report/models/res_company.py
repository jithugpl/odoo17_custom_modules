from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    inv_terms_and_conditions = fields.Text(string='Terms and Conditions')
