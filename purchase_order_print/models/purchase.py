from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PurchaseOrderPrintReport(models.AbstractModel):
    _name = 'report.purchase_order_print.report_purchase_order'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'purchase_order_print.report_purchase_order')
        obj = self.env[report.model].browse(docids)

        # Iterate over each order
        for record in obj:
            # Iterate over each order line
            for line in record.order_line:
                if len(line.taxes_id) > 1:
                    # Raise error if more than one tax is found on a product line
                    raise ValidationError(_('Print can be taken only for orders with a single tax per product line.'))

        # If no validation error, return the report values
        return {
            'docs': obj,
        }