# -*- coding: utf-8 -*-
# Copyright (c) 2024-Present Gate-E. (<https://www.Gate-E.com>)

from odoo import api, models


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['gatee'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res
