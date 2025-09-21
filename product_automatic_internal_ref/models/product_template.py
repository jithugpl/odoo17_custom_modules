from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # New field for Style Code
    style_code = fields.Char(string='Style Code')

    automatic_ref_activated = fields.Boolean(
        string='Automatic Reference Activated',
        compute='_compute_automatic_ref_activated'
    )

    def _compute_automatic_ref_activated(self):
        """
        This field is used in views to determine if the automatic internal reference is activated.
        It can be used to render the default_code field as read-only in the view.
        """
        for product in self:
            product.automatic_ref_activated = self.env['ir.config_parameter'].sudo().get_param(
                'activate.automatic.product.ref', False
            )

    @api.constrains('default_code')
    def unique_default_code(self):
        """
        Enforce that each product template has a unique internal reference.
        If two or more products have the same default_code, a UserError is raised.
        """
        for product in self.filtered(lambda p: p.default_code):
            product_with_same_code = self.env['product.template'].search([
                ('default_code', '=', product.default_code),
                ('id', '!=', product.id)
            ])
            if product_with_same_code:
                raise UserError(_(
                    'These product templates: %s, %s have the same default code'
                ) % (product.display_name, product_with_same_code.display_name))

    @api.model_create_multi
    def create(self, val_list):
        """
        Override the create method:

        - If the automatic internal reference feature is activated (via the configuration parameter)
          and no manual override is provided via context, then:
            - The user is not allowed to manually set the internal reference.
            - Instead, the module automatically generates a default_code from a sequence defined on the product category.
            - The generated code is also assigned to both barcode and style_code.
        """
        automatic_ref_activated = self.env['ir.config_parameter'].sudo().get_param(
            'activate.automatic.product.ref', False
        )
        if automatic_ref_activated and not self.env.context.get('product_ref', False):
            for values in val_list:
                if 'default_code' in values and values.get('default_code', False):
                    raise UserError(_("Sorry, you cannot set an Internal Reference. Odoo sets it by itself!"))
                defaults = self.default_get(['categ_id'])
                categ_id = values.get('categ_id') or defaults.get('categ_id')
                category = self.env['product.category'].browse(categ_id)
                sequence = category.get_sequence_for_internal_ref()
                generated_code = sequence.next_by_id()
                values['default_code'] = generated_code
                # Update both barcode and style_code with the generated code
                values['barcode'] = generated_code
                values['style_code'] = generated_code
        return super(ProductTemplate, self.with_context(product_ref=True)).create(val_list)

    def write(self, vals):
        """
        Override the write method:

        - Prevent modification of the internal reference (default_code) if the automatic feature is active.
        - If default_code is updated via other means (with allowed context),
          then update barcode and style_code accordingly.
        """
        automatic_ref_activated = self.env['ir.config_parameter'].sudo().get_param(
            'activate.automatic.product.ref', False
        )
        if (not self.env.context.get('product_ref', False) and
                not self.env.context.get('force_default_code', False) and
                automatic_ref_activated and 'default_code' in vals):
            raise UserError(_("Sorry, you cannot modify the Internal Reference of a Product."))
        # If default_code is updated, ensure that barcode and style_code get the new value
        if 'default_code' in vals:
            vals['barcode'] = vals['default_code']
            vals['style_code'] = vals['default_code']
        return super(ProductTemplate, self).write(vals)

    @api.onchange('default_code')
    def _onchange_default_code(self):
        """
        When the internal reference (default_code) changes (e.g., in the UI),
        update both the barcode and style_code fields with the new value.
        """
        if self.default_code:
            self.barcode = self.default_code
            self.style_code = self.default_code
