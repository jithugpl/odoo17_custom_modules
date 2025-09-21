from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_picking_ids = fields.Many2many(comodel_name='stock.picking',
                                            relation='invoice_purchase_order_delivery_ids',
                                            column1="acc_id",
                                            column2="pick_id", string="Purchase Picking Ids",
                                            compute='_compute_get_po_picking_ids')

    picking_ids = fields.Many2many(comodel_name='stock.picking',
                                   relation='invoice_order_delivery_ids',
                                   column1="acc_id",
                                   column2="pick_id", string="Receive Goods No")

    site_material_transfer_id = fields.Many2many('site.material.transfer', string='Site To Site Material Transfer')

    receive_goods_reference = fields.Char(string='Receive Goods Reference',
                                          compute='_compute_stock_supplier_reference_no', store=True)

    project_id = fields.Many2one('project.project', string='Project', tracking=True, copy=False)

    def _compute_get_po_picking_ids(self):
        for record in self:
            source_orders = record.line_ids.purchase_line_id.order_id
            purchase_orders = self.env['purchase.order'].sudo().search([('id', 'in', source_orders.ids)])
            done_picking_ids = purchase_orders.mapped('picking_ids').filtered(lambda p: p.state == 'done').ids
            record.purchase_picking_ids = [(6, 0, done_picking_ids)]

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if len(self.purchase_picking_ids):
            if not len(self.picking_ids):
                raise ValidationError("The Receive Goods Number is required to validate this document.")
            for i in self.picking_ids:
                i.inv_bill_generated = True
        return res

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        for i in self.picking_ids:
            i.inv_bill_generated = False
        return res

    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        for i in self.picking_ids:
            i.inv_bill_generated = False
        return res

    @api.depends('picking_ids')
    def _compute_stock_supplier_reference_no(self):
        for i in self:
            i.receive_goods_reference = ', '.join([s.supplier_reference or '' for s in i.picking_ids])


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    project_task_id = fields.Many2one('project.task', string='Task')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals['project_id'] = self.project_id.id
        return invoice_vals


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line()
        res['project_task_id'] = self.project_task_id.id
        return res


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        values = super()._prepare_default_reversal(move)
        values['project_id'] = move.project_id.id
        return values
