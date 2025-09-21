from odoo import models, fields, api


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    brand_link = fields.Char(string='Brand Store Link')
    is_active_brand = fields.Boolean(string="Is Active Brand")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_store_link = fields.Char(string="Brand Store Link", compute="_compute_brand_store_data", store=True)
    selected_brand_name = fields.Char(string="Selected Brand", compute="_compute_brand_store_data", store=True)

    @api.depends('attribute_line_ids.value_ids', 'attribute_line_ids.value_ids.is_active_brand',
                 'attribute_line_ids.value_ids.brand_link')
    def _compute_brand_store_data(self):
        """Compute the brand store link and brand name only if is_active_brand is checked."""
        for product in self:
            brand_link = ""
            brand_name = ""
            for line in product.attribute_line_ids:
                active_values = line.value_ids.filtered(lambda v: v.is_active_brand and v.brand_link)
                if active_values:
                    brand_link = active_values[0].brand_link  # Take the first active brand
                    brand_name = active_values[0].name  # Store the brand name

            product.brand_store_link = brand_link
            product.selected_brand_name = brand_name
