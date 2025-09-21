from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking')
    material_purchase_requisition_id = fields.Many2one('material.purchase.requisition', string='Purchase Requisition')
    # purchase_picking_ids = fields.Many2many(comodel_name='stock.picking',
    #                                         relation='custom_purchase_order_delivery_ids',
    #                                         column1="pur_id",
    #                                         column2="pick_id", string="Picking Ids")

    # def _prepare_invoice(self):
    #     invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
    #     invoice_vals['picking_ids'] = self.purchase_picking_ids
    #     return invoice_vals
    project_id = fields.Many2one('project.project', string='Project', tracking=True, copy=False)

    @api.onchange('project_id')
    def _onchange_po_project_id(self):
        for i in self.order_line:
            i.project_task_id = False
            if self.project_id.analytic_account_id and not i.analytic_distribution:
                i.analytic_distribution = {str(self.project_id.analytic_account_id.id): 100}

    def _prepare_picking(self):
        res = super()._prepare_picking()
        res['project_id'] = self.project_id.id
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_unit_inclusive = fields.Float(string='Unit Price incl.', compute='_compute_line_price_unit_inclusive',
                                        store=True)
    project_task_id = fields.Many2one('project.task', string='Task')

    requisition_line_id = fields.Many2one('material.purchase.requisition.line', string='Requisition Line')

    @api.depends('price_total', 'product_qty')
    def _compute_line_price_unit_inclusive(self):
        for i in self:
            i.price_unit_inclusive = i.price_total / i.product_qty if i.product_qty > 0 else 0

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line()
        line = self.env['purchase.order.line'].sudo().browse(res['purchase_line_id'])
        order = line.order_id
        if order.picking_type_id.is_expense_account:
            account_id = line.product_id.categ_id.property_account_expense_categ_id.id if line.product_id.categ_id.property_account_expense_categ_id else 0
            res.update({
                'account_id': account_id
            })
        return res

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        res['analytic_account_id'] = self.order_id.project_id.analytic_account_id.id
        return res
