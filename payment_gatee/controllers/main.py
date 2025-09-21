# -*- coding: utf-8 -*-
# Copyright (c) 2024-Present Gate-E. (<https://www.Gate-E.com>)

import logging
import pprint
import requests

from werkzeug import urls

from odoo import http
from odoo.http import request
from odoo.addons.payment.models.payment_provider import PaymentProvider

_logger = logging.getLogger(__name__)


class GateeController(http.Controller):
    _callback_url = '/payment/gatee/callback'

    @http.route(_callback_url, type='http', auth='public', csrf=False, save_session=False)
    def gatee_callback(self, **data):
        """ Process the notification data sent by Gate-e after redirection from checkout.

        :param dict data: The notification data.
        """
        _logger.info("Handling redirection from Gate-e with data:\n%s", pprint.pformat(data))

        # Handle the notification data.
        if data.get('status') != 'completed':
            request.env['payment.transaction'].sudo()._handle_notification_data('gatee', data)
        else:  # The customer cancelled the payment by clicking on the close button.
            pass  # Don't try to process this case because the transaction id was not provided.

        # Redirect the user to the status page.
        return request.redirect('/payment/status')
