from odoo import models, fields, api
from odoo.addons.payment.models.payment_acquirer import ValidationError
import razorpay
import logging

_logger = logging.getLogger(__name__)

class PaymentAcquirerRazorpay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('razorpay', 'Razorpay')], ondelete={'razorpay': 'set default'})
    razorpay_key_id = fields.Char(string="Razorpay Key ID", required_if_provider='razorpay')
    razorpay_key_secret = fields.Char(string="Razorpay Key Secret", required_if_provider='razorpay')

    def _get_razorpay_client(self):
        self.ensure_one()
        return razorpay.Client(auth=(self.razorpay_key_id, self.razorpay_key_secret))

class PaymentTransactionRazorpay(models.Model):
    _inherit = 'payment.transaction'

    def _razorpay_form_get_tx_from_data(self, data):
        tx = self.search([('reference', '=', data.get('merchant_order_id'))])
        if not tx:
            raise ValidationError("Transaction not found.")
        return tx

    def _razorpay_form_validate(self, data):
        self.ensure_one()
        acquirer = self.acquirer_id
        client = acquirer._get_razorpay_client()
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })
            self._set_transaction_done()
            self.write({'acquirer_reference': data.get('razorpay_payment_id')})
            return True
        except Exception as e:
            _logger.error(f"Razorpay signature verification failed: {e}")
            self._set_transaction_error(str(e))
            return False