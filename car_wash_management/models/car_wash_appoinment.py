from odoo import models, fields,api
from odoo.exceptions import ValidationError



class CarWashAppointment(models.Model):
    _name = 'car.wash.appointment'
    _description = 'Car Wash Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    # customer_id = fields.Many2one('res.partner', string='Customer')
    customer_id = fields.Many2one('res.partner', string="Customer", related='vehicle_number_id.customer_id',
                                  readonly=True, store=True)
    vehicle_type_id = fields.Many2one('vehicle.type', string="Vehicle Type",
                                      related='vehicle_number_id.vehicle_type_id', readonly=True, store=True)

    vehicle_number_id = fields.Many2one('vehicle.details', string="Vehicle number", required=True, tracking=True)
    # vehicle_number = fields.Char(string='Vehicle Number')
    # vehicle_type_id = fields.Many2one('vehicle.type', string="Vehicle Type")
    rate = fields.Float(string="Rate", compute="_compute_rate", store=True, readonly=True)
    discount = fields.Float(string="Discount", default=0.0)
    # rate = fields.Float(string="Rate")
    wash_type_id = fields.Many2one('car.wash.type', string='Wash Type' )
    employee_id = fields.Many2one('hr.employee', string='In-Charge' , tracking=True, required=True)
    in_time = fields.Datetime(string='In-Time' ,tracking=True ,required=True)
    customer_mobile = fields.Char(string="Mobile", related='customer_id.mobile', readonly=True)
    final_amount = fields.Float(string="Total Amount", compute="_compute_final_amount", store=True)
    billing_line_ids = fields.One2many('car.wash.billing.line', 'appointment_id', string="Billing Lines")
    subtotal_amount = fields.Float(string="Subtotal", compute='_compute_subtotal_amount', store=True)
    is_pickup = fields.Boolean(string="Pickup Required?" ,tracking=True)
    pickup_employee_id = fields.Many2one('hr.employee', string="Pickup Person", tracking=True)
    pickup_time = fields.Datetime(string="Pickup Time", tracking=True)
    drop_employee_id = fields.Many2one('hr.employee', string="Drop Person" ,tracking=True)
    drop_time = fields.Datetime(string="Drop Time" ,tracking=True)
    product_line_ids = fields.One2many(
        'car.wash.product.line',
        'appointment_id',
        string="Sold Products"
    )

    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    @api.depends('billing_line_ids.total_amount', 'product_line_ids.subtotal')
    def _compute_total_amount(self):
        for rec in self:
            billing_total = sum(line.total_amount for line in rec.billing_line_ids)
            product_total = sum(line.subtotal for line in rec.product_line_ids)
            rec.total_amount = billing_total + product_total
    # is_pickup = fields.Boolean(string="Pickup Required?")
    # pickup_employee_id = fields.Many2one(
    #     'hr.employee', string="Pickup Person")
    # pickup_time = fields.Datetime(string="Pickup Time")
    #
    # drop_employee_id = fields.Many2one(
    #     'hr.employee', string="Drop Person")
    # drop_time = fields.Datetime(string="Drop Time")


    @api.constrains('billing_line_ids')
    def _check_one_line_only(self):
        for rec in self:
            if len(rec.billing_line_ids) > 1:
                raise ValidationError("Only one billing line is allowed.")
    @api.onchange('billing_line_ids')
    def _onchange_billing_line_ids(self):
        for rec in self:
            if len(rec.billing_line_ids) > 1:
                return {
                    'warning': {
                        'title': "Only one line allowed",
                        'message': "You can only add one billing line.",
                        'type': 'warning',
                    }
                }

    @api.onchange('is_pickup')
    def _onchange_is_pickup(self):
        if not self.is_pickup:
            self.pickup_employee_id = False
            self.pickup_time = False
            self.drop_employee_id = False
            self.drop_time = False

    @api.depends('billing_line_ids.total_amount')
    def _compute_subtotal_amount(self):
        for rec in self:
            rec.subtotal_amount = sum(rec.billing_line_ids.mapped('total_amount'))

    state = fields.Selection([
        ('new', 'New'),
        ('started', 'Started'),
        ('pending', 'Pending'),
        ('finished', 'Finished'),
        ('delivered', 'Delivered'),
    ], string='Status', default='new', tracking=True)

    # Button methods
    def action_start(self):
        self.state = 'started'

    def action_pending(self):
        self.state = 'pending'

    def action_finish(self):
        self.state = 'finished'

    def action_deliver(self):
        self.state = 'delivered'

    # @api.depends('vehicle_type_id')
    # def _compute_rate(self):
    #     for rec in self:
    #         rec.rate = rec.vehicle_type_id.rate if rec.vehicle_type_id else 0.0

    @api.depends('vehicle_type_id', 'wash_type_id')
    def _compute_rate(self):
        for rec in self:
            vehicle_rate = rec.vehicle_type_id.rate if rec.vehicle_type_id else 0.0
            wash_price = rec.wash_type_id.price if rec.wash_type_id else 0.0
            rec.rate = vehicle_rate + wash_price

    @api.depends('rate', 'discount')
    def _compute_final_amount(self):
        for rec in self:
            discount_amount = (rec.rate * rec.discount) / 100 if rec.discount else 0.0
            rec.final_amount = rec.rate - discount_amount