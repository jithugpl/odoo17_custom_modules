from datetime import datetime
import io
from odoo import models, fields
import xlsxwriter
from io import BytesIO
import base64

class SaleOrderExcel(models.Model):
    _inherit = 'account.move'

    file_out = fields.Binary('Excel File')
    file_out_filename = fields.Char('Excel File Name')

    def print_report_excel(self):
        file_io = BytesIO()
        workbook = xlsxwriter.Workbook(file_io)
        worksheet = workbook.add_worksheet()

        # Define formats
        heading_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9EAD3',
            'font_color': '#000000',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'size': 12
        })

        data_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'text_wrap': True
        })

        total_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'
        })

        # Set column widths
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 35)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 25)

        # # Fetch and insert company logo
        # if self.company_id.logo:
        #     logo_data = base64.b64decode(self.company_id.logo)
        #     logo_io = BytesIO(logo_data)
        #     worksheet.insert_image('D1', 'company_logo.png', {'image_data': logo_io, 'x_offset': 10, 'y_offset': 15})

        company_details = (
            f"{self.company_id.name}\n"
            f"{self.company_id.street or ''}\n"
            f"{self.company_id.street2 or ''}\n"
            f"{self.company_id.city or ''}\n"
            f"{self.company_id.email or ''}\n"
            f"{self.company_id.website or ''}\n"
            f"{self.company_id.phone or ''}"
        )
        worksheet.merge_range('A1:C10', company_details, data_format)
        worksheet.merge_range('A1:J10','',)
        worksheet.merge_range('C12:H14', '', )
        worksheet.merge_range('A26:J26', '', )

        # # Define the formats for heading and data
        # heading_format = workbook.add_format({'align': 'left'})
        # data_format = workbook.add_format({'align': 'left'})

        # Invoice details
        worksheet.merge_range('A11:J11', 'TAX INVOICE', heading_format)
        worksheet.write('A12:B12', 'Invoice No', heading_format)
        worksheet.write('B12', self.name or '', data_format)
        worksheet.write('I12', 'Invoice Date', heading_format)
        worksheet.write('J12', self.invoice_date.strftime('%d/%m/%Y') if self.invoice_date else 'N/A', data_format)
        worksheet.write('A13', 'Payment Terms', heading_format)
        worksheet.write('B13', self.invoice_payment_term_id.name or '', data_format)
        worksheet.write('I13', 'Due Date', heading_format)
        due_date = getattr(self, 'invoice_date_due', self.invoice_date)  # Use self.invoice_date_due if available, fallback to self.invoice_date
        worksheet.write('J13', due_date.strftime('%d/%m/%Y') if due_date else 'N/A', data_format)
        worksheet.write('A14', 'Currency', heading_format)
        worksheet.write('B14', self.currency_id.name or '', data_format)

        # Receiver details table
        worksheet.merge_range('A15:D15', 'Details of Receiver (Billed To)', heading_format)
        receiver_details = f"{self.partner_id.name or ''}\n{self.partner_id.street or ''}\n{self.partner_id.city or ''}, {self.partner_id.state_id.name or ''} {self.partner_id.zip or ''}\n{self.partner_id.country_id.name or ''}\nPhone: {self.partner_id.phone or ''}\nEmail: {self.partner_id.email or ''}"
        worksheet.merge_range('A16:D21', receiver_details, data_format)
        #
        # Consignee details table (on the right side)
        worksheet.merge_range('E15:J15', 'Details of Consignee (Shipped To)', heading_format)
        consignee_details = f"{self.partner_shipping_id.name or ''}\n{self.partner_shipping_id.street or ''}\n{self.partner_shipping_id.city or ''}, {self.partner_shipping_id.state_id.name or ''} {self.partner_shipping_id.zip or ''}\n{self.partner_shipping_id.country_id.name or ''}\nPhone: {self.partner_shipping_id.phone or ''}\nEmail: {self.partner_shipping_id.email or ''}"
        worksheet.merge_range('E16:J21', consignee_details, data_format)
        #
        # Define the range for each heading to stretch across columns A to J
        worksheet.merge_range('A22:B22', 'Sales Rep', heading_format)
        worksheet.merge_range('A23:B25', self.invoice_user_id.name)
        worksheet.merge_range('C22:D22', 'Customer ID', heading_format)
        worksheet.merge_range('C23:D25', self.partner_id.customer_id)
        worksheet.merge_range('E22:F22', 'Order No', heading_format)
        worksheet.merge_range('E23:F25', self.name)
        worksheet.merge_range('G22:H22', 'Reference', heading_format)
        worksheet.merge_range('G23:H25', self.ref)
        worksheet.merge_range('I22:J22', 'Transported By', heading_format)
        transported_by = getattr(self, 'transported_by', 'N/A')
        worksheet.merge_range('I23:J25', transported_by)
        # Table headers for line items
        row = 26
        worksheet.write(row, 0, '#', heading_format)
        worksheet.write(row, 1, 'Item', heading_format)
        worksheet.write(row, 2, 'Barcode', heading_format)
        worksheet.write(row, 3, 'Qty', heading_format)
        worksheet.write(row, 4, 'UOM', heading_format)
        worksheet.write(row, 5, 'Rate', heading_format)
        worksheet.write(row, 6, 'Disc', heading_format)
        worksheet.write(row, 7, 'Taxable Amount', heading_format)
        worksheet.write(row, 8, 'VAT %', heading_format)
        worksheet.write(row, 9, 'Total Amount (Incl. VAT)', heading_format)

        # Invoice line items
        row += 1
        item_no = 1
        for line in self.invoice_line_ids:
            worksheet.write(row, 0, item_no, data_format)
            worksheet.write(row, 1, line.product_id.name, data_format)
            worksheet.write(row, 2, line.product_id.barcode, data_format)
            worksheet.write(row, 3, line.quantity, data_format)
            worksheet.write(row, 4, line.product_uom_id.name, data_format)
            worksheet.write(row, 5, line.price_unit, data_format)
            worksheet.write(row, 6, line.discount, data_format)
            worksheet.write(row, 7, line.price_subtotal, data_format)
            worksheet.write(row, 8, sum(tax.amount for tax in line.tax_ids), data_format)
            worksheet.write(row, 9, line.price_total, data_format)
            row += 1
            item_no += 1

        # Total amounts
        row += 1
        worksheet.write(row, 8, 'Gross Total AED:', total_format)
        worksheet.write(row, 9, self.amount_total, data_format)

        row += 1
        worksheet.write(row, 8, 'Total Discount:', total_format)
        worksheet.write(row, 9, sum(line.price_unit * line.quantity * line.discount / 100 for line in self.invoice_line_ids), data_format)

        row += 1
        worksheet.write(row, 8, 'Sub Total:', total_format)
        worksheet.write(row, 9, self.amount_untaxed, data_format)

        row += 1
        worksheet.write(row, 8, 'Total VAT:', total_format)
        worksheet.write(row, 9, self.amount_tax, data_format)

        row += 1
        worksheet.write(row, 8, 'Total AED:', total_format)
        worksheet.write(row, 9, self.amount_total, data_format)

        # Bank details
        row -= 4
        worksheet.write(row, 0, 'Bank', heading_format)
        worksheet.write(row, 1, 'Emirates NBD', data_format)

        worksheet.write(row + 1, 0, 'A/c No', heading_format)
        worksheet.write(row + 1, 1, '101518452001', data_format)

        worksheet.write(row + 2, 0, 'IBAN', heading_format)
        worksheet.write(row + 2, 1, 'AE85026000101518452001', data_format)

        worksheet.write(row + 3, 0, 'SWIFT', heading_format)
        worksheet.write(row + 3, 1, '', data_format)  # Add SWIFT code if available

        worksheet.write(row + 4, 0, 'Beneficiary', heading_format)
        worksheet.write(row + 4, 1, 'SM Bros Group General Trading LLC', data_format)

        # Receiver details, signature, and mobile number
        row += 6
        worksheet.merge_range(row, 0, row, 4, 'Receiver:', data_format)
        worksheet.merge_range(row + 1, 0, row + 1, 4, 'Signature:', data_format)
        worksheet.merge_range(row + 1, 5, row + 1, 9, 'Mob:', data_format)
        #
        # Footer terms and conditions
        terms = "Terms and Conditions: Once goods delivery is confirmed, customer agrees to pay the total invoice amount without additional deductions and within the agreed payment terms. For any discrepancy noted in the invoice, the company should be informed within 48 hours from the date of receipt. No further requests will be accepted later than 48 hours of delivery."
        worksheet.merge_range(row + 5, 0, row + 7, 9, terms, data_format)




        workbook.close()
        file_out = base64.b64encode(file_io.getvalue())
        file_io.close()

        self.file_out = file_out
        self.file_out_filename = 'invoice_report.xlsx'

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=account.move&id=%s&field=file_out&download=true&filename=%s' % (
                self.id, self.file_out_filename),
            'target': 'self',
        }
