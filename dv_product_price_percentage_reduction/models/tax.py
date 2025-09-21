import re
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tax_string_value = fields.Float(
        string="Tax String Value",
        compute="_compute_tax_string_value",
        store=True
    )

    @api.depends('tax_string')
    def _compute_tax_string_value(self):
        for product in self:
            # Clean and extract only the first valid number from the string
            match = re.search(r'([\d,]+\.?\d*)', product.tax_string or "")
            if match:
                # Remove commas and convert to float
                number_str = match.group(1).replace(',', '')
                product.tax_string_value = float(number_str)
            else:
                product.tax_string_value = 0.0



