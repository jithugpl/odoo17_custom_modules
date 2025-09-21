from odoo import models, fields, api


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    is_active_attribute = fields.Boolean(string="Is Active Attribute")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_html = fields.Html(string="Description")
    material_id = fields.Many2one('product.material', string="Material")
    colour_id = fields.Many2one('product.colour', string="Colour")
    size_id = fields.Many2one('product.size', string="Size")
    care_guide_id = fields.Many2one('care.guide', string="Care guide")
    items_included_id = fields.Many2one('items.included', string="Items Included")

    product_note_id = fields.Html(string="Product Note")

    active_attribute_values = fields.Text(
        string="Active Attribute Values",
        compute="_compute_active_attribute_values",
        store=True  # Store=True ensures computed values are saved and available
    )

    @api.depends("attribute_line_ids.value_ids.is_active_attribute")
    def _compute_active_attribute_values(self):
        """Compute and store only active attribute values for the product."""
        for product in self:
            attributes = []
            for line in product.attribute_line_ids:
                active_values = line.value_ids.filtered(lambda v: v.is_active_attribute)
                if active_values:
                    value_names = ", ".join(active_values.mapped("name"))
                    attributes.append(f"{line.attribute_id.name}: {value_names}")

            product.active_attribute_values = " | ".join(attributes) if attributes else ""






