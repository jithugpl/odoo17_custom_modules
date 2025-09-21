from odoo import models, fields, api

class DetailingAppointment(models.Model):
    _name = 'detailing.appointment'
    _description = 'Detailing Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    customer_id = fields.Many2one('res.partner', string="Customer", related='vehicle_number_id.customer_id',
                                  readonly=True, store=True)
    vehicle_type_id = fields.Many2one('vehicle.type', string="Vehicle Type",
                                      related='vehicle_number_id.vehicle_type_id', readonly=True, store=True)

    vehicle_number_id = fields.Many2one('vehicle.details', string="Vehicle number", required=True)
    # vehicle_number = fields.Char(string='Vehicle Number')
    # vehicle_type_id = fields.Many2one('vehicle.type', string="Vehicle Type")
    # rate = fields.Float(string="Rate", compute="_compute_rate", store=True, readonly=True)
    rate = fields.Float(string="Rate")
    # wash_type_id = fields.Many2one('car.wash.type', string='Wash Type')
    detailing_type_id = fields.Many2one('car.detailing.type', string='Detailing Type')

    employee_id = fields.Many2one('hr.employee', string='In-Charge')
    scheduled_time = fields.Datetime(string='Scheduled Time')
    customer_mobile = fields.Char(string="Mobile", related='customer_id.mobile', readonly=True)

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

    @api.depends('vehicle_type_id')
    def _compute_rate(self):
        for rec in self:
            rec.rate = rec.vehicle_type_id.rate if rec.vehicle_type_id else 0.0

    # vehicle_number_id = fields.Many2one('vehicle.details', string="Vehicle Number", required=True)
    # customer_id = fields.Many2one('res.partner', string="Customer", related='vehicle_number_id.customer_id', readonly=True, store=True)
    # vehicle_type_id = fields.Many2one('vehicle.type', string="Vehicle Type", related='vehicle_number_id.vehicle_type_id', readonly=True, store=True)
    #
    # detailing_type_id = fields.Many2one('car.detailing.type', string="Detailing Type", required=True)
    # employee_id = fields.Many2one('hr.employee', string="Assigned To")
    # scheduled_time = fields.Datetime(string="Scheduled Time", required=True)
    # rate = fields.Float(string="Rate")
    #
    # state = fields.Selection([
    #     ('new', 'New'),
    #     ('started', 'Started'),
    #     ('pending', 'Pending'),
    #     ('finished', 'Finished'),
    #     ('delivered', 'Delivered'),
    # ], string='Status', default='new', tracking=True)
    #
    # def action_start(self):
    #     self.state = 'started'
    #
    # def action_pending(self):
    #     self.state = 'pending'
    #
    # def action_finish(self):
    #     self.state = 'finished'
    #
    # def action_deliver(self):
    #     self.state = 'delivered'
