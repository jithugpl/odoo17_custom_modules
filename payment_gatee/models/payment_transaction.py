# -*- coding: utf-8 -*-
# Copyright (c) 2024-Present Gate-E. (<https://www.Gate-E.com>)

import logging
import json
import requests
import http.client
import pprint
import requests

from werkzeug import urls

from odoo import _, api, fields, models
from odoo.addons.payment.models.payment_provider import ValidationError
from odoo.addons.payment_gatee.controllers.main import GateeController
from odoo.tools.float_utils import float_compare
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    gatee_payment_id = fields.Char('Gate-e Payment ID')

    def _get_request_data(self, processing_values):
        order_history = []
        items = []

        base_url = self.provider_id.get_base_url()
        _logger.info(" base_url= %s", base_url)

        ### Payment Details  ###
        country_id = self.partner_country_id
        for c in country_id:
            country = c.name
        currency_id = self.currency_id
        for c in currency_id:
            currency_code = c.name

        ref_name = processing_values.get('reference').split('-')[0]
        sale_order = request.env['sale.order'].sudo().search([('name', '=', ref_name)])

        if sale_order:
            if self.amount == sale_order.amount_total:
                amount = sale_order.amount_untaxed
                tax_amount = sale_order.amount_tax
            else:
                amount = self.amount
                tax_amount = 0

            # Sale order lines
            for line in sale_order.order_line:
                items.append({
                    "title": line.name,
                    "amount": line.price_unit,
                    "currency": currency_code,
                    "quantity": line.product_uom_qty,
                    "category": line.product_id.categ_id.name
                })

        # Count confirmed sales orders for the customer
        customers_orders_count = request.env['sale.order'].sudo().search_count([
            ('partner_id', '=', self.partner_id.id),
            ('state', 'in', ('sale', 'done'))
        ])

        # Customer details
        customer_data = {
            "name": self.partner_id.name,
            "email": self.partner_id.email,
            "register_date": self.partner_id.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            "mobile": self.partner_id.mobile.replace('+', '') if self.partner_id.mobile else False,
            "loyalty_level": customers_orders_count
        }

        # Fetch last 5 orders of the customer
        customer_orders = request.env['sale.order'].sudo().search([
            ('partner_id', '=', self.partner_id.id),
            ('state', 'in', ('sale', 'done'))
        ], order="date_order desc", limit=5)

        for order in customer_orders:
            order_history.append({
                "date": order.date_order.strftime('%Y-%m-%d %H:%M:%S'),
                "amount": order.amount_total,
                "currency": order.currency_id.name,
                "status": order.invoice_status,
            })

        post_json = {
            "items": items,
            "customer": customer_data,
            "order_history": order_history
        }

        data = {
            'unique_id': self.provider_id.gatee_unique_id,  # required
            'api_type': self.provider_id.gatee_api_type,  # required
            'amount': amount,  # required
            'tax_amount': tax_amount,
            'ref_code': processing_values.get('reference'),
            'currency_code': currency_code,
            'action': 'background',
            'callback_url': urls.url_join(base_url, GateeController._callback_url),
            'show_callback': self.provider_id.gatee_show_callback,
            'field1': base_url,
            'field2': 'Odoo V16 - Gatee_api_v04_2_1',
            'field3': processing_values.get('reference'),
            'name': self.partner_name,
            'email': self.partner_email,
            'mobile': self.partner_phone.replace('+', ''),
            'city': self.partner_city,
            'address': self.partner_address,
            'country': country,
            'locale': self.provider_id.gatee_locale,
            'user_code': 'uc-user' + str(self.create_uid.id),
            'card_save': self.provider_id.gatee_card_save,
            'card_list': self.provider_id.gatee_card_list,
            'email_send': self.provider_id.gatee_email_send,
            'sms_send': self.provider_id.gatee_sms_send,
            'post_json': post_json
        }

        if request.env.user.id != request.env.ref('base.public_user').id:
            data['user_code'] = 'uc-user' + str(request.env.user.id)

        data['description'] = "reference code id = " + format(data['ref_code']) + " || amount = " + format(
            data['amount']) + " " + format(data['currency_code']) + " || user name = " + format(data['name'])

        hash = self.provider_id.gatee_hash
        calculated_hash = self.provider_id.calculateHash(hash, data)
        data['calculated_hash'] = calculated_hash

        return data

    def _get_specific_rendering_values(self, processing_values):
        # this function will called by payment.transaction module and check provider if it equal to payment gateway or not
        _logger.info("Entering _get_specific_rendering_values with processing_values %s",
                     pprint.pformat(processing_values))

        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_id.code != 'gatee':
            return res

        request_data = self._get_request_data(processing_values)

        print("post_json", request_data['post_json'])

        payment_link_data = self.provider_id._gatee_make_request(data=request_data)

        if payment_link_data and payment_link_data['payment_id']:
            self.gatee_payment_id = payment_link_data['payment_id']

        print("payment_link_data", payment_link_data)

        # Extract the payment URL and embed it in the redirect form.
        rendering_values = {
            'api_url': payment_link_data['payment_url'],
        }
        return rendering_values

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on Gate-e data.

        :param str provider_code: The code of the provider that handled the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction if found.
        :rtype: recordset of `payment.transaction`
        :raise ValidationError: If inconsistent data were received.
        :raise ValidationError: If the data match no transaction.
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'gatee' or len(tx) == 1:
            return tx

        print("notification_data", notification_data)

        transaction_ref = self.search(
            [('gatee_payment_id', '=', notification_data['payment_id']), ('provider_code', '=', 'gatee')])

        if not transaction_ref:
            raise ValidationError(
                "Gate-e: " + _("No transaction found matching reference %s.", transaction_ref)
            )
        return transaction_ref

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on Gate-e data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data were received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'gatee':
            return

        # Process the verified notification data.

        self.provider_reference = notification_data['payment_id']
        gatee_hash = self.provider_id.gatee_hash
        gatee_unique_id = self.provider_id.gatee_unique_id

        gatee_url = self.provider_id._get_gatee_urls()
        payment_url = format(gatee_url) + "api/getpayment.php?unique_id=" + format(
            gatee_unique_id) + "&payment_id=" + format(notification_data['payment_id']) + "&hash=" + format(gatee_hash)

        headers = {
            "Content-Type": "multipart/form-data",
        }
        print("getpayment payment_url respppppppp", payment_url)
        response = requests.get(payment_url, headers=headers, timeout=20)
        resp = response.json()

        print("getpayment respp", response.json())

        _logger.info('url = %s', pprint.pformat(payment_url))

        payment_status = resp.get('status')
        validated = resp['validated']
        if payment_status == 'completed' and validated:
            self._set_done()
        elif payment_status == 'uncompleted' or not validated:
            # self._set_canceled()
            self._set_canceled(_(
                "An error occurred during the processing of your payment (status %s). ", payment_status
            ))
        else:
            _logger.warning(
                "Received data with invalid payment status (%s) for transaction with reference %s.",
                payment_status, self.reference
            )
            self._set_error("Gate-e: " + _("Unknown payment status: %s", payment_status))
