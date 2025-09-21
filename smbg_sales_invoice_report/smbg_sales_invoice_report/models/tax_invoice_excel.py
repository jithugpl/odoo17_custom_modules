from odoo import models, fields
import base64
from io import BytesIO
import xlsxwriter


class AccountMove(models.Model):
    _inherit = 'account.move'

    file_out = fields.Binary('Excel File')
    file_out_filename = fields.Char('Excel File Name')

    def print_report_excel(self):
        file_io = BytesIO()
        workbook = xlsxwriter.Workbook(file_io)
        sheet = workbook.add_worksheet()

        data={
            'company_name':self.company_id.name,
            'com_street':self.company_id.street,
            'com_street2':self.company_id.street2,
            'com_city':self.company_id.city,
            'com_state':self.company_id.state_id.name,
            'com_zip':self.company_id.zip,
            'com_country':self.company_id.country_id.name,
            'com_phone':self.company_id.phone,
            'com_email':self.company_id.email,
            'invoice_no':self.name,
            'invoice_date':self.invoice_date



        }
        row=8
        col=0

        size=workbook.add_format({'bold':True,'font_size':18,'font_color':'#FF66CC','align':'center','valign':'vcenter'})
        com_address=workbook.add_format({'font_size':10,  'indent': 5})
        sheet.write(row-4,col+1,'Invoice No:')
        sheet.write(row-4,col+3,''+data['invoice_no'])
        sheet.write(row-4,col+7,'Invoice Date:')
        sheet.write(row-4,col+9,''+data['invoice_no'])


        sheet.merge_range('A3:M3','Tax Invoice',size)
        sheet.merge_range('A2:M2',
                          str(data['company_name']) + '\n' + str(data['com_street']) + '\n' + str(
                              data['com_street2']) + '\n' + str(data[
                                                                    'com_city']) + ' ' + str(
                              data['com_state']) + ' ' + str(
                              data['com_zip']) + '\n' + str(
                              data['com_country']) + '\n' +
                          str(data['com_phone']) + '\n' + str(data['com_email']), com_address)

        sheet.set_row(1,80)
        sheet.set_row(2,35)
        sheet.set_row(row-4,20)
        sheet.set_row(row-3,20)
        sheet.set_column('B:B',16)
        sheet.set_column('D:D', 16)
        sheet.set_column('H:H', 16)
        sheet.set_column('J:J', 16)

        workbook.close()
        file_out = base64.b64encode(file_io.getvalue())
        file_io.close()

        self.file_out = file_out
        self.file_out_filename = 'tax invoice.xlsx'

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=account.move&id=%s&field=file_out&download=true&filename=%s' % (
                self.id, self.file_out_filename),
            'target': 'self',
        }
