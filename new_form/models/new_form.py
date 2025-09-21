from odoo import models, fields, api, _


class NewForm(models.Model):
    _name = "new.form"
    _description = "Delivery Form"

    form_no = fields.Char(string='Form Number', required=True, readonly=True, default=lambda self: _('New'))
    vehicle_no = fields.Char(string='Vehicle Number')
    stage_id = fields.Many2one('new.form.stage', string="Stage", group_expand='_read_group_stage_ids', index=True)


    @api.model
    def create(self, vals):
        if vals.get('form_no', _('New')) == _('New'):
            vals['form_no'] = self.env['ir.sequence'].next_by_code('new.code') or _('New')

        return super(NewForm, self).create(vals)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return stages.search([], order=order)



class NewFormStage(models.Model):
    _name = "new.form.stage"
    _description = "New Form Stage"
    _order = "sequence"

    name = fields.Char(required=True, string="Stage Name")
    sequence = fields.Integer(default=1, string="Sequence")
    fold = fields.Boolean(string="Folded in Kanban", default=False)



