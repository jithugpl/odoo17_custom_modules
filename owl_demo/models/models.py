from odoo import models, fields


class jsClass(models.Model):
    _name = "js.class"
    _description = "description"
    name = fields.Char(string="Field Label", required=False, readonly=False, index=False, default="Default Value")
    number_of_video= fields.Integer(string="Number of Videos", required=False, readonly=False,)
    assestsName=fields.Many2one('assets.request', string="Assests name", required=False)

class Assests(models.Model):
    _name = "assets.request"
    _description = "description"
    name = fields.Char(string="Assests ",)
    description= fields.Char(string="Description", )
