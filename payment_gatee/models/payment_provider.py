# -*- coding: utf-8 -*-
# Copyright (c) 2024-Present Gate-E. (<https://www.Gate-E.com>)

import hashlib
import logging
import pprint
import requests

from odoo import api, fields, models, _
from collections import OrderedDict

from odoo.exceptions import ValidationError
from odoo.addons.payment_gatee import const

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    # add fields to invoicing payment gateway settings
    code = fields.Selection(selection_add=[('gatee', 'Gatee')], ondelete={'gatee': 'set default'})
    gatee_unique_id = fields.Char(string='Unique ID', required_if_provider='gatee', groups='base.group_user',
                                  required=True)
    gatee_hash = fields.Char(string='Hash', required_if_provider='gatee', groups='base.group_user', required=True)
    gatee_api_type = fields.Selection([('1', 'Use API through customer registration'),
                                       ('2', 'Use API without customer registration'),
                                       ('3', 'Use API through customer registration & customer information only'),
                                       ('4', 'Use API though customer login only')], ondelete={'1': 'set default'},
                                      string='API Type', required_if_provider='gatee', groups='base.group_user')
    gatee_show_callback = fields.Selection([('0', 'Don\'t show callback'), ('1', 'Show callback')],
                                           ondelete={'0': 'set default'}, string='Show Callback',
                                           required_if_provider='gatee', groups='base.group_user')
    gatee_card_save = fields.Selection([('checked', 'save card option is checked by default'),
                                        ('unchecked', 'save card option is unchecked by default'),
                                        ('force', 'force the customer to save the card'),
                                        ('disable', 'disable the save card option')],
                                       ondelete={'checked': 'set default'}, string='Card Save (if feature enabled)',
                                       required_if_provider='gatee', groups='base.group_user')
    gatee_card_list = fields.Selection(
        [('0', 'Don\'t show for customer his card list'), ('1', 'Show for customer his card list')],
        ondelete={'1': 'set default'}, string='Card List (if feature enabled)', required_if_provider='gatee',
        groups='base.group_user')
    gatee_locale = fields.Selection([('en', 'English'), ('ar', 'Arabic')], ondelete={'en': 'set default'},
                                    string='Language', required_if_provider='gatee', groups='base.group_user')
    gatee_debug = fields.Selection([('disable', 'Disable debug'), ('enable', 'Enable debug')],
                                   ondelete={'disable': 'set default'}, string='Debug mode',
                                   required_if_provider='gatee', groups='base.group_user')

    gatee_api_nodes = fields.Selection([('gate-e.com', 'api.gate-e.com'),
                                        ('gate-e.net', 'api.gate-e.net'),
                                        ('gate-e.co', 'api.gate-e.co')],
                                       string='API Nodes',
                                       required_if_provider='gatee', groups='base.group_user', default='gate-e.com')

    gatee_email_send = fields.Selection([('0', 'Do not send'),
                                        ('1', 'Send to client only'),
                                        ('2', 'Send to merchant only'),
                                        ('3', 'Send to both (merchant & client)')],
                                       string='Send Email',
                                       required_if_provider='gatee', groups='base.group_user', default='0')

    gatee_sms_send = fields.Selection([('0', 'Do not send'),
                                        ('1', 'Send to client only'),
                                        ('2', 'Send to merchant only'),
                                        ('3', 'Send to both (merchant & client)')],
                                       string='Send SMS',
                                       required_if_provider='gatee', groups='base.group_user', default='0')

    @api.model
    def _get_compatible_providers(self, *args, is_validation=False, **kwargs):
        providers = super()._get_compatible_providers(*args, is_validation=is_validation, **kwargs)
        if is_validation:
            providers = providers.filtered(lambda p: p.code != 'gatee')

        return providers

    def _get_gatee_urls(self):
        _logger.info('Entering _get_gatee_urls', pprint.pformat(self.gatee_api_nodes))
        """ Gate-e URLS it will return first url if user select in gateway setting allow and will return second url if user select test"""
        if self.state == 'enabled':
            return 'https://www.' + self.gatee_api_nodes + '/'
        return 'https://www.test.gate-e.com/'

    def _gatee_make_request(self, data=None):
        self.ensure_one()
        print("_gatee_make_request data", data)
        parameters = ""
        for key, value in data.items():
            parameters += str(str(str(key) + "=") + str(value)) + "&"
        _logger.info("data= %s", parameters)
        gatee_url = self._get_gatee_urls()

        payment_url = format(gatee_url) + "api/process.php?" + format(parameters)
        _logger.info(" process payment_url = %s", payment_url)
        headers = {
            "Content-Type": "multipart/form-data",
        }
        response = requests.post(payment_url, headers=headers, timeout=20)
        print("response", response)
        print("response json", response.json())

        try:
            response = response.json()
            print("response.get('status') ", response.get('status') )
            if response.get('status') == 'success':
                return response
            else:
                raise ValidationError(_("We having some issues, contact us for the support!"))
        except:
            raise ValidationError(_("We having some issues, contact us for the support!  - Error: %s", response.get('error')))

    @api.model
    def create(self, vals):
        providers = super(PaymentProvider, self).create(vals)
        for provider in providers:
            if provider.code == 'gatee':
                provider.journal_id = self.env.ref('payment_gatee.gatee_account_journal').id
        return providers

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'gatee':
            return default_codes
        return const.DEFAULT_PAYMENT_METHODS_CODES

    # def _get_default_payment_method_id(self, code):
    #     self.ensure_one()
    #     if code != 'gatee':
    #         return super()._get_default_payment_method_id()
    #     return self.env.ref('payment_gatee.payment_method_gatee').id

    def calculateHash(self, hash, data):
        data = OrderedDict(sorted(data.items()))
        data1 = ''
        for key, value in data.items():
            if key != 'data' and key != 'note' and key != 'post_json':
                data1 += str(str(str(key) + "=") + str(value)) + ";"
        data1 += str("hash=" + str(hash)) + ";"
        calculated_hash = hashlib.md5(data1.encode('utf-8')).hexdigest()
        return calculated_hash
