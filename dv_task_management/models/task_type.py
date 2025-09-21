from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class TaskType(models.Model):
    _name = 'task.type'
    _description = 'Task Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Task Type Name', required=True)


class TraineeType(models.Model):
    _name = 'trainee.type'
    _description = 'Trainee Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Trainee Type Name', required=True, tracking=True)
    user_ids = fields.Many2many('res.users', string='Users', tracking=True)

    @api.constrains('user_ids')
    def _check_unique_users(self):
        all_users = self.env['trainee.type'].search([])
        for record in self:
            for user in record.user_ids:
                for other_type in all_users:
                    if other_type.id != record.id and user in other_type.user_ids:
                        raise ValidationError(
                            f"User '{user.name}' is already assigned to another Trainee Type: '{other_type.name}'." )

class TaskManager(models.Model):
    _name = 'task.manager'
    _description = 'Task Manager'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Task Name', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string="User", tracking=True)
    trainee_type_id = fields.Many2one('trainee.type', string="Trainee Type", readonly=True, tracking=True)
    @api.model
    def create(self, vals):
        if vals.get('user_id') and not vals.get('trainee_type_id'):
            trainee_type = self.env['trainee.type'].search([
                ('user_ids', 'in', vals['user_id'])
            ], limit=1)
            vals['trainee_type_id'] = trainee_type.id if trainee_type else False
        return super().create(vals)

    def write(self, vals):
        if vals.get('user_id') and 'trainee_type_id' not in vals:
            trainee_type = self.env['trainee.type'].search([
                ('user_ids', 'in', vals['user_id'])
            ], limit=1)
            vals['trainee_type_id'] = trainee_type.id if trainee_type else False
        return super().write(vals)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            trainee_type = self.env['trainee.type'].search([
                ('user_ids', 'in', self.user_id.id)
            ], limit=1)
            self.trainee_type_id = trainee_type or False

            if not trainee_type:
                return {
                    'warning': {
                        'title': "No Employee Type",
                        'message': "This user is not assigned to any Employee Type.",
                    }
                }
        else:
            self.trainee_type_id = False

    poa = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ], string='POA', required=True, tracking=True)
    from_date = fields.Date(string='From Date', tracking=True)
    to_date = fields.Date(string='To Date', tracking=True)
    task_type_id = fields.Many2one('task.type', string='Task Type', tracking=True)  # Link to Task Type Master
    percentage_completed = fields.Float(string='Percentage Completed', tracking=True)
    description = fields.Text(string='Description', tracking=True)  # <-- Description field added here

    daily_work_progress_ids = fields.One2many(
        'daily.work.progress', 'task_id', string="Daily Work Progress"
    )

    # Stage field
    stage = fields.Selection([
        ('new', 'New'),
        ('ongoing', 'Ongoing'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed')
    ], string='Stage', default='new', tracking=True, group_expand='_group_expand_stage' )

    def action_start_task(self):
        for rec in self:
            rec.stage = 'ongoing'

    def action_complete_task(self):
        for rec in self:
            rec.stage = 'completed'
        # Ensure the stage is set to 'ongoing' before completing
    def action_dropped_task(self):
        for rec in self:
            rec.stage = 'dropped'

    def action_cancel_task(self):
        for rec in self:
            rec.stage = 'new'
    @api.onchange('poa')
    def _onchange_poa(self):
        if self.poa == 'daily':
            today = date.today()
            self.from_date = today
            self.to_date = today
        elif self.poa == 'weekly':
            today = date.today()
            self.from_date = today
            self.to_date = False

    @api.model
    def _group_expand_stage(self, stages, domain, order):
        return ['new', 'ongoing','dropped', 'completed']


class DailyWorkProgress(models.Model):
    _name = 'daily.work.progress'
    _description = 'Daily Work Progress'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    # task_id = fields.Many2one('task.manager', string="Task", required=True, ondelete='cascade')
    note = fields.Text(string="Note")
    task_id = fields.Many2one('task.manager', string="Task")


    attachment_ids = fields.Many2many(
        'ir.attachment',
        'daily_work_progress_ir_attachments_rel',
        'progress_id', 'attachment_id',
        string="Attachments",
        domain=[('res_model', '=', 'daily.work.progress')],
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.task_id:
            attachments = ""
            if record.attachment_ids:
                attachment_links = [
                    f'{att.name}'
                    for att in record.attachment_ids
                ]
                attachments = "Attachments:" + "".join(attachment_links)
            record.task_id.message_post(
                body=f"New daily work progress added:Note: {record.note or 'No note'}{attachments}",
                message_type='comment'
            )
        return record


    def write(self, vals):
        for rec in self:
            old_attachments = rec.attachment_ids.ids  # capture before write

        res = super().write(vals)

        for rec in self:
            if rec.task_id:
                changes = []

                if 'note' in vals:
                    changes.append(f"Note updated: {vals['note']}")

                if 'attachment_ids' in vals:
                    new_attachments = rec.attachment_ids.ids
                    added = list(set(new_attachments) - set(old_attachments))
                    removed = list(set(old_attachments) - set(new_attachments))

                    added_names = [
                        att.name for att in self.env['ir.attachment'].browse(added)
                    ]
                    removed_names = [
                        att.name for att in self.env['ir.attachment'].browse(removed)
                    ]

                    if added_names:
                        changes.append("Added Attachments: " + ", ".join(added_names))
                    if removed_names:
                        changes.append("Removed Attachments: " + ", ".join(removed_names))

                if changes:
                    rec.task_id.message_post(
                        body="".join(changes),
                        message_type='comment'
                    )
        return res





