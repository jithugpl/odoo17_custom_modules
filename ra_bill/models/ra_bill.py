# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError


class RunningBill(models.Model):
    _name = 'running.bill'
    _description = 'Running Bill'
    _inherit = ['portal.mixin', 'mail.thread.main.attachment', 'mail.activity.mixin']
    _order = 'id DESC'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), tracking=True)

    project_id = fields.Many2one('project.project', string='Project', copy=False)
    partner_id = fields.Many2one(related='project_id.partner_id', store=True)
    sale_id = fields.Many2one('sale.order', string='Work Order', copy=False)

    date = fields.Date(string='Date', default=fields.Date.today())
    ra_line_ids = fields.One2many('running.bill.line', 'line_id', string="Amendment Lines")
    order_type = fields.Selection(
        [('work_order', 'Work Order'), ('extra_work_order', 'Extra Work Order')],
        string='Order Type', default='work_order', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        string='State', default='draft', readonly=True)
    ra_sequence = fields.Char(string='RA Sequence', copy=False, readonly=True)

    project_sale_ids = fields.Many2many('sale.order', string="Project Sale Ids",
                                        compute='_compute_get_project_sale_ids')

    @api.onchange('project_id')
    def _onchange_ra_bill_project_id(self):
        self.sale_id = False
        self.ra_line_ids = False

    @api.onchange('sale_id')
    def _onchange_ra_bill_sale_id(self):
        self.order_type = self.sale_id.order_type
        self.ra_line_ids = False

    def action_done(self):
        line_len = len([i for i in self.ra_line_ids if i.present_quantity > 0])
        if not line_len:
            raise ValidationError('You need to add the present quantity before finishing.')
        if self.ra_line_ids.filtered(lambda l: l.cum_quantity > l.quantity):
            raise ValidationError("Quantity is greater than the order")
        if self.project_id:
            project_id = self.project_id
            if self.order_type == 'work_order':
                last_record = self.search(
                    [('project_id', '=', project_id.id), ('order_type', '=', 'work_order'), ('state', '=', 'done')],
                    order='id desc', limit=1)
                if last_record:
                    if last_record.ra_sequence:
                        last_sequence_number = int(last_record.ra_sequence[4:])
                        new_sequence_number = last_sequence_number + 1
                    else:
                        new_sequence_number = 1
                else:
                    new_sequence_number = 1
                self.write({'ra_sequence': 'RA{:04d}'.format(new_sequence_number)})
            else:
                last_record = self.search(
                    [('project_id', '=', project_id.id), ('order_type', '=', 'extra_work_order'),
                     ('state', '=', 'done')],
                    order='id desc', limit=1)
                if last_record:
                    if last_record.ra_sequence:
                        last_sequence_number = int(last_record.ra_sequence[4:])
                        new_sequence_number = last_sequence_number + 1
                    else:
                        new_sequence_number = 1
                else:
                    new_sequence_number = 1
                self.write({'ra_sequence': 'ARA{:04d}'.format(new_sequence_number)})
        self.state = 'done'

    def action_reset(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancelled'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('running.bill.seq') or _('New')
        res = super(RunningBill, self).create(vals)
        return res

    def action_get_product(self):
        if self.sale_id:
            self._cr.execute(
                """DELETE FROM running_bill_line where running_bill_line.line_id = %s""" % self._origin.id)
            for sale in self.sale_id.order_line:
                previous_amt = self.env['running.bill.line'].sudo().search(
                    [('sale_line_id', '=', sale.id), ('line_id.state', '=', 'done')])
                self.sudo().write({
                    'ra_line_ids': [(0, 0, {
                        'product_id': sale.product_id.id,
                        'quantity': sale.product_uom_qty,
                        'uom_id': sale.product_uom.id,
                        'unit_price': sale.price_unit,
                        'sale_line_id': sale.id,
                        'previous_quantity': sum(previous_amt.mapped('present_quantity')),
                        'previous_amount': sum(previous_amt.mapped('total')),
                        'description': sale.name
                    })]
                })

    def _compute_get_project_sale_ids(self):
        for record in self:
            project = record.project_id
            sale_order_line = self.env['sale.order.line'].sudo().search(
                [('project_id', '=', project.id), ('order_id.state', '=', 'sale')])
            done_sale_ids = sale_order_line.mapped('order_id').filtered(lambda p: p.state == 'sale').ids
            record.project_sale_ids = [(6, 0, done_sale_ids)]


class AmendmentRequestLines(models.Model):
    _name = 'running.bill.line'

    line_id = fields.Many2one('running.bill', string="Line", ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='WO Qty', help="The original number of quantities in the order.")
    present_quantity = fields.Float(string='Present Qty', help="The number of quantities entered.")
    previous_quantity = fields.Float(string='Previous Qty',
                                     help="The number of quantities entered in previous orders.")
    previous_amount = fields.Float(string='Previous Amount', help="The amount entered in previous orders.")
    cum_quantity = fields.Float(string='Cumulative Qty', compute='_compute_cum_quantity', store=True)
    uom_id = fields.Many2one('uom.uom', string='Unit')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    unit_price = fields.Float(string='Unit Price')
    total = fields.Float(string='Untaxed Amount', compute='_compute_total', store=True)

    description = fields.Html(string='Description')

    @api.depends('unit_price', 'present_quantity')
    def _compute_total(self):
        for line in self:
            line.total = line.present_quantity * line.unit_price

    @api.depends('previous_quantity', 'present_quantity')
    def _compute_cum_quantity(self):
        for run in self:
            run.cum_quantity = (run.present_quantity + run.previous_quantity)
