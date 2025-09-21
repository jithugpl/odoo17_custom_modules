from odoo import models, fields, _


class DispatchReportWizard(models.TransientModel):
    _name = "dispatch.report.wizard"
    _description = "Dispatch Report Wizard"

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    project_name = fields.Many2one('project.project', string='Project Name')
    product_id = fields.Many2one('product.product', string='Product')



    def action_open_report(self):
        self.env['aggregated.delivery.data'].create_aggregated_data()
        domain = []

        if self.from_date:
            domain.append(('delivery_date', '>=', self.from_date))  # Ensure 'delivery_date' is correct
        if self.to_date:
            domain.append(('delivery_date', '<=', self.to_date))  # Ensure 'delivery_date' is correct
        if self.project_name:
            domain.append(('project_name', '=', self.project_name.id))  # Ensure 'project_name' is correct

        if self.product_id:
            domain.append(('product_name', '=', self.product_id.id))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Notes'),
            'view_mode': 'tree,form',
            'res_model': 'aggregated.delivery.data',
            'views': [(self.env.ref('delivery_form.aggregated_delivery_data_tree').id, 'tree')],
            'domain': domain,
            'target': 'current',
        }





