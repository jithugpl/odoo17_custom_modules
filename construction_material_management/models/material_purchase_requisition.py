from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError


class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = 'Purchase Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,
                                 copy=False, readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('approve', 'Approved'), ('cancel', 'Cancelled'),
         ('bidding', 'Bidding'),
         ('close', 'Closed')], default='draft',
        string="Status", tracking=True)

    project_id = fields.Many2one('project.project', string='Project', required=True, tracking=True)
    created_on = fields.Date(string='Created On', default=lambda self: fields.Date.to_string(date.today()), copy=False,
                             tracking=True)
    picking_ids = fields.Many2many('stock.picking', string='Transfer', copy=False)
    vendor_ids = fields.Many2many('res.partner', string='Vendors', copy=False)

    requisition_line_ids = fields.One2many('material.purchase.requisition.line', 'requisition_id',
                                           string='Purchase Requisition Lines', copy=False)
    rfq_count = fields.Integer(string="Purchase Count", compute='_compute_rfq_count')
    stock_picking_id = fields.Many2one('stock.picking', string='Source Document', copy=False)

    #####New #####
    task_ids = fields.Many2many('project.task', string='Task', copy=False)
    cost_bom_ids = fields.Many2many('actual.bom', string='Cost BOM', copy=False)
    purchase_requisition_type = fields.Selection(related='company_id.purchase_requisition_type', store=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('material.purchase.requisition.code') or _('New')
        res = super(MaterialPurchaseRequisition, self).create(vals)
        return res

    @api.onchange('project_id')
    def _onchange_requisition_project_id(self):
        self.picking_ids = False
        self.vendor_ids = False
        self.task_ids = False
        self.cost_bom_ids = False
        self.requisition_line_ids = False

    @api.onchange('picking_ids')
    def _onchange_requisition_transfer_ids(self):
        self.requisition_line_ids = False

    @api.onchange('task_ids')
    def _onchange_requisition_task_ids(self):
        self.cost_bom_ids = False
        self.requisition_line_ids = False

    @api.onchange('cost_bom_ids')
    def _onchange_requisition_cost_bom_ids(self):
        self.requisition_line_ids = False

    def get_requisition_products(self):
        self.requisition_line_ids = False
        vals = []
        if self.purchase_requisition_type == 'transfer':
            for i in self.picking_ids:
                for j in i.move_ids_without_package:
                    qty = j.product_uom_qty - j.quantity if j.product_uom_qty != j.quantity else 0
                    if qty > 0:
                        vals.append((0, 0, {
                            'product_id': j.product_id.id,
                            'transfer_avl_quantity': qty,
                            'qty': qty,
                            'uom': j.product_id.uom_id.id,
                            'picking_id': i.id
                        }))
        elif self.purchase_requisition_type == 'cost_bom':
            for j in self.cost_bom_ids:
                for k in j.bom_line_ids:
                    if k.requisition_balance_quantity > 0:
                        vals.append((0, 0, {
                            'product_id': k.product_id.id,
                            # 'bom_avl_quantity': k.requisition_balance_quantity,
                            # 'qty': k.requisition_balance_quantity,
                            'uom': k.uom_id.id,
                            'task_id': j.task_id.id,
                            'cost_bom_line_id': k.id
                        }))
        self.write({'requisition_line_ids': vals})

    def apply_vendors(self):
        for i in self:
            for j in i.requisition_line_ids:
                if j.is_select:
                    j.vendor_ids = [(6, 0, i.vendor_ids.ids)]

    def action_select_all(self):
        for i in self.requisition_line_ids:
            if i.is_select == False:
                i.is_select = True

    def action_deselect_all(self):
        for i in self.requisition_line_ids:
            if i.is_select == True:
                i.is_select = False

    def button_confirm(self):
        line_len = len([i for i in self.requisition_line_ids if i.is_select])
        if not line_len:
            raise ValidationError('You need to select a line before Confirming')
        if self.purchase_requisition_type == 'transfer':
            transfer_line_qty = [i for i in self.requisition_line_ids if
                                 i.is_select and (i.qty <= 0 or i.qty > i.transfer_avl_quantity)]
            if len(transfer_line_qty):
                for j in transfer_line_qty:
                    raise ValidationError(
                        _("The selected quantity must be greater than 0 and less than or equal to the transfer quantity of %s for the product: %s") % (
                            j.transfer_avl_quantity, j.product_id.name))
        if self.purchase_requisition_type == 'cost_bom':
            bom_line_qty = [i for i in self.requisition_line_ids if
                            i.is_select and (i.bom_requested_qty <= 0 or i.bom_requested_qty > i.bom_avl_quantity)]
            if len(bom_line_qty):
                for j in bom_line_qty:
                    raise ValidationError(
                        _("The selected quantity must be greater than 0 and less than or equal to the BOM quantity of %s for the product: %s") % (
                            j.bom_avl_quantity, j.product_id.name))
        self.state = 'confirm'

    def button_approve(self):
        line_len = len([i for i in self.requisition_line_ids if i.is_select])
        if not line_len:
            raise ValidationError('You need to select a line before Approving')
        if self.purchase_requisition_type == 'transfer':
            transfer_line_qty = [i for i in self.requisition_line_ids if
                                 i.is_select and (i.qty <= 0 or i.qty > i.transfer_avl_quantity)]
            if len(transfer_line_qty):
                for j in transfer_line_qty:
                    raise ValidationError(
                        _("The selected quantity must be greater than 0 and less than or equal to the transfer quantity of %s for the product: %s") % (
                            j.transfer_avl_quantity, j.product_id.name))
        if self.purchase_requisition_type == 'cost_bom':
            bom_line_qty = [i for i in self.requisition_line_ids if
                            i.is_select and (i.bom_requested_qty <= 0 or i.bom_requested_qty > i.bom_avl_quantity)]
            if len(bom_line_qty):
                for j in bom_line_qty:
                    raise ValidationError(
                        _("The selected quantity must be greater than 0 and less than or equal to the BOM quantity of %s for the product: %s") % (
                            j.bom_avl_quantity, j.product_id.name))
            # additional_qty_sum = sum([i.additional_qty for i in self.requisition_line_ids if i.is_select])
            # if additional_qty_sum > 0:
            #     if (not self.project_id.purchase_amendment_user_id or
            #             self.env.user != self.project_id.purchase_amendment_user_id):
            #         raise ValidationError(_("There is some additional quantity, only an authorized person can approve"))
        self.state = 'approve'

    def button_create_rfq(self):
        line_len = len([i for i in self.requisition_line_ids if i.is_select])
        if not line_len:
            raise ValidationError('You need to select a line before create RFQ')
        #####Analytic Checking#####
        if self.project_id and self.project_id.analytic_account_id:
            analytic_value = {
                str(self.project_id.analytic_account_id.id): 100.0
                # Assuming 100% distribution to the analytic account
            }
        else:
            analytic_value = {}
        #####
        if self.purchase_requisition_type == 'transfer':
            transfer_line_qty = [i for i in self.requisition_line_ids if
                                 i.is_select and (i.qty <= 0 or i.qty > i.transfer_avl_quantity)]
            transfer_line_line_qty = len([i for i in self.requisition_line_ids if
                                          i.is_select and i.qty > 0 and i.qty <= i.transfer_avl_quantity])
            transfer_transfer_line_line_qty = len([i for i in self.requisition_line_ids if
                                                   i.is_select and i.qty > 0 and i.qty <= i.transfer_avl_quantity and len(
                                                       i.vendor_ids) > 0])
            if len(transfer_line_qty):
                for j in transfer_line_qty:
                    raise ValidationError(
                        _("The selected quantity must be greater than 0 and less than or equal to the transfer quantity of %s for the product: %s") % (
                            j.transfer_avl_quantity, j.product_id.name))
            if transfer_line_line_qty != transfer_transfer_line_line_qty:
                raise ValidationError('You must select a vendor for the selected lines.')
            #####PURCHASE ORDER#####
            purchase_order_obj = self.env['purchase.order']
            list1 = []
            x = []
            dict1 = {}
            dict2 = {}
            for j in self.requisition_line_ids:
                if j.is_select and j.qty > 0 and j.qty <= j.transfer_avl_quantity:
                    for ze in j.vendor_ids:
                        list1.append(ze.id)
                        x = list(set(list1))
            for l in x:
                y = []
                z = []
                for k in self.requisition_line_ids:
                    if k.is_select and k.qty > 0 and k.qty <= k.transfer_avl_quantity:
                        for po in k.vendor_ids:
                            if l == po.id:
                                y.append(po.id)
                                z.append(k)
                                dict1[l] = y
                                dict2[l] = z
            for i in dict1.keys():
                vals = {
                    'partner_id': i,
                    'material_purchase_requisition_id': self.id,
                    'project_id': self.project_id.id
                }
                x = purchase_order_obj.create(vals)
                for ol in dict2[i]:
                    x.write({'order_line': [(0, 0, {
                        'product_id': ol.product_id.id,
                        'name': ol.product_id.name,
                        'product_qty': ol.qty,
                        'product_uom': ol.uom.id,
                        'partner_id': i,
                        'analytic_distribution': analytic_value,
                        'requisition_line_id': ol.id
                    })]})
            self.state = 'bidding'
            #####
        if self.purchase_requisition_type == 'cost_bom':
            bom_line_qty = [i for i in self.requisition_line_ids if
                            i.is_select and (i.bom_requested_qty <= 0 or i.bom_requested_qty > i.bom_avl_quantity)]
            bom_line_line_qty = len([i for i in self.requisition_line_ids if
                                     i.is_select and i.bom_requested_qty > 0 and i.bom_requested_qty <= i.bom_avl_quantity])
            bom_bom_line_line_qty = len([i for i in self.requisition_line_ids if
                                         i.is_select and i.bom_requested_qty > 0 and i.bom_requested_qty <= i.bom_avl_quantity and len(
                                             i.vendor_ids) > 0])
            if len(bom_line_qty):
                for j in bom_line_qty:
                    raise ValidationError(
                        _("The selected quantity must be greater than 0 and less than or equal to the BOM quantity of %s for the product: %s") % (
                            j.bom_avl_quantity, j.product_id.name))
            if bom_line_line_qty != bom_bom_line_line_qty:
                raise ValidationError('You must select a vendor for the selected lines.')
            #####PURCHASE ORDER#####
            purchase_order_obj = self.env['purchase.order']
            list1 = []
            x = []
            dict1 = {}
            dict2 = {}
            for j in self.requisition_line_ids:
                if j.is_select and j.bom_requested_qty > 0 and j.bom_requested_qty <= j.bom_avl_quantity:
                    j.cost_bom_line_id.requisition_balance_quantity -= j.bom_requested_qty
                    j.cost_bom_line_id.pr_used_quantity += j.bom_requested_qty
                    for ze in j.vendor_ids:
                        list1.append(ze.id)
                        x = list(set(list1))
            for l in x:
                y = []
                z = []
                for k in self.requisition_line_ids:
                    if k.is_select and k.bom_requested_qty > 0 and k.bom_requested_qty <= k.bom_avl_quantity:
                        for po in k.vendor_ids:
                            if l == po.id:
                                y.append(po.id)
                                z.append(k)
                                dict1[l] = y
                                dict2[l] = z
            for i in dict1.keys():
                vals = {
                    'partner_id': i,
                    'material_purchase_requisition_id': self.id,
                    'project_id': self.project_id.id
                }
                x = purchase_order_obj.create(vals)
                for ol in dict2[i]:
                    x.write({'order_line': [(0, 0, {
                        'product_id': ol.product_id.id,
                        'name': ol.product_id.name,
                        'product_qty': ol.bom_requested_qty,
                        'product_uom': ol.uom.id,
                        'partner_id': i,
                        'project_task_id': ol.task_id.id,
                        'analytic_distribution': analytic_value,
                        'requisition_line_id': ol.id
                    })]})
            self.state = 'bidding'
            #####END#####

    def button_cancel(self):
        self.state = 'cancel'

    def button_close(self):
        self.state = 'close'

    def button_reset(self):
        self.state = 'draft'

    def action_show_po(self):
        return {
            'name': _('RFQ'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('material_purchase_requisition_id', '=', self.id)],
            'context': {'create': False, 'delete': False}
        }

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise ValidationError(
                    'You cannot delete a Purchase Requisition that is not in draft or cancelled state.')
        return super(MaterialPurchaseRequisition, self).unlink()

    def _compute_rfq_count(self):
        for rec in self:
            rfq_history = self.env['purchase.order'].sudo().search_count(
                [('material_purchase_requisition_id', '=', rec.id)])
            rec.rfq_count = rfq_history


class MaterialPurchaseRequisitionLine(models.Model):
    _name = 'material.purchase.requisition.line'
    _description = 'Purchase Requisition Lines'
    _rec_name = 'requisition_id'

    requisition_id = fields.Many2one('material.purchase.requisition', string='Requisition')

    is_select = fields.Boolean(string="Select", default=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    uom = fields.Many2one('uom.uom', string='UOM', required=True)
    vendor_ids = fields.Many2many('res.partner', string='Vendors')
    picking_id = fields.Many2one('stock.picking', string='Transfer')

    #####New#####
    task_id = fields.Many2one('project.task', string='Task')
    cost_bom_line_id = fields.Many2one('bom.line', string='Cost BOM')

    bom_avl_quantity = fields.Float(string="BOM Qty", related='cost_bom_line_id.requisition_balance_quantity')
    transfer_avl_quantity = fields.Float(string="Transfer Qty")

    bom_requested_qty = fields.Float(string="Total Requirement")
    # bom_requested_qty = fields.Float(string="BOM Requested Qty")
    # additional_qty = fields.Float(string="Additional Qty")

    qty = fields.Float(string="Qty")
    # qty_bom = fields.Float(string='Total Requirement', compute='_compute_total_requirement_qty', store=True)

    po_qty = fields.Float(string='PO Qty', compute='_compute_total_purchase_qty')

    # @api.depends('bom_requested_qty', 'additional_qty')
    # def _compute_total_requirement_qty(self):
    #     for i in self:
    #         i.qty_bom = i.bom_requested_qty + i.additional_qty

    def _compute_total_purchase_qty(self):
        for rec in self:
            po_line = self.env['purchase.order.line'].sudo().search(
                [('requisition_line_id', '=', rec.id), ('state', '=', 'purchase')])
            po_line_qty_sum = sum([i.product_qty for i in po_line])
            rec.po_qty = po_line_qty_sum
