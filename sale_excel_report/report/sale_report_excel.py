from datetime import datetime, date
import io
from odoo import models, fields, api
import xlsxwriter
from io import BytesIO
import base64

class SaleOrderExcel(models.Model):
    _inherit = 'sale.order'

    file_out = fields.Binary('Excel File')
    file_out_filename = fields.Char('Excel File Name')

    def print_report_excel(self):
        file_io = BytesIO()
        workbook = xlsxwriter.Workbook(file_io)
        worksheet = workbook.add_worksheet()

        heading_format = workbook.add_format({
            'bold': True,
            # 'bg_color': '#FFCC00',
            'font_color': '#000000',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'size': 12
        })

        sub_heading_format = workbook.add_format({
            'bold': True,
            # 'bg_color': '#D3D3D3',
            'font_color': '#000000',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'size': 10
        })

        data_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 50)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 50)

        # Invoice header details
        worksheet.write(0, 0, 'Invoice No', heading_format)
        worksheet.write(0, 1, self.name, data_format)

        worksheet.write(1, 0, 'Invoice Date', heading_format)
        worksheet.write(1, 1, self.date_order.strftime('%d/%m/%Y'), data_format)

        worksheet.write(2, 0, 'Due Date', heading_format)
        worksheet.write(2, 1, self.date_order.strftime('%d/%m/%Y'), data_format)

        # Receiver details table
        worksheet.merge_range('A4:B4', 'Details of Receiver (Billed To)', heading_format)
        receiver_details = f"Name: {self.partner_id.name or ''}\nAddress: {self.partner_id.street or ''}\n{self.partner_id.city or ''}, {self.partner_id.state_id.name or ''} {self.partner_id.zip or ''}\n{self.partner_id.country_id.name or ''}\nPhone: {self.partner_id.phone or ''}\nEmail: {self.partner_id.email or ''}"
        worksheet.merge_range('A5:B9', receiver_details, data_format)

        # Consignee details table (on the right side)
        worksheet.merge_range('D4:E4', 'Details of Consignee (Shipped To)', heading_format)
        consignee_details = f"Name: {self.partner_shipping_id.name or ''}\nAddress: {self.partner_shipping_id.street or ''}\n{self.partner_shipping_id.city or ''}, {self.partner_shipping_id.state_id.name or ''} {self.partner_shipping_id.zip or ''}\n{self.partner_shipping_id.country_id.name or ''}\nPhone: {self.partner_shipping_id.phone or ''}\nEmail: {self.partner_shipping_id.email or ''}"
        worksheet.merge_range('D5:E9', consignee_details, data_format)

        # Table headers for line items
        row = 10
        worksheet.write(row, 0, 'Item', heading_format)
        worksheet.write(row, 1, 'Qty', heading_format)
        worksheet.write(row, 2, 'UOM', heading_format)
        worksheet.write(row, 3, 'Rate', heading_format)
        worksheet.write(row, 4, 'Disc', heading_format)
        worksheet.write(row, 5, 'Taxable Amount', heading_format)
        worksheet.write(row, 6, 'VAT %', heading_format)
        worksheet.write(row, 7, 'Total Amount (Incl. VAT)', heading_format)

        # Invoice line items
        row += 1
        for line in self.order_line:
            worksheet.write(row, 0, line.product_id.default_code, data_format)
            worksheet.write(row, 1, line.product_uom_qty, data_format)
            worksheet.write(row, 2, line.product_uom.name, data_format)
            worksheet.write(row, 3, line.price_unit, data_format)
            worksheet.write(row, 4, line.discount, data_format)
            worksheet.write(row, 5, line.price_subtotal, data_format)
            worksheet.write(row, 6, sum(tax.amount for tax in line.tax_id), data_format)
            worksheet.write(row, 7, line.price_total, data_format)
            row += 1

        # Total amounts
        worksheet.write(row, 0, 'Total Amount:', heading_format)
        worksheet.write(row, 1, self.amount_total, data_format)

        worksheet.write(row + 1, 0, 'Total Discount:', heading_format)
        worksheet.write(row + 1, 1, sum(line.price_unit * line.product_uom_qty * line.discount / 100 for line in self.order_line), data_format)

        worksheet.write(row + 2, 0, 'Sub Total:', heading_format)
        worksheet.write(row + 2, 1, self.amount_untaxed, data_format)

        worksheet.write(row + 3, 0, 'Total VAT:', heading_format)
        worksheet.write(row + 3, 1, self.amount_tax, data_format)

        worksheet.write(row + 4, 0, 'Total AED:', heading_format)
        worksheet.write(row + 4, 1, self.amount_total, data_format)

        workbook.close()
        file_out = base64.b64encode(file_io.getvalue())
        file_io.close()

        self.file_out = file_out
        self.file_out_filename = 'sale_order_report.xlsx'


        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=sale.order&id=%s&field=file_out&download=true&filename=%s' % (
            self.id, self.file_out_filename),
            'target': 'self',
        }