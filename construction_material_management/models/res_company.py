import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    operational_type_id = fields.Many2one('stock.picking.type', string='Transfer Operational Type', tracking=True)
    manufacture_operational_type_id = fields.Many2one('stock.picking.type', string='Manufacture Operational Type',
                                                      tracking=True)

    purchase_requisition_type = fields.Selection(
        [('cost_bom', 'Cost BOM'), ('transfer', 'Transfer')], default='cost_bom',
        string="Purchase Requisition", required=True, tracking=True)

    site_material_transfer_journal_id = fields.Many2one('account.journal',
                                                        string='Site To Site Material Transfer Journal', tracking=True)
    site_material_transfer_credit_account_id = fields.Many2one('account.account',
                                                               string='Site To Site Material Transfer Credit Account',
                                                               tracking=True)
    site_material_transfer_debit_account_id = fields.Many2one('account.account',
                                                              string=' Site To Site Material Transfer Debit Account',
                                                              tracking=True)
