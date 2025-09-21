from odoo import models, fields


class MaterialRequestInherited(models.Model):
    _inherit = 'material.request'

# # Add your custom fields here
# custom_field = fields.Char(string='Custom Field')
#
# # Add your custom methods or overrides here
