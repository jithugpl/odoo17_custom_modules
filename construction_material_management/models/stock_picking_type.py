from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_purchase_requisition = fields.Boolean(string='Purchase Requisition')
    is_manufacture_order = fields.Boolean(string='Manufacturing Order')

    is_expense_account = fields.Boolean(string='Expense Account',
                                        help='Vendor Bill Expense Account for Project Direct Purchase to Site',
                                        tracking=True)
