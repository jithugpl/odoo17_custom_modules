from odoo import models, fields, api

class VehicleDetails(models.Model):
    _name = 'vehicle.details'
    _description = 'Vehicle Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Vehicle Number", required=True ,tracking=True)
    customer_id = fields.Many2one('res.partner', string="Customer", required=True ,tracking=True)
    vehicle_type_id = fields.Many2one('vehicle.type', string="Vehicle Type", required=True ,tracking=True)
    brand = fields.Char(string="Brand" ,tracking=True)
    model = fields.Char(string="Model" ,tracking=True)
    notes = fields.Text(string="Notes" ,tracking=True)

    # Computed One2many fields
    wash_appointment_ids = fields.One2many(
        'car.wash.appointment', 'vehicle_number_id',
        string="Wash History"
    )

    detailing_appointment_ids = fields.One2many(
        'detailing.appointment', 'vehicle_number_id',
        string="Detailing History"
    )

    # @api.depends('id')
    # def _compute_wash_appointments(self):
    #     for rec in self:
    #         rec.wash_appointment_ids = self.env['car.wash.appointment'].search([
    #             ('vehicle_number_id', '=', rec.id)
    #         ])
    #
    # @api.depends('id')
    # def _compute_detailing_appointments(self):
    #     for rec in self:
    #         rec.detailing_appointment_ids = self.env['detailing.appointment'].search([
    #             ('vehicle_number_id', '=', rec.id)
    #         ])
