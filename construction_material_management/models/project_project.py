from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    site_details = fields.Html(string='Site Details')


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    in_progress = fields.Boolean(string='In Progress', copy=False,
                                 help='Identify the task in progress in the material request.')
