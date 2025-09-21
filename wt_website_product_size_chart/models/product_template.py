# -*- coding: utf-8 -*-
# Copyright (C) Wisenetic Technologies.
from odoo import models, fields, api


# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     size_chart_id = fields.Many2one(
#         'website.product.size.chart', string='Size Chart')
#
#     def _get_size_chart(self):
#         self.ensure_one()
#         size_chart = None
#         if self.size_chart_id and self.size_chart_id.is_active:
#             size_chart = self.size_chart_id
#         else:
#             category = self.categ_id
#             found_active_chart = False  # Flag to indicate if an active size chart is found
#             while category and not found_active_chart:
#                 if category.size_chart_id and category.size_chart_id.is_active:
#                     size_chart = category.size_chart_id
#                     found_active_chart = True  # Set the flag to True
#                 else:
#                     category = category.parent_id
#
#         return size_chart

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

        return size_chart



