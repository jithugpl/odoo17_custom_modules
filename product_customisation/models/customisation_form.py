from odoo import models, fields, api


class ProductCustomisation(models.TransientModel):
    _name = 'product.customisation'
    _description = 'Product Customisation'

    product_id = fields.Many2one('product.template', string='Product', required=True)
    customisation_details = fields.Text(string='Customisation Details', required=True)

    def action_submit(self):
        """Create a CRM opportunity with current user details."""
        user = self.env.user  # Get the current logged-in user

        # Prepare contact details
        contact_details = {
            'name': user.name,
            'email': user.partner_id.email,
            'phone': user.partner_id.phone,
            'street': user.partner_id.street,
            'city': user.partner_id.city,
            'zip': user.partner_id.zip,
            'country': user.partner_id.country_id.name if user.partner_id.country_id else '',
        }

        # Create CRM opportunity
        self.env['crm.lead'].create({
            'name': f"Customisation for {self.product_id.name}",
            'type': 'opportunity',
            'description': self.customisation_details,
            'contact_name': contact_details['name'],
            'email_from': contact_details['email'],
            'phone': contact_details['phone'],
            'street': contact_details['street'],
            'city': contact_details['city'],
            'zip': contact_details['zip'],
            'country_id': user.partner_id.country_id.id if user.partner_id.country_id else False,
        })

        return {'type': 'ir.actions.act_window_close'}

    # working code with out user details

# class ProductCustomisation(models.TransientModel):
#     _name = 'product.customisation'
#     _description = 'Product Customisation'
#
#     product_id = fields.Many2one('product.template', string='Product', required=True)
#     customisation_details = fields.Text(string='Customisation Details', required=True)
#
#     def action_submit(self):
#         """Create a CRM opportunity."""
#         self.env['crm.lead'].create({
#             'name': f"Customisation for {self.product_id.name}",
#             'type': 'opportunity',
#             'description': self.customisation_details,
#         })
#         return {'type': 'ir.actions.act_window_close'}
