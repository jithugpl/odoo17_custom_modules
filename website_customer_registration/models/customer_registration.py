from odoo import models, fields, api


#
# class CustomerRegistration(models.Model):
#     _name = 'customer.registration'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = 'Customer Registration'
#
#     name = fields.Char(string='Name', required=True)
#     email = fields.Char(string="Email", required=True)
#     phone = fields.Char(string="Phone")
#     address = fields.Text(string="Address")
#     registered_on = fields.Datetime(string="Registered On", default=fields.Datetime.now)
#     order_line_ids = fields.One2many('customer.registration.order.line', 'registration_id', string="Order Lines")
#
#     def action_open_create_task_wizard(self):
#         # Open the create task wizard with the context including default_customer_registration_id
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Create Task Wizard',
#             'res_model': 'create.task.wizard',
#             'view_mode': 'form',
#             'view_id': self.env.ref('website_customer_registration.view_create_task_wizard_form').id,
#             'target': 'new',
#             'context': {'default_customer_registration_id': self.id,
#                         'name':self.name},  # Include the context here
#         }
#
#
# class CustomerRegistrationOrderLine(models.Model):
#     _name = 'customer.registration.order.line'
#     _description = 'Customer Registration Order Line'
#
#     registration_id = fields.Many2one('customer.registration', string="Customer Registration", required=True,
#                                       ondelete='cascade')
#     file_name = fields.Char(string="File Name", required=True)
#     file = fields.Binary(string="File", required=True)  # This field allows file upload

# class CustomerRegistration(models.Model):
#     _inherit = 'res.partner'
#     order_line_ids = fields.One2many('customer.registration.file', 'registration_id', string="Order Lines")
#

# class CustomerRegistrationOrderLine(models.Model):
#     # _name = 'cureg'
#     _inherit = 'res.partner'
#     _description = 'Customer Registration Order Line'
#     #
#     # registration_id = fields.Many2one(
#     #     'res.partner',  # Changed from 'customer.registration' to 'res.partner'
#     #     string="Customer Registration",
#     #     required=True,
#     #     ondelete='cascade'
#     # )
#     registration_id = fields.Char(string="Registration ID")
#     file_name = fields.Char(string="File Name", required=True)
#     file = fields.Binary(string="File", required=True)  # This field allows file upload

class CustomerRegistrationFile(models.Model):
    _description = 'Customer Registration File'
    _inherit = 'res.partner'

    file_name = fields.Char(string="File Name", )
    file_data = fields.Binary(string="File", )

    # same_vat_partner_id = fields.Many2one('res.partner', string='Partner with same Tax ID',
    #                                        store=False)
    # partner_gid = fields.Integer('Company database ID', store=True)
    # additional_info = fields.Char('Additional info')
    # same_company_registry_partner_id = fields.Many2one('res.partner', string='Partner with same Company Registry', store=False)




# class CreateTaskWizard(models.TransientModel):
#     _name = 'create.task.wizard'
#     _description = 'Create Task Wizard'
#
#     project_id = fields.Many2one('project.project', string="Project", required=True)
#     customer_registration_id = fields.Many2one('customer.registration', string="Customer Registration",
#                                                compute='_compute_customer_registration_id')
#
#     @api.depends_context('default_customer_registration_id')
#     def _compute_customer_registration_id(self):
#         for record in self:
#             record.customer_registration_id = self.env.context.get('default_customer_registration_id')
#
#
#     def action_create_task(self):
#         # Create a task under the selected project and link it to the customer registration
#         # task_data = {
#         #     'name': f'Task for {self.customer_registration_id.name}',
#         #     'project_id': self.project_id.id,
#         #     'description': f'Task created from Customer Registration: {self.customer_registration_id.name}',
#         #     'partner_id':self.customer_registration_id
#         # }
#         # task = self.env['project.task'].create(task_data)
#         # return task
#         partner = self.env['res.partner'].create({
#             'name': self.customer_registration_id.name,
#             'email': self.customer_registration_id.email,
#             'phone': self.customer_registration_id.phone,
#         })
#
#         # Now create the task and link it to the partner
#         task_data = {
#             'name': f'Task for {self.customer_registration_id.name}',
#             'project_id': self.project_id.id,
#             'description': f'Task created from Customer Registration: {self.customer_registration_id.name}',
#             'partner_id': partner.id,
#         }
#         task = self.env['project.task'].create(task_data)
#         return task
#
#


# models/res_partner.py
from odoo import models, fields


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    file_attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    is_special_customer = fields.Selection(
        [('website_customer', 'Website Customer'), ('non_website_customer', 'Non Website Customer')],
        default='non_website_customer')

# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
#
#
# class CustomerRegistration(models.Model):
#     _name = 'customer.registration'
#     _description = 'Customer Registration'
#
#     name = fields.Char(string='Name', required=True)
#     email = fields.Char(string="Email", required=True)
#     phone = fields.Char(string="Phone")
#     address = fields.Text(string="Address")
#     registered_on = fields.Datetime(string="Registered On", default=fields.Datetime.now)
#     order_line_ids = fields.One2many('customer.registration.order.line', 'registration_id', string="Order Lines")
#
#     def action_open_create_task_wizard(self):
#         # Open the create task wizard
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Create Task Wizard',
#             'res_model': 'create.task.wizard',
#             'view_mode': 'form',
#             'view_id': self.env.ref('website_customer_registration.view_create_task_wizard_form').id,
#             'target': 'new',
#             'context': {'default_customer_registration_id': self.id},
#         }
#
#
# class CustomerRegistrationOrderLine(models.Model):
#     _name = 'customer.registration.order.line'
#     _description = 'Customer Registration Order Line'
#
#     registration_id = fields.Many2one('customer.registration', string="Customer Registration", required=True,
#                                                ondelete='cascade')
#     file_name = fields.Char(string="File Name", required=True)
#     file = fields.Binary(string="File", required=True)  # This field allows file upload
#
#
# class CreateTaskWizard(models.TransientModel):
#     _name = 'create.task.wizard'
#     _description = 'Create Task Wizard'
#
#     project_id = fields.Many2one('project.project', string="Project", required=True)
#     customer_registration_id = fields.Many2one('customer.registration',string="Customer Registration",
#                                                compute='_compute_customer_registration_id',store=True,)
#
#     @api.depends_context('default_customer_registration_id')
#     def _compute_customer_registration_id(self):
#         for record in self:
#             record.customer_registration_id = self.env.context.get('default_customer_registration_id')
#             print(record.customer_registration_id)
#
#     def action_create_task(self):
#         # Create a task under the selected project and link it to the customer registration
#
#         task_data = {
#             'name': f'Task for {self.customer_registration_id.name}',
#             'project_id': self.project_id.id,
#             'description': f'Task created from Customer Registration: {self.customer_registration_id.name}',
#         }
#         task = self.env['project.task'].create(task_data)
#         return task
#
#
# class CustomerRegistration(models.Model):
#     _inherit = 'customer.registration'
#
#     def action_open_create_task_wizard(self):
#         # Open the create task wizard
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Create Task Wizard',
#             'res_model': 'create.task.wizard',
#             'view_mode': 'form',
#             'view_id': self.env.ref('website_customer_registration.view_create_task_wizard_form').id,
#             'target': 'new',
#         }
