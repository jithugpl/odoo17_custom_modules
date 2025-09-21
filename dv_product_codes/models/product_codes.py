from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    style_code = fields.Char(string='Style Code')

    @api.onchange('default_code')
    def _onchange_default_code(self):
        """
        When the internal reference changes, update both the barcode and style code with the same value.
        """
        if self.default_code:
            self.barcode = self.default_code
            self.style_code = self.default_code
