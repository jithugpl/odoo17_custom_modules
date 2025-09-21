#power_factor_reading/models/power_factor_reading.py

import datetime
#from odoo.addons.lunch.models.lunch_supplier import time_to_float
#from addons.lunch.models.lunch_supplier import time_to_float
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.populate import compute
from odoo.tools.safe_eval import pytz


class PowerFactorRecord(models.Model):
    _name = 'power.factor.record'
    _description = 'Power Factor Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'date'

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        index=True,
        default=lambda self: self.env.company
    )
    shift_number = fields.Many2one(
        'iso.masters.shift',  # Reference to the IsoMaster model
        string='Shift Number',
        required=True,
        tracking=True,
    )
    meter_name  = fields.Many2one(
        'iso.masters.meter',  # Reference to the IsoMaster model
        string='Meter Name',
        required=True,
        tracking=True,
    )
    recording_time = fields.Float(
        string='Recorded Time',
        required=True,
        digits=(2, 2),
        tracking=True,
        readonly=True,
        compute="_compute_recording_time",
    store = True

    )
    power_factor = fields.Float(
        string='Power Factor (p.u.)',
        digits=(3, 2),
        required=True,
        tracking=True,
        help="Power factor reading in per unit (p.u.)"
    )
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approved', 'Approved')
        ],
        string='Status',
        required=True,
        default='draft',
        tracking=True
    )

    from datetime import datetime
    import pytz

    # @api.model
    # def create(self, vals):
    #     """Ensure the recording time is set to the current time on record creation."""
    #     # Define the time zone
    #     tz = pytz.timezone('Asia/Kolkata')  # Indian Standard Time
    #     # Check if 'recording_time' is not provided or is set to 0
    #     if vals.get('recording_time') in [False, 0]:
    #         # Get the current time in the specified time zone
    #         now = datetime.datetime.now(tz)
    #         print(now)
    #         # Extract hour and minute
    #         hour = now.hour
    #         minute = now.minute
    #         print(f"{hour}.{minute:02d}")
    #         # Format the decimal time to HH.MM
    #         decimal_time = f"{hour}.{minute:02d}"
    #         # Correct usage with the module
    #         # Convert to decimal hours
    #
    #         vals['recording_time'] = decimal_time
    #
    #     # Call the parent create method to actually create the record with the updated vals
    #     result = super(PowerFactorRecord, self).create(vals)
        #return result

    @api.depends('power_factor')  # Triggers the compute method when a record is created or modified
    def _compute_recording_time(self):
        tz = pytz.timezone('Asia/Kolkata')  # Indian Standard Time
        for record in self:
            # Get the current time in the specified time zone
            now = datetime.datetime.now(tz)
            # Extract hour and minute
            hour = now.hour
            minute = now.minute
            # Compute the decimal time
            decimal_time = f"{hour}.{minute:02d}"
            print("compute_recording_time works")
            # Assign the computed value
            record.recording_time =decimal_time

            # Optional: round to 2 decimal places




    @api.constrains('recording_time')
    def _check_recording_time(self):
        for record in self:
            # Check for non-negative time
            if record.recording_time <= 0:
                raise ValidationError("Recorded Time must be greater than zero.")
            # Check for maximum time limit (example: 24 hours)
            if record.recording_time > 24.00:
                raise ValidationError("Recorded Time must be less than or equal to 24.00.")

            # Check for unique time per shift
            # existing_records = self.search([
            #     # ('shift_number', '=', record.shift_number.id),
            #     # ('recording_time', '=', record.recording_time),
            #     ('id', '!=', record.id)  # Exclude the current record
            # ])
            # if existing_records:
            #     raise ValidationError("The recorded time must be unique.")

    def action_approve(self):
        """Set the record's status to 'Approved'."""
        for record in self:
            record.status = 'approved'

    def action_set_to_draft(self):
        """Set the record's status back to 'Draft'."""
        for record in self:
            record.status = 'draft'

    _sql_constraints = [
        ('unique_shift_meter_time', 'UNIQUE(shift_number, meter_name, recording_time)',
         'A record with the same shift, meter, and recording time already exists!')
    ]








