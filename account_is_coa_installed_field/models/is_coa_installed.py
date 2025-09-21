# custom_partner_extension/models/res_partner.py
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_coa_installed = fields.Boolean(string="Is COA Installed", default=False)
