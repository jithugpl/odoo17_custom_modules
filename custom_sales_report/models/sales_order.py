from odoo import models, fields, api



class SaleOrder(models.Model):
    _inherit = 'sale.order'

class ResCompany(models.Model):
    _inherit='res.company'

    bankname=fields.Char(string="Bank Name")
    bank_account_number=fields.Char(string="Account Number")
    branch=fields.Char(string="Branch")
    ifsc=fields.Char(string="IFSC")

    def _get_report_values(self, docids, data=None):
        orders = self.env['sale.order'].browse(docids)
        companies = self.env['res.company'].search([])  # Fetch all companies, adjust the search domain as needed
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': orders,
            'companies': companies,  # Pass companies data to the template
        }