# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Selection(
        [('work_order', 'Work Order'), ('extra_work_order', 'Extra Work Order')],
        string='Order Type', default='work_order')
