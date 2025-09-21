# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError


class MaterialRequest(models.Model):
    _name = 'material.request'
    _description = 'Material Request'
    _inherit = ['portal.mixin', 'mail.thread.main.attachment', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), tracking=True)

    project_id = fields.Many2one('project.project', string='Project', tracking=True, copy=False)
    task_id = fields.Many2one('project.task', string='Task', tracking=True, copy=False)
    cost_bom_ids = fields.Many2many('actual.bom', string='Cost BOM')

    partner_id = fields.Many2one(related='project_id.partner_id', store=True)
    date = fields.Date(string='Date', default=fields.Date.today(), copy=False)
    expected_date = fields.Date(string='Expected Date', copy=False, tracking=True)

    material_request_line_ids = fields.One2many('material.request.line', 'line_id', string="Material Lines", copy=False)
    transfer_count = fields.Integer(string='Transfer count', compute="_compute_transfer_count")

    state = fields.Selection(
        [('draft', 'Draft'), ('in_review', 'In Review'), ('approved', 'Approved'), ('cancelled', 'Cancelled')],
        string='State', default='draft', readonly=True)

    note = fields.Html(string='Note')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('material.request.seq') or _('New')
        res = super(MaterialRequest, self).create(vals)
        return res

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.task_id = False
        self.cost_bom_ids = False

    @api.onchange('task_id')
    def onchange_task_id(self):
        self.cost_bom_ids = False

    @api.onchange('cost_bom_ids')
    def _onchange_get_cost_bom_products(self):
        self.material_request_line_ids = False
        if len(self.cost_bom_ids):
            cost_list = []
            for line in self.cost_bom_ids:
                for i in line.bom_line_ids:
                    if i.balance_quantity > 0:
                        cost_list.append((0, 0, {
                            'bom_line_id': i.id,
                            'product_id': i.product_id.id,
                            'avl_quantity': i.balance_quantity,
                            'quantity': i.balance_quantity,
                            'uom_id': i.uom_id.id,
                            'cost': i.cost
                        }))
            self.write({'material_request_line_ids': cost_list})

    def action_select_all(self):
        for i in self.material_request_line_ids:
            if i.is_select == False:
                i.is_select = True

    def action_deselect_all(self):
        for i in self.material_request_line_ids:
            if i.is_select == True:
                i.is_select = False

    def action_in_review(self):
        line_len = len([i for i in self.material_request_line_ids if i.is_select])
        line_qty = [i for i in self.material_request_line_ids if
                    i.is_select and (i.quantity <= 0 or i.quantity > i.avl_quantity)]
        if not line_len:
            raise ValidationError('You need to select a line before Review')
        if len(line_qty):
            for i in line_qty:
                raise ValidationError(
                    _("The selected quantity must be greater than 0 and less than or equal to the available quantity of %s for the product: %s") % (
                        i.avl_quantity, i.product_id.name))
        self.state = 'in_review'

    def action_approve(self):
        line_len = len([i for i in self.material_request_line_ids if i.is_select])
        line_qty = [i for i in self.material_request_line_ids if
                    i.is_select and (i.quantity <= 0 or i.quantity > i.avl_quantity)]
        if not line_len:
            raise ValidationError('You need to select a line before Review')
        if len(line_qty):
            for i in line_qty:
                raise ValidationError(
                    _("The selected quantity must be greater than 0 and less than or equal to the available quantity of %s for the product: %s") % (
                        i.avl_quantity, i.product_id.name))
        picking_type = self.env.company.operational_type_id
        if picking_type:
            picking = self.env['stock.picking'].sudo().create({
                'picking_type_id': picking_type.id,
                'company_id': self.env.company.id,
                'origin': 'Material Request %s' % self.name,
                'project_id': self.project_id.id,
                'task_id': self.task_id.id,
                'scheduled_date': self.expected_date,
                'material_request_id': self.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id
            })
            for vals in self.material_request_line_ids:
                if vals.is_select and vals.quantity > 0 and vals.quantity <= vals.avl_quantity:
                    vals.bom_line_id.balance_quantity -= vals.quantity
                    vals.bom_line_id.mr_used_quantity += vals.quantity
                    picking.sudo().write({
                        'move_ids_without_package': [(0, 0, {
                            'product_id': vals.product_id.id,
                            'name': vals.product_id.name,
                            'product_uom_qty': vals.quantity,
                            'product_uom': vals.uom_id.id,
                            'location_id': picking_type.default_location_src_id.id,
                            'location_dest_id': picking_type.default_location_dest_id.id,
                            'analytic_account_id': self.project_id.analytic_account_id.id
                        })]
                    })
                else:
                    vals.unlink()
        else:
            raise ValidationError('Operation type not set in your company!')
        self.state = 'approved'

    def action_reset(self):
        self.state = 'draft'

    def action_cancel(self):
        picking = self.env['stock.picking'].sudo().search([('material_request_id', '=', self.id)])
        if any(states == 'done' for states in picking.mapped('state')):
            raise ValidationError("Transfer is in done state.")
        else:
            for i in picking:
                i.action_cancel()
            if self.state == 'approved':
                for j in self.material_request_line_ids:
                    j.bom_line_id.balance_quantity += j.quantity
                    j.bom_line_id.mr_used_quantity -= j.quantity
        self.state = 'cancelled'

    def button_open_picking(self):
        return {
            'name': _('Transfers'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('material_request_id', '=', self.id)],
            'context': {'create': False, 'delete': False}
        }

    def _compute_transfer_count(self):
        for pick in self:
            picking = self.env['stock.picking'].sudo().search([('material_request_id', '=', pick.id)])
            pick.transfer_count = len(picking)

    def unlink(self):
        for rec in self:
            if rec.state == 'approved':
                raise ValidationError(
                    'You cannot delete a material request that in approved state.')
        return super(MaterialRequest, self).unlink()


class MaterialRequestLines(models.Model):
    _name = 'material.request.line'

    is_select = fields.Boolean(string="Select", default=True)
    line_id = fields.Many2one('material.request')
    product_id = fields.Many2one('product.product', string='Product')
    avl_quantity = fields.Float(string="BOM Qty")
    quantity = fields.Float(string="Qty")
    uom_id = fields.Many2one('uom.uom', 'UOM')
    cost = fields.Float(string='Cost')
    total = fields.Float(string='Total', compute='_compute_line_total', store=True)
    bom_line_id = fields.Many2one('bom.line', string='Cost BOM')

    is_true = fields.Boolean(string='Is True', compute='_compute_get_line_true')

    @api.depends('cost', 'quantity')
    def _compute_line_total(self):
        for i in self:
            i.total = i.quantity * i.cost

    def _compute_get_line_true(self):
        for i in self:
            i.is_true = True if i.is_select and i.quantity > 0 and i.quantity <= i.avl_quantity else False

    @api.onchange('is_select', 'quantity')
    def _onchange_material_request_line_value(self):
        for i in self:
            i._compute_get_line_true()
