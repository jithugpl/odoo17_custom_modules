
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    size_chart_id = fields.Many2one(
        'website.product.size.chart', string='Size Chart')

    def _get_size_chart(self):
        self.ensure_one()
        size_chart = None
        if self.size_chart_id and self.size_chart_id.is_active:
            size_chart = self.size_chart_id
        else:
            # Check category hierarchy
            category = self.categ_id
            found_active_chart = False
            while category and not found_active_chart:
                if category.size_chart_id and category.size_chart_id.is_active:
                    size_chart = category.size_chart_id
                    found_active_chart = True
                else:
                    category = category.parent_id

            # Check product tags if no chart found in categories
            if not found_active_chart:
                for tag in self.product_tag_ids:
                    if tag.size_chart_id and tag.size_chart_id.is_active:
                        size_chart = tag.size_chart_id
                        break

                        # Check public categories if no chart found in product tags
            if not found_active_chart:
                for public_category in self.public_categ_ids:
                    if public_category.size_chart_id and public_category.size_chart_id.is_active:
                        size_chart = public_category.size_chart_id
                        break

        return size_chart



