import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    material_request_id = fields.Many2one('material.request', string='Material Request')
    amendment_request_id = fields.Many2one('amendment.request', string='Amendment Request')
    project_id = fields.Many2one('project.project', string='Project')
    task_id = fields.Many2one('project.task', string='Task')

    manufacture_count = fields.Integer(string='Manufacture count', compute='_compute_manufacture_count')

    purchase_requisition_count = fields.Integer(string='Purchase Requisition Count',
                                                compute='_compute_purchase_requisition_count')
    show_purchase_requisition = fields.Boolean(string='Show Requisition',
                                               compute='_compute_show_purchase_requisition_button')
    supplier_reference = fields.Char(string='Supplier Invoice No')
    is_manufacture_order = fields.Boolean(related='picking_type_id.is_manufacture_order', store=True)

    inv_bill_generated = fields.Boolean(string='Bill Generated', copy=False)

    def action_manufacture(self):
        if any(line.is_manufacture and not line.is_manufacture_created for line in self.move_ids_without_package):
            picking_type = self.env.company.manufacture_operational_type_id
            for line in self.move_ids_without_package:
                if line.is_manufacture:
                    manufacture_order = self.env['mrp.production'].create({
                        'product_id': line.product_id.id,
                        'product_qty': line.quantity,
                        'picking_type_id': picking_type.id,
                        'location_src_id': picking_type.default_location_src_id.id,
                        'location_dest_id': picking_type.default_location_dest_id.id,
                        'stock_picking_id': self.id,
                    })
                    manufacture_order._compute_bom_id()
                    line.is_manufacture_created = True
        else:
            raise ValidationError("No Product to manufacture.")

    def button_manufacture(self):
        mrp = self.env['mrp.production'].sudo().search([('stock_picking_id', '=', self.id)])
        action = self.env['ir.actions.act_window']._for_xml_id('mrp.mrp_production_action')
        mrp_list = mrp.mapped('id')
        if len(mrp_list) == 1:
            action['views'] = [(self.env.ref('mrp.mrp_production_form_view').id, 'form')]
            action['res_id'] = mrp_list[0]
        else:
            action['domain'] = [('id', 'in', mrp_list)]
        return action

    def _compute_manufacture_count(self):
        for manufacture in self:
            mrp = self.env['mrp.production'].sudo().search([('stock_picking_id', '=', manufacture.id)])
            manufacture.manufacture_count = len(mrp)

    #####Create Purchase Requisition#####
    def action_create_purchase_requisition(self):
        material_line_filtered_lines = self.move_ids_without_package.filtered(
            lambda i: i.product_uom_qty != i.quantity and i.requisition_quantity < (i.product_uom_qty - i.quantity))
        if len(material_line_filtered_lines) and self.project_id and self.picking_type_id.is_purchase_requisition:
            requisition = self.env['material.purchase.requisition'].sudo().create({
                'project_id': self.project_id.id,
                'picking_ids': [(6, 0, self.ids)],
                'stock_picking_id': self.id
            })
            for line in material_line_filtered_lines:
                #####condition#####
                req_qty = line.product_uom_qty - line.quantity
                if line.requisition_quantity < req_qty:
                    check_line_value = line.quantity + line.requisition_quantity
                    if check_line_value <= req_qty:
                        pro_qty = req_qty - line.requisition_quantity
                        line.requisition_quantity += pro_qty
                    else:
                        pro_qty = req_qty - line.requisition_quantity
                        line.requisition_quantity += pro_qty
                    #####end#####
                    requisition.write({
                        'requisition_line_ids': [(0, 0, {
                            'product_id': line.product_id.id,
                            'qty': pro_qty,
                            'picking_id': self.id
                        })]
                    })

    def action_show_requisition(self):
        return {
            'name': _('Purchase Requisition'),
            'type': 'ir.actions.act_window',
            'res_model': 'material.purchase.requisition',
            'view_mode': 'tree',
            'domain': [('stock_picking_id', '=', self.id)],
            'context': {'create': False, 'delete': False, 'edit': False}
        }

    def _compute_purchase_requisition_count(self):
        for i in self:
            pur = self.env['material.purchase.requisition'].sudo().search([('stock_picking_id', '=', i.id)])
            i.purchase_requisition_count = len(pur)

    def _compute_show_purchase_requisition_button(self):
        for rec in self:
            material_line_filtered_lines = rec.move_ids_without_package.filtered(
                lambda i: i.product_uom_qty != i.quantity and i.requisition_quantity < (i.product_uom_qty - i.quantity))
            if (len(material_line_filtered_lines) and rec.project_id and rec.picking_type_id.is_purchase_requisition and
                    rec.state in ('waiting', 'confirmed', 'assigned')):
                rec.show_purchase_requisition = True
            else:
                rec.show_purchase_requisition = False


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    is_manufacture = fields.Boolean(string='Is Manufacture')
    is_manufacture_created = fields.Boolean(string='Is Manufacture Created')
    is_purchase_created = fields.Boolean(string='Is Purchase Created')

    requisition_quantity = fields.Float(string='Requisition Quantity')

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id, svl_id, description):
        res = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value,
                                                                    debit_account_id, credit_account_id, svl_id,
                                                                    description)
        res['debit_line_vals']['analytic_line_ids'] = [(6, 0, self.analytic_account_id.ids)]
        res['credit_line_vals']['analytic_line_ids'] = [(6, 0, self.analytic_account_id.ids)]
        return res
