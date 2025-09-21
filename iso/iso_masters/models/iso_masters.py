from odoo import models, fields
#iso_masters/models/iso_masters.py:18
class IsoMasterShift(models.Model):
    _name = 'iso.masters.shift'
    _description = 'General Master for Module'
    _rec_name = "shift_name"
    shift_name = fields.Char(string='Shift Name', required=True)
    _sql_constraints = [
        ('shift_name_unique', 'UNIQUE(shift_name)', 'Duplicate shift names are not allowed!')
    ]


class IsoMasterMeter(models.Model):
    _name = 'iso.masters.meter'
    _description = 'General Master for Module'
    _rec_name = "power_meter_name"
    power_meter_name = fields.Char(string='Power Meter Name', required=True)
    _sql_constraints = [
        ('power_meter_name_unique', 'UNIQUE(power_meter_name)', 'Duplicate meter names are not allowed!')
    ]


#
# from odoo import models, fields
#
# class IsoMaster(models.Model):
#     _name = 'iso.masters'
#     _description = 'General Master for Module'
#
#
#     shift_name = fields.Char(string='Shift Name', required=True)
#     power_meter_name = fields.Char(string='Power Meter Name', required=True)
#
#
#
#     _sql_constraints = [
#         ('power_factor_master_unique', 'unique(shift_name, power_meter_name)', 'Duplicate entries are not allowed!')
#     ]
