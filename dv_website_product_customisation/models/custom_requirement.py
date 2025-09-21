
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductCustomizationRequest(models.Model):
    _name = 'product.customization.request'
    _description = 'Product Customization Request'

    product_id = fields.Many2one('product.product', string='Product', readonly=True, required=True)
    customization_details = fields.Text(string='Customization Details', required=True)
    contact_number = fields.Char(string='Contact Number', required=True)




    # def action_submit(self):
    #     """Create a CRM opportunity."""
    #
    #     self.env['crm.lead'].create({
    #         'name': f"Customisation for {self.product_id.name}",
    #         'type': 'opportunity',
    #         'description': self.customisation_details,
    #     })
    #     return {'type': 'ir.actions.act_window_close'}
