# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cat_consign_delivery_print(models.Model):
#     _name = 'cat_consign_delivery_print.cat_consign_delivery_print'
#     _description = 'cat_consign_delivery_print.cat_consign_delivery_print'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

