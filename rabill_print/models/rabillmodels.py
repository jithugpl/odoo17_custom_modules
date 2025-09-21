
from odoo import models, fields, api, _
from num2words import num2words

class RunningBill(models.Model):
    _inherit = 'running.bill'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def amount_to_words(self,amount):
        return num2words(amount, lang='en').title()
class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bank_id = fields.Many2one('res.bank', string='Bank')
    acc_number = fields.Char(string='Account Number')
    # swift_code = fields.Char(string='Swift Code')
    street = fields.Char(string='Address')  # If address is stored in the bank record


class ResCompany(models.Model):
    _inherit='res.company'

    bankname=fields.Char(string="Bank Name")
    bank_account_number=fields.Char(string="Account Number")
    branch=fields.Char(string="Branch")
    ifsc=fields.Char(string="IFSC")

    def _get_report_values(self, docids, data=None):
        orders = self.env['running.bill'].browse(docids)
        companies = self.env['res.company'].search([])  # Fetch all companies, adjust the search domain as needed
        return {
            'doc_ids': docids,
            'doc_model': 'running.bill',
            'docs': orders,
            'companies': companies,  # Pass companies data to the template
        }
