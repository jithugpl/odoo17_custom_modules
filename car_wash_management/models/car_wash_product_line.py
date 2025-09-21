from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CarWashProductLine(models.Model):
    _name = 'car.wash.product.line'

    appointment_id = fields.Many2one('car.wash.appointment', string="Appointment")
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    price_unit = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.uom_id = rec.product_id.uom_id
            rec.price_unit = rec.product_id.lst_price

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price_unit
