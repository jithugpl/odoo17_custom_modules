# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ActualBom(models.Model):
    _name = 'actual.bom'
    _description = 'Cost BOM'
    _inherit = ['portal.mixin', 'mail.thread.main.attachment', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'id desc'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company, copy=False)
    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), tracking=True)
    date = fields.Date(string='Date', default=fields.Date.today(), copy=False)

    project_id = fields.Many2one('project.project', string='Project', tracking=True)
    partner_id = fields.Many2one(related='project_id.partner_id', store=True, tracking=True)
    task_id = fields.Many2one('project.task', string='Task', tracking=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('in_review', 'In Review'), ('verified', 'Verified'), ('approved', 'Approved'),
         ('revised', 'Revised'), ('cancelled', 'Cancelled')],
        string='State',
        default='draft', readonly=True, tracking=True)

    actual_material_total = fields.Float(string="Material Total Amount", compute='_compute_actual_bom_total_values',
                                         store=True)
    actual_labour_total = fields.Float(string="Labour Total Amount", compute='_compute_actual_bom_total_values',
                                       store=True)
    actual_overhead_total = fields.Float(string="Overhead Total Amount", compute='_compute_actual_bom_total_values',
                                         store=True)
    actual_other_total = fields.Float(string="Subcontract Total Amount", compute='_compute_actual_bom_total_values',
                                      store=True)
    actual_total_amount = fields.Float(string="Total Amount", compute='_compute_actual_bom_total_values', store=True)

    work_order_product_id = fields.Many2one('product.product', string='Product',
                                            compute='_compute_get_work_order_values')
    work_order_qty = fields.Float(string='Quantity', compute='_compute_get_work_order_values')
    work_order_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', compute='_compute_get_work_order_values')
    work_order_price = fields.Float(string='Unit Price', compute='_compute_work_order_price')

    bom_line_ids = fields.One2many('bom.line', 'line_id', string="Material Lines")
    labour_line_ids = fields.One2many('actual.bom.labour.line', 'labour_line_id', string="Labour Lines")
    overhead_line_ids = fields.One2many('actual.bom.over.head.line', 'overhead_line_id', string="Overhead Lines")
    subcontract_line_ids = fields.One2many('actual.bom.subcontract.line', 'subcontract_line_id',
                                           string="Subcontract Lines")

    reviewed_user_id = fields.Many2one('res.users', string='Reviewed User', tracking=True, copy=False)
    review_date = fields.Date(string='Reviewed Date', tracking=True, copy=False)

    verified_user_id = fields.Many2one('res.users', string='Verified User', tracking=True, copy=False)
    verify_date = fields.Date(string='Verified Date', tracking=True, copy=False)

    approved_user_id = fields.Many2one('res.users', string='Approved User', tracking=True, copy=False)
    approve_date = fields.Date(string='Approved Date', tracking=True, copy=False)

    revision_reason = fields.Char(string='Reason', copy=False)
    bom_reference = fields.Char(string='Reference', copy=False)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('actual.bom.seq') or _('New')
        res = super(ActualBom, self).create(vals)
        return res

    def action_in_review(self):
        if not self.bom_line_ids:
            raise ValidationError('There are no material lines!')
        line_len = len([i for i in self.bom_line_ids if i.is_select])
        if not line_len:
            raise ValidationError('You need to select a material before Confirming')
        #####Qty Checking for Used Qty#####
        for j in (line for line in self.bom_line_ids if line.is_select):
            max_value = max(j.mr_used_quantity, j.pr_used_quantity)
            if j.quantity < max_value:
                raise ValidationError(
                    _("The selected quantity must be greater than or equal to the used quantity of %s for the product: %s") % (
                        max_value, j.product_id.name))
        #####
        self.reviewed_user_id = self.env.user.id
        self.review_date = fields.Date.today()
        self.state = 'in_review'

    def action_verify(self):
        self.verified_user_id = self.env.user.id
        self.verify_date = fields.Date.today()
        self.state = 'verified'

    def action_approve(self):
        self.approved_user_id = self.env.user.id
        self.approve_date = fields.Date.today()
        self.state = 'approved'

    def action_reset(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancelled'

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.task_id = False
        self.bom_line_ids = False

    def action_select(self):
        for i in self.bom_line_ids:
            if i.is_select == True:
                i.is_select = False

    def action_select_all(self):
        for i in self.bom_line_ids:
            if i.is_select == False:
                i.is_select = True

    @api.depends('bom_line_ids.total', 'labour_line_ids.total', 'overhead_line_ids.total', 'subcontract_line_ids.total')
    def _compute_actual_bom_total_values(self):
        for i in self:
            material_total = sum([j.total for j in i.bom_line_ids if j.is_select])
            labour_total = sum([j.total for j in i.labour_line_ids])
            overhead_total = sum([j.total for j in i.overhead_line_ids])
            other_total = sum([j.total for j in i.subcontract_line_ids])

            i.actual_material_total = material_total
            i.actual_labour_total = labour_total
            i.actual_overhead_total = overhead_total
            i.actual_other_total = other_total
            i.actual_total_amount = material_total + labour_total + overhead_total + other_total

    def _compute_get_work_order_values(self):
        for i in self:
            sale_line = self.env['sale.order.line'].sudo().search([('id', '=', i.task_id.sale_line_id.id)], limit=1)
            if sale_line:
                i.work_order_product_id = sale_line.product_id.id
                i.work_order_qty = sale_line.product_uom_qty
                i.work_order_uom_id = sale_line.product_uom.id
            else:
                i.work_order_product_id = False
                i.work_order_qty = False
                i.work_order_uom_id = False

    def unlink(self):
        for rec in self:
            raise ValidationError(
                'You cannot delete a Cost BOM.')
        return super(ActualBom, self).unlink()

    @api.depends('actual_total_amount', 'work_order_qty')
    def _compute_work_order_price(self):
        for i in self:
            i.work_order_price = i.actual_total_amount / i.work_order_qty if i.work_order_qty > 0 else 0

    def action_revision(self):
        if not self.revision_reason:
            raise ValidationError('Reason must be provided before proceeding with the revision.')
        bom_vals, labour_vals, overhead_vals, contract_vals = self._prepare_revised_form()
        ctx = self.copy()
        ctx.update({
            'bom_reference': self.name,
            'bom_line_ids': bom_vals,
            'labour_line_ids': labour_vals,
            'overhead_line_ids': overhead_vals,
            'subcontract_line_ids': contract_vals
        })
        self.state = 'revised'

    def _prepare_revised_form(self):
        bom_vals = [
            (0, 0, {
                'product_id': i.product_id.id,
                'quantity': i.quantity,
                'previous_quantity': i.quantity,
                'balance_quantity': i.balance_quantity,
                'mr_used_quantity': i.mr_used_quantity,
                'requisition_balance_quantity': i.requisition_balance_quantity,
                'pr_used_quantity': i.pr_used_quantity,
                'cost': i.cost
            })
            for i in self.bom_line_ids if i.is_select
        ]
        labour_vals = [
            (0, 0, {
                'product_id': j.product_id.id,
                'quantity': j.quantity,
                'cost': j.cost
            })
            for j in self.labour_line_ids
        ]
        overhead_vals = [
            (0, 0, {
                'product_id': k.product_id.id,
                'quantity': k.quantity,
                'cost': k.cost
            })
            for k in self.overhead_line_ids
        ]
        contract_vals = [
            (0, 0, {
                'product_id': sub.product_id.id,
                'quantity': sub.quantity,
                'cost': sub.cost
            })
            for sub in self.subcontract_line_ids
        ]
        return bom_vals, labour_vals, overhead_vals, contract_vals


class BoMLines(models.Model):
    _name = 'bom.line'
    _rec_name = 'line_id'

    line_id = fields.Many2one('actual.bom', string="Line")

    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Qty')
    balance_quantity = fields.Float(string='MR Balance Qty')
    requisition_balance_quantity = fields.Float(string='PR Balance Qty')
    uom_id = fields.Many2one(related='product_id.uom_id', store=True)
    cost = fields.Float(string='Rate')
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    is_select = fields.Boolean(string="Select", default=True)

    previous_quantity = fields.Float(string='Previous Qty')
    mr_used_quantity = fields.Float(string='MR Used Qty')
    pr_used_quantity = fields.Float(string='PR Used Qty')

    @api.depends('cost', 'quantity')
    def _compute_total(self):
        for i in self:
            i.total = i.quantity * i.cost

    @api.onchange('quantity')
    def _def_onchange_quantity(self):
        self.balance_quantity = self.quantity - self.mr_used_quantity
        self.requisition_balance_quantity = self.quantity - self.pr_used_quantity


class ActualBomLabourLines(models.Model):
    _name = 'actual.bom.labour.line'
    _rec_name = 'labour_line_id'

    labour_line_id = fields.Many2one('actual.bom', string="Labour Line")

    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Qty')
    uom_id = fields.Many2one(related='product_id.uom_id', store=True)
    cost = fields.Float(string='Rate')
    total = fields.Float(string='Total', compute='_labour_compute_total', store=True)

    @api.depends('cost', 'quantity')
    def _labour_compute_total(self):
        for i in self:
            i.total = i.quantity * i.cost


class ActualBomOverHeadLines(models.Model):
    _name = 'actual.bom.over.head.line'
    _rec_name = 'overhead_line_id'

    overhead_line_id = fields.Many2one('actual.bom', string="Overhead Line")

    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Qty')
    uom_id = fields.Many2one(related='product_id.uom_id', store=True)
    cost = fields.Float(string='Rate')
    total = fields.Float(string='Total', compute='_overhead_compute_total', store=True)

    @api.depends('cost', 'quantity')
    def _overhead_compute_total(self):
        for i in self:
            i.total = i.quantity * i.cost


class ActualBomSubcontractLines(models.Model):
    _name = 'actual.bom.subcontract.line'
    _rec_name = 'subcontract_line_id'

    subcontract_line_id = fields.Many2one('actual.bom', string="Subcontract Line")

    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Qty')
    uom_id = fields.Many2one(related='product_id.uom_id', store=True)
    cost = fields.Float(string='Rate')
    total = fields.Float(string='Total', compute='_subcontract_compute_total', store=True)

    @api.depends('cost', 'quantity')
    def _subcontract_compute_total(self):
        for i in self:
            i.total = i.quantity * i.cost
