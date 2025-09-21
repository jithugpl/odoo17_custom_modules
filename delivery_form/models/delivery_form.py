from odoo import models, fields, api, _


class DeliveryNote(models.Model):
    _name = "delivery.form"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # used to activate chatter
    _description = "Delivery Form"
    _rec_name = "delivery_no"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    # (used to set company rule)
    delivery_no = fields.Char(string='Delivery Number', required=True, readonly=True, default=lambda self: _('New'))
    delivery_date = fields.Date(string='Delivery Date')
    project_name = fields.Many2one(comodel_name='project.project', string='Project Name')
    product_line_ids = fields.One2many('delivery.form.lines', 'product_id', string='Product Lines')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    vehicle_no = fields.Char(string='Vehicle Number')
    customer_name = fields.Many2one(comodel_name='res.partner', string='Customer Name')
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)
    # (user id field is used to display activity in chatter)

    @api.model
    def create(self, vals):
        if vals.get('delivery_no', _('New')) == _('New'):
            vals['delivery_no'] = self.env['ir.sequence'].next_by_code('delivery.slip') or _('New')
        if not vals.get('user_id'):
            vals['user_id'] = self.env.user.id
        return super(DeliveryNote, self).create(vals)

    @api.depends('product_line_ids.amount')
    def _compute_total_amount(self):
        for note in self:
            note.total_amount = sum(line.amount for line in note.product_line_ids)

    @api.onchange('project_name')
    def _onchange_project_name(self):
        if self.project_name:
            self.customer_name = self.project_name.partner_id
        else:
            self.customer_name = False

    @api.model
    def create(self, vals):
        if vals.get('delivery_no', _('New')) == _('New'):
            vals['delivery_no'] = self.env['ir.sequence'].next_by_code('delivery.slip') or _('New')
        return super(DeliveryNote, self).create(vals)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('dispatch', 'Dispatched'),
        ('cancel', 'Cancelled'),
    ], default='draft', string="Status", required=True, tracking=True)

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_review(self):
        for rec in self:
            rec.state = 'review'

    def action_dispatch(self):
        for rec in self:
            rec.state = 'dispatch'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


class DeliveryNoteLines(models.Model):
    _name = "delivery.form.lines"

    product_id = fields.Many2one('delivery.form', 'Product')
    product_name = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    rate = fields.Float(string='Rate')
    amount = fields.Float(string='Amount', compute='_compute_amount', store=True)

    @api.depends('quantity', 'rate')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.rate

    @api.onchange('product_name')
    def _onchange_product_name(self):
        if self.product_name:
            self.rate = self.product_name.list_price
            self.description = self.product_name.description_sale  # Assuming description_sale field is used for the product description
            self.uom_id = self.product_name.uom_id  # Fetch the UOM from the product
        else:
            self.rate = 0.0
            self.description = ''
            self.uom_id = False


class AggregatedDeliveryData(models.Model):
    _name = 'aggregated.delivery.data'
    _description = 'Aggregated Delivery Data'

    delivery_no = fields.Char(string='Delivery Number')
    delivery_date = fields.Date(string='Delivery Date')
    project_name = fields.Many2one(comodel_name='project.project', string='Project Name')
    total_amount = fields.Float(string='Total Amount')
    vehicle_no = fields.Char(string='Vehicle Number')
    customer_name = fields.Many2one(comodel_name='res.partner', string='Customer Name')
    product_name = fields.Many2one(comodel_name='product.product', string='Product Name')
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit of Measure')
    rate = fields.Float(string='Rate')
    amount = fields.Float(string='Amount')
    user_id = fields.Many2one('res.users', string='Created By')

    @api.model
    def create_aggregated_data(self):
        self.search([]).unlink()  # Clear existing data
        delivery_notes = self.env['delivery.form'].search([])
        for delivery in delivery_notes:
            for line in delivery.product_line_ids:
                self.create({
                    'delivery_no': delivery.delivery_no,
                    'delivery_date': delivery.delivery_date,
                    'project_name': delivery.project_name.id,
                    'total_amount': delivery.total_amount,
                    'vehicle_no': delivery.vehicle_no,
                    'customer_name': delivery.customer_name.id,
                    'product_name': line.product_name.id,
                    'description': line.description,
                    'quantity': line.quantity,
                    'uom_id': line.uom_id.id,
                    'rate': line.rate,
                    'amount': line.amount,
                    'user_id': delivery.user_id.id,
                })
