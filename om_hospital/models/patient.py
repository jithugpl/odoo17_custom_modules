from odoo import models, fields, api



class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _description = "Hospital Patient"

    name=fields.Char(string="name")
