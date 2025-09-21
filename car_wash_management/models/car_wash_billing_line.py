from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CarWashBillingLine(models.Model):
    _name = 'car.wash.billing.line'
    _description = 'Car Wash Billing Line'

    appointment_id = fields.Many2one('car.wash.appointment', string="Appointment", ondelete='cascade')
    wash_type_id = fields.Many2one('car.wash.type', string="Wash Type")
    vehicle_type_id = fields.Many2one('vehicle.type',string="Vehicle Type",related='appointment_id.vehicle_number_id.vehicle_type_id',
        readonly=True,store=True)

    # vehicle_type_id = fields.Many2one('vehicle.type', string="Vehicle Type")
    rate = fields.Float(string="Rate", compute="_compute_rate", store=True, readonly=True)

    # rate = fields.Float(string="Rate")
    discount = fields.Float(string="Discount (%)")
    discount_amount = fields.Float(string="Discount Amount", compute="_compute_discount_amount", store=True)
    total_amount = fields.Float(string="Total", compute="_compute_total_amount", store=True)

    @api.depends('vehicle_type_id', 'wash_type_id')
    def _compute_rate(self):
        for rec in self:
            vehicle_rate = rec.vehicle_type_id.rate if rec.vehicle_type_id else 0.0
            wash_price = rec.wash_type_id.price if rec.wash_type_id else 0.0
            rec.rate = vehicle_rate + wash_price

    @api.constrains('discount')
    def _check_discount_limit(self):
        for rec in self:
            if rec.discount < 0 or rec.discount > 100:
                raise ValidationError("Discount must be between 0 and 100%.")

    @api.depends('rate', 'discount')
    def _compute_discount_amount(self):
        for rec in self:
            if rec.discount and rec.rate:
                rec.discount_amount = (rec.discount / 100) * rec.rate
            else:
                rec.discount_amount = 0.0

    @api.depends('rate', 'discount')
    def _compute_total_amount(self):
        for line in self:
            discount_amt = (line.rate * line.discount) / 100 if line.discount else 0.0
            line.total_amount = line.rate - discount_amt
